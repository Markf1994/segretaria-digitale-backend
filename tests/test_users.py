import os
from unittest.mock import patch
from fastapi.testclient import TestClient

# Set test database before importing the app
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app

client = TestClient(app)

def auth_user(email: str, nome: str = "Test"):
    resp = client.post(
        "/users/",
        json={"email": email, "password": "secret", "nome": nome},
    )
    user_id = resp.json()["id"]
    token = client.post("/login", json={"email": email, "password": "secret"}).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id

def test_create_user():
    response = client.post(
        "/users/",
        json={"email": "test@example.com", "password": "secret", "nome": "Test"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["nome"] == "Test"
    assert "id" in data
    assert data["turni"] == []

def test_duplicate_user():
    client.post(
        "/users/",
        json={"email": "dup@example.com", "password": "secret", "nome": "Test"},
    )
    response = client.post(
        "/users/",
        json={"email": "dup@example.com", "password": "secret", "nome": "Test"},
    )
    assert response.status_code == 409


def test_list_users():
    client.post(
        "/users/",
        json={"email": "a@example.com", "password": "secret", "nome": "Beta"},
    )
    client.post(
        "/users/",
        json={"email": "b@example.com", "password": "secret", "nome": "Alpha"},
    )
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert [u["nome"] for u in data] == ["Alpha", "Beta"]


def test_user_turni_listed_after_creation(setup_db):
    with patch("app.services.gcal.sync_shift_event"), patch("app.services.gcal.delete_shift_event"):
        headers, user_id = auth_user("shift@example.com")

        shift = {
            "user_id": user_id,
            "giorno": "2023-01-01",
            "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
            "slot2": None,
            "slot3": None,
            "tipo": "NORMALE",
            "note": "",
        }
        res = client.post("/orari/", json=shift, headers=headers)
        assert res.status_code == 200

        res = client.get("/users/")
        assert res.status_code == 200
        users = res.json()
        found = next(u for u in users if u["id"] == user_id)
        assert len(found["turni"]) == 1

