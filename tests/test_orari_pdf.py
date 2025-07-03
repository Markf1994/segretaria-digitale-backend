import os
from pathlib import Path
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# Patch Google API clients before importing the app
with patch(
    "google.oauth2.service_account.Credentials.from_service_account_file",
    return_value=MagicMock(),
):
    with patch("googleapiclient.discovery.build", return_value=MagicMock()):
        os.environ["DATABASE_URL"] = "sqlite:///./test.db"
        from app.main import app

client = TestClient(app)


def auth_user(email: str):
    resp = client.post(
        "/users/", json={"email": email, "password": "secret", "nome": "Test"}
    )
    user_id = resp.json()["id"]
    token = client.post("/login", json={"email": email, "password": "secret"}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_orari_pdf_returns_pdf(setup_db, tmp_path):
    headers, user_id = auth_user("shift@example.com")
    data = {
        "user_id": user_id,
        "giorno": "2023-01-04",
        "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
        "slot2": None,
        "slot3": None,
        "tipo": "NORMALE",
        "note": "",
    }
    client.post("/orari/", json=data, headers=headers)

    def fake_from_file(html_path, pdf_path):
        Path(pdf_path).write_bytes(b"%PDF-1.4 fake")
        return True

    with patch(
        "app.services.excel_import.pdfkit.from_file", side_effect=fake_from_file
    ):
        res = client.get("/orari/pdf?week=2023-W01", headers=headers)

    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
