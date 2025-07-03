import os
from pathlib import Path
from unittest.mock import patch

import pytest

import pandas as pd

from fastapi import HTTPException
from app.services.excel_import import parse_excel, df_to_pdf


def test_parse_excel(tmp_path):
    df = pd.DataFrame([
        {
            "User ID": 1,
            "Data": "2023-01-01",
            "Inizio1": "08:00:00",
            "Fine1": "12:00:00",
            "Tipo": "NORMALE",
            "Note": "n1",
        },
        {
            "User ID": "2",
            "Data": "2023-01-02",
            "Inizio1": "09:00:00",
            "Fine1": "13:00:00",
            "Inizio2": "14:00:00",
            "Fine2": "18:00:00",
            "Inizio3": "19:00:00",
            "Fine3": "21:00:00",
            "Tipo": "EXTRA",
            "Note": "n2",
        },
    ])
    xls = tmp_path / "sample.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls), None)

    assert rows == [
        {
            "user_id": "1",
            "giorno": "2023-01-01",
            "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
            "tipo": "NORMALE",
            "note": "n1",
        },
        {
            "user_id": "2",
            "giorno": "2023-01-02",
            "slot1": {"inizio": "09:00:00", "fine": "13:00:00"},
            "slot2": {"inizio": "14:00:00", "fine": "18:00:00"},
            "slot3": {"inizio": "19:00:00", "fine": "21:00:00"},
            "tipo": "EXTRA",
            "note": "n2",
        },
    ]


def test_parse_excel_straordinario(tmp_path):
    df = pd.DataFrame([
        {
            "User ID": 3,
            "Data": "2023-02-01",
            "Inizio1": "08:00:00",
            "Fine1": "12:00:00",
            "Straordinario inizio": "20:00:00",
            "Straordinario fine": "22:00:00",
        }
    ])
    xls = tmp_path / "straordinario.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls), None)

    assert rows == [
        {
            "user_id": "3",
            "giorno": "2023-02-01",
            "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
            "slot3": {"inizio": "20:00:00", "fine": "22:00:00"},
            "tipo": "NORMALE",
            "note": "",
        }
    ]


def test_parse_excel_with_db(tmp_path):
    """Ensure parsing works when resolving user names via a DB session."""
    from app.database import SessionLocal
    from app.models.user import User

    db = SessionLocal()
    user = User(id="u1", email="a@example.com", nome="Agent X", hashed_password="x")
    db.add(user)
    db.commit()

    df = pd.DataFrame([
        {
            "Agente": "Agent X",
            "Data": "2023-01-03",
            "Inizio1": "07:00:00",
            "Fine1": "11:00:00",
        }
    ])
    xls = tmp_path / "agent.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls), db)

    assert rows == [
        {
            "user_id": "u1",
            "giorno": "2023-01-03",
            "slot1": {"inizio": "07:00:00", "fine": "11:00:00"},
            "tipo": "NORMALE",
            "note": "",
        }
    ]

    db.close()


def test_parse_excel_missing_column(tmp_path):
    """An HTTPException is raised when required columns are missing."""
    from app.database import SessionLocal

    db = SessionLocal()

    df = pd.DataFrame([
        {
            "Agente": "Agent X",
            "Data": "2023-01-04",
            "Inizio1": "07:00:00",
            # "Fine1" column intentionally omitted
        }
    ])
    xls = tmp_path / "missing.xlsx"
    df.to_excel(xls, index=False)

    with pytest.raises(HTTPException) as exc:
        parse_excel(str(xls), db)

    assert exc.value.status_code == 400
    assert "Missing columns" in exc.value.detail

    db.close()


def test_parse_excel_agente_without_db(tmp_path):
    """Parsing fails when only the Agente column is present and no DB session is provided."""

    df = pd.DataFrame([
        {
            "Agente": "Agent X",
            "Data": "2023-01-05",
            "Inizio1": "08:00:00",
            "Fine1": "12:00:00",
        }
    ])
    xls = tmp_path / "no_db.xlsx"
    df.to_excel(xls, index=False)

    with pytest.raises(HTTPException) as exc:
        parse_excel(str(xls), None)

    assert exc.value.status_code == 400
    assert "Database session required" in exc.value.detail


def test_parse_excel_unknown_user_id(tmp_path):
    """An HTTPException is raised for an unknown User ID when a DB session is provided."""
    from app.database import SessionLocal

    db = SessionLocal()

    df = pd.DataFrame([
        {
            "User ID": "missing",
            "Data": "2023-03-01",
            "Inizio1": "08:00:00",
            "Fine1": "12:00:00",
        }
    ])
    xls = tmp_path / "unknown_id.xlsx"
    df.to_excel(xls, index=False)

    with pytest.raises(HTTPException) as exc:
        parse_excel(str(xls), db)

    assert exc.value.status_code == 400
    assert "Unknown user ID" in exc.value.detail

    db.close()


def test_df_to_pdf_creates_files_and_cleanup(tmp_path):
    rows = [
        {
            "user_id": "1",
            "giorno": "2023-01-01",
            "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
            "tipo": "NORMALE",
            "note": "",
        }
    ]

    def fake_from_file(html_path, pdf_path):
        Path(pdf_path).write_bytes(b"%PDF-1.4 fake")
        return True

    with patch("app.services.excel_import.pdfkit.from_file", side_effect=fake_from_file):
        pdf_path, html_path = df_to_pdf(rows)

    assert os.path.exists(pdf_path)
    assert os.path.exists(html_path)

    os.remove(pdf_path)
    os.remove(html_path)

    assert not os.path.exists(pdf_path)
    assert not os.path.exists(html_path)


def test_df_to_pdf_missing_wkhtmltopdf(tmp_path):
    """An informative HTTPException is raised when wkhtmltopdf is missing."""
    rows = [
        {
            "user_id": "1",
            "giorno": "2023-01-01",
            "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
            "tipo": "NORMALE",
            "note": "",
        }
    ]

    def fake_from_file(html_path, pdf_path):
        raise OSError("No wkhtmltopdf executable found")

    with patch("app.services.excel_import.pdfkit.from_file", side_effect=fake_from_file):
        with pytest.raises(HTTPException) as exc:
            df_to_pdf(rows)

    assert exc.value.status_code == 500
    assert "wkhtmltopdf" in exc.value.detail
