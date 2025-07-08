import os
from pathlib import Path
from unittest.mock import patch

import pytest

import pandas as pd

from fastapi import HTTPException
from app.services.excel_import import parse_excel, df_to_pdf


def test_parse_excel(tmp_path):
    df = pd.DataFrame(
        [
            {
                "User ID": 1,
                "Giorno": "2023-01-01",
                "Inizio1": "08:00:00",
                "Fine1": "12:00:00",
                "Tipo": "NORMALE",
                "Note": "n1",
            },
            {
                "User ID": "2",
                "Giorno": "2023-01-02",
                "Inizio1": "09:00:00",
                "Fine1": "13:00:00",
                "Inizio2": "14:00:00",
                "Fine2": "18:00:00",
                "Inizio3": "19:00:00",
                "Fine3": "21:00:00",
                "Tipo": "EXTRA",
                "Note": "n2",
            },
        ]
    )
    xls = tmp_path / "sample.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls), None)

    assert rows == [
        {
            "user_id": "1",
            "giorno": "2023-01-01",
            "inizio_1": "08:00:00",
            "fine_1": "12:00:00",
            "tipo": "NORMALE",
            "note": "n1",
        },
        {
            "user_id": "2",
            "giorno": "2023-01-02",
            "inizio_1": "09:00:00",
            "fine_1": "13:00:00",
            "inizio_2": "14:00:00",
            "fine_2": "18:00:00",
            "inizio_3": "19:00:00",
            "fine_3": "21:00:00",
            "tipo": "EXTRA",
            "note": "n2",
        },
    ]


