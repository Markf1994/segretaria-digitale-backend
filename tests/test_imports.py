import os
from unittest.mock import patch, MagicMock
from pathlib import Path
import pandas as pd
from fastapi.testclient import TestClient

# Patch Google API clients before importing the app
with patch("google.oauth2.service_account.Credentials.from_service_account_file", return_value=MagicMock()):
    with patch("googleapiclient.discovery.build", return_value=MagicMock()):
        os.environ["DATABASE_URL"] = "sqlite:///./test.db"
        from app.main import app

client = TestClient(app)

def auth_user(email: str):
    resp = client.post("/users/", json={"email": email, "password": "secret"})
    user_id = resp.json()["id"]
    token = client.post("/login", json={"email": email, "password": "secret"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_import_xlsx_creates_turni_and_returns_pdf(setup_db, tmp_path):
    headers, user_id = auth_user("sheet@example.com")
    df = pd.DataFrame([
        {
            "User ID": user_id,
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
