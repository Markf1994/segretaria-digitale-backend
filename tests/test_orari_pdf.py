import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Patch Google API clients before importing the app
with patch("google.oauth2.service_account.Credentials.from_service_account_file", return_value=MagicMock()):
    with patch("googleapiclient.discovery.build", return_value=MagicMock()):
        os.environ["DATABASE_URL"] = "sqlite:///./test.db"
        from app.main import app

client = TestClient(app)


def auth_user(email: str, nome: str = "Test"):
    resp = client.post("/users/", json={"email": email, "password": "secret", "nome": nome})
    user_id = resp.json()["id"]
    token = client.post("/login", json={"email": email, "password": "secret"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_week_pdf_filters_turni(setup_db, tmp_path):
    headers, user_id = auth_user("week@example.com")

    shift1 = {
        "user_id": user_id,
        "giorno": "2023-01-02",
        "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
        "slot2": None,
        "slot3": None,
        "tipo": "NORMALE",
        "note": "",
    }
    shift2 = {
        "user_id": user_id,
        "giorno": "2023-01-08",
        "slot1": {"inizio": "09:00:00", "fine": "13:00:00"},
        "slot2": None,
        "slot3": None,
        "tipo": "NORMALE",
        "note": "",
    }
    shift3 = {
        "user_id": user_id,
        "giorno": "2023-01-09",
        "slot1": {"inizio": "10:00:00", "fine": "14:00:00"},
        "slot2": None,
        "slot3": None,
        "tipo": "NORMALE",
        "note": "",
    }

    client.post("/orari/", json=shift1, headers=headers)
    client.post("/orari/", json=shift2, headers=headers)
    client.post("/orari/", json=shift3, headers=headers)

    captured = {}
    real_df_to_pdf = __import__("app.services.excel_import", fromlist=["df_to_pdf"]).df_to_pdf

    def fake_from_file(html_path, pdf_path):
        Path(pdf_path).write_bytes(b"%PDF-1.4 fake")
        return True

    def capture_df_to_pdf(rows):
        captured["rows"] = rows
        return real_df_to_pdf(rows)

    with patch("app.services.excel_import.pdfkit.from_file", side_effect=fake_from_file):
        with patch("app.routes.orari.df_to_pdf", side_effect=capture_df_to_pdf):
            res = client.get("/orari/pdf?week=2023-W01", headers=headers)

    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(captured["rows"]) == 2
    days = {r["giorno"] for r in captured["rows"]}
    assert days == {"2023-01-02", "2023-01-08"}


def test_week_pdf_invalid_format(setup_db):
    """Requesting an invalid week string should return a 400 error."""
    headers, _ = auth_user("badweek@example.com")

    res = client.get("/orari/pdf?week=bad", headers=headers)

    assert res.status_code == 400
    assert "Invalid week format" in res.json()["detail"]


def test_week_pdf_temp_files_removed(setup_db, tmp_path):
    """Temporary PDF and HTML files should be cleaned up after the request."""
    headers, user_id = auth_user("clean@example.com")

    shift = {
        "user_id": user_id,
        "giorno": "2023-01-02",
        "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
        "slot2": None,
        "slot3": None,
        "tipo": "NORMALE",
        "note": "",
    }

    client.post("/orari/", json=shift, headers=headers)

    captured = {}

    def fake_df_to_pdf(rows):
        pdf_path = tmp_path / "week.pdf"
        html_path = tmp_path / "week.html"
        pdf_path.write_bytes(b"%PDF-1.4 fake")
        html_path.write_text("<html></html>")
        captured["pdf"] = str(pdf_path)
        captured["html"] = str(html_path)
        return str(pdf_path), str(html_path)

    with patch("app.routes.orari.df_to_pdf", side_effect=fake_df_to_pdf):
        res = client.get("/orari/pdf?week=2023-W01", headers=headers)

    assert res.status_code == 200
    assert not os.path.exists(captured["pdf"])
    assert not os.path.exists(captured["html"])