def test_parse_excel_straordinario(tmp_path):
    df = pd.DataFrame(
        [
            {
                "User ID": 3,
                "Giorno": "2023-02-01",
                "Inizio1": "08:00:00",
                "Fine1": "12:00:00",
                "Straordinario inizio": "20:00:00",
                "Straordinario fine": "22:00:00",
            }
        ]
    )
    xls = tmp_path / "straordinario.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls), None)

    assert rows == [
        {
            "user_id": "3",
            "giorno": "2023-02-01",
            "inizio_1": "08:00:00",
            "fine_1": "12:00:00",
            "inizio_3": "20:00:00",
            "fine_3": "22:00:00",
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

    df = pd.DataFrame(
        [
            {
                "Agente": "Agent X",
                "Giorno": "2023-01-03",
                "Inizio1": "07:00:00",
                "Fine1": "11:00:00",
            }
        ]
    )
    xls = tmp_path / "agent.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls), db)

    assert rows == [
        {
            "user_id": "u1",
            "giorno": "2023-01-03",
            "inizio_1": "07:00:00",
            "fine_1": "11:00:00",
            "tipo": "NORMALE",
            "note": "",
        }
    ]

    db.close()


def test_parse_excel_missing_column(tmp_path):
    """An HTTPException is raised when required columns are missing."""
    from app.database import SessionLocal

    db = SessionLocal()

    df = pd.DataFrame(
        [
            {
                "Agente": "Agent X",
                "Giorno": "2023-01-04",
                "Inizio1": "07:00:00",
                # "Fine1" column intentionally omitted
            }
        ]
    )
    xls = tmp_path / "missing.xlsx"
    df.to_excel(xls, index=False)

    with pytest.raises(HTTPException) as exc:
        parse_excel(str(xls), db)

    assert exc.value.status_code == 400
    assert "Missing columns" in exc.value.detail

    db.close()


def test_parse_excel_agente_without_db(tmp_path):
    """Parsing fails when only the Agente column is present and no DB session is provided."""

    df = pd.DataFrame(
        [
            {
                "Agente": "Agent X",
                "Giorno": "2023-01-05",
                "Inizio1": "08:00:00",
                "Fine1": "12:00:00",
            }
        ]
    )
    xls = tmp_path / "no_db.xlsx"
    df.to_excel(xls, index=False)

    with pytest.raises(HTTPException) as exc:
        parse_excel(str(xls), None)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Row 2: Database session required to resolve 'Agente'"


def test_parse_excel_empty_user_id(tmp_path):
    """Empty cells in the User ID column should result in a 400 error."""

    df = pd.DataFrame(
        [
            {
                "User ID": "",
                "Giorno": "2023-03-01",
                "Inizio1": "08:00:00",
                "Fine1": "12:00:00",
            }
        ]
    )
    xls = tmp_path / "empty_user.xlsx"
    df.to_excel(xls, index=False)

    with pytest.raises(HTTPException) as exc:
        parse_excel(str(xls), None)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Row 2: Missing user identifier"


def test_parse_excel_empty_agente(tmp_path):
    """Empty cells in the Agente column should result in a 400 error."""
    from app.database import SessionLocal

    db = SessionLocal()
    df = pd.DataFrame(
        [
            {
                "Agente": " ",
                "Giorno": "2023-03-02",
                "Inizio1": "08:00:00",
                "Fine1": "12:00:00",
            }
        ]
    )
    xls = tmp_path / "empty_agent.xlsx"
    df.to_excel(xls, index=False)

    with pytest.raises(HTTPException) as exc:
        parse_excel(str(xls), db)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Row 2: Missing user identifier"

    db.close()


def test_parse_excel_unknown_user_id(tmp_path):
    """An invalid User ID should raise an HTTPException when a DB session is supplied."""
    from app.database import SessionLocal

    db = SessionLocal()

    df = pd.DataFrame(
        [
            {
                "User ID": "missing",
                "Giorno": "2023-04-01",
                "Inizio1": "08:00:00",
                "Fine1": "12:00:00",
            }
        ]
    )
    xls = tmp_path / "unknown_id.xlsx"
    df.to_excel(xls, index=False)

    with pytest.raises(HTTPException) as exc:
        parse_excel(str(xls), db)

    assert exc.value.status_code == 400
    assert exc.value.detail == "Row 2: Unknown user ID: missing"

    db.close()


def test_parse_excel_day_off_missing_times(tmp_path):
    df = pd.DataFrame(
        [
            {
                "User ID": 1,
                "Giorno": "2024-01-01",
                "Inizio1": None,
                "Fine1": None,
                "Tipo": "FESTIVO",
            }
        ]
    )
    xls = tmp_path / "dayoff.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls), None)

    assert rows == [
        {
            "user_id": "1",
            "giorno": "2024-01-01",
            "inizio_1": None,
            "fine_1": None,
            "tipo": "FESTIVO",
            "note": "",
        }
    ]


def test_parse_excel_day_off_missing_times_recupero(tmp_path):
    """Day-off rows of type RECUPERO allow missing time values."""
    df = pd.DataFrame(
        [
            {
                "User ID": 2,
                "Giorno": "2024-01-02",
                "Inizio1": None,
                "Fine1": None,
                "Tipo": "RECUPERO",
            }
        ]
    )
    xls = tmp_path / "recupero.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls), None)

    assert rows == [
        {
            "user_id": "2",
            "giorno": "2024-01-02",
            "inizio_1": None,
            "fine_1": None,
            "tipo": "RECUPERO",
            "note": "",
        }
    ]


def test_parse_excel_strips_whitespace(tmp_path):
    """Leading/trailing spaces in time columns are ignored."""
    df = pd.DataFrame(
        [
            {
                "User ID": 4,
                "Giorno": "2024-01-02",
                "Inizio1": " 08:00",
                "Fine1": "12:00 ",
            }
        ]
    )
    xls = tmp_path / "spaces.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls), None)

    assert rows == [
        {
            "user_id": "4",
            "giorno": "2024-01-02",
            "inizio_1": "08:00",
            "fine_1": "12:00",
            "tipo": "NORMALE",
            "note": "",
        }
    ]


def test_parse_excel_day_off_nan_times(tmp_path):
    """NaN time cells in day-off rows should be returned as None."""
    df = pd.DataFrame(
        [
            {
                "User ID": 5,
                "Giorno": "2024-01-03",
                "Inizio1": float("nan"),
                "Fine1": float("nan"),
                "Tipo": "FESTIVO",
            }
        ]
    )
    xls = tmp_path / "dayoff_nan.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls), None)

    assert rows == [
        {
            "user_id": "5",
            "giorno": "2024-01-03",
            "inizio_1": None,
            "fine_1": None,
            "tipo": "FESTIVO",
            "note": "",
        }
    ]


def test_df_to_pdf_creates_files_and_cleanup(tmp_path):
    rows = [
        {
            "user_id": "1",
            "giorno": "2023-01-01",
            "inizio_1": "08:00:00",
            "fine_1": "12:00:00",
            "tipo": "NORMALE",
            "note": "",
        }
    ]

    def fake_from_file(html_path, pdf_path):
        Path(pdf_path).write_bytes(b"%PDF-1.4 fake")
        return True

    with patch(
        "app.services.excel_import.pdfkit.from_file", side_effect=fake_from_file
    ):
        pdf_path, html_path = df_to_pdf(rows, None)

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
            "inizio_1": "08:00:00",
            "fine_1": "12:00:00",
            "tipo": "NORMALE",
            "note": "",
        }
    ]

    def fake_from_file(html_path, pdf_path):
        raise OSError("No wkhtmltopdf executable found")

    with patch(
        "app.services.excel_import.pdfkit.from_file", side_effect=fake_from_file
    ):
        with pytest.raises(HTTPException) as exc:
            df_to_pdf(rows, None)

    assert exc.value.status_code == 500
    assert "wkhtmltopdf" in exc.value.detail
