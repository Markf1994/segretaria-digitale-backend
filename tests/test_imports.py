import os
from unittest.mock import patch
from pathlib import Path
import pandas as pd
from fastapi.testclient import TestClient
from fastapi import HTTPException

from app.main import app

client = TestClient(app)

def auth_user(email: str, nome: str = "Mario Rossi"):
    resp = client.post("/users/", json={"email": email, "password": "secret", "nome": nome})
    body = resp.json()
    user_id = body["id"]
    token = client.post("/login", json={"email": email, "password": "secret"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id, nome


def test_import_xlsx_creates_turni_and_returns_pdf(setup_db, tmp_path):
    headers, user_id, nome = auth_user("sheet@example.com")
    df = pd.DataFrame([
        {
            "Agente": nome,
            "Data": "2023-01-01",
            "Inizio1": "08:00:00",
            "Fine1": "12:00:00",
        }
    ])
    xlsx_path = tmp_path / "shift.xlsx"
    df.to_excel(xlsx_path, index=False)

    def fake_from_file(html_path, pdf_path):
        Path(pdf_path).write_bytes(b"%PDF-1.4 fake")
        return True

    with patch("app.services.excel_import.pdfkit.from_file", side_effect=fake_from_file):
        with open(xlsx_path, "rb") as fh:
            res = client.post(
                "/import/xlsx",
                files={"file": ("shift.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"

    list_res = client.get("/orari/", headers=headers)
    assert list_res.status_code == 200
    body = list_res.json()
    assert len(body) == 1
    assert body[0]["user_id"] == user_id


def test_temp_files_removed_after_request(setup_db, tmp_path):
    captured = {}

    def fake_parse_excel(path, db):
        captured['xlsx'] = path
        return []

    def fake_from_file(html_path, pdf_path):
        captured['html'] = html_path
        captured['pdf'] = pdf_path
        Path(pdf_path).write_bytes(b"%PDF-1.4 fake")
        return True

    with patch("app.routes.imports.parse_excel", side_effect=fake_parse_excel):
        with patch("app.services.excel_import.pdfkit.from_file", side_effect=fake_from_file):
            dummy = tmp_path / "shift.xlsx"
            dummy.write_bytes(b"data")
            with open(dummy, "rb") as fh:
                res = client.post(
                    "/import/xlsx",
                    files={"file": ("shift.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                )
    assert res.status_code == 200
    assert not os.path.exists(captured['xlsx'])
    assert not os.path.exists(captured['html'])
    assert not os.path.exists(captured['pdf'])


def test_parse_error_returns_400_and_removes_xlsx(tmp_path):
    captured = {}

    def fake_parse_excel(path, db):
        captured['xlsx'] = path
        raise HTTPException(status_code=400, detail="bad data")

    with patch("app.routes.imports.parse_excel", side_effect=fake_parse_excel):
        dummy = tmp_path / "shift.xlsx"
        dummy.write_bytes(b"data")
        with open(dummy, "rb") as fh:
            res = client.post(
                "/import/xlsx",
                files={"file": ("shift.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )

    assert res.status_code == 400
    assert not os.path.exists(captured['xlsx'])


def test_import_excel_alias_returns_pdf(tmp_path):
    df = pd.DataFrame([
        {
            "Agente": "Mario Rossi",
            "Data": "2023-01-01",
            "Inizio1": "08:00:00",
            "Fine1": "12:00:00",
        }
    ])
    xlsx_path = tmp_path / "shift.xlsx"
    df.to_excel(xlsx_path, index=False)

    def fake_from_file(html_path, pdf_path):
        Path(pdf_path).write_bytes(b"%PDF-1.4 fake")
        return True

    with patch("app.services.excel_import.pdfkit.from_file", side_effect=fake_from_file):
        with open(xlsx_path, "rb") as fh:
            res = client.post(
                "/import/excel",
                files={"file": ("shift.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
            )

    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"


def test_import_xlsx_unknown_agent_returns_400(tmp_path):
    """Uploading a sheet with an unknown Agente should return a 400 response."""
    df = pd.DataFrame([
        {
            "Agente": "Unknown Agent",
            "Data": "2023-01-01",
            "Inizio1": "08:00:00",
            "Fine1": "12:00:00",
        }
    ])
    xlsx_path = tmp_path / "unknown.xlsx"
    df.to_excel(xlsx_path, index=False)

    with open(xlsx_path, "rb") as fh:
        res = client.post(
            "/import/xlsx",
            files={"file": ("unknown.xlsx", fh, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )

    assert res.status_code == 400
    assert "Unknown user" in res.json()["detail"]
