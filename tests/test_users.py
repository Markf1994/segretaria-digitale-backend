from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_user(email: str, nome: str = "Test"):
    resp = client.post(
        "/users/",
        json={"email": email, "password": "secret", "nome": nome},
    )
    user_id = resp.json()["id"]
    token = client.post("/login", json={"email": email, "password": "secret"}).json()[
        "access_token"
    ]
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
    with patch("app.services.gcal.sync_shift_event"), patch(
        "app.services.gcal.delete_shift_event"
    ):
        headers, user_id = auth_user("shift@example.com")

        shift = {
            "user_id": user_id,
            "giorno": "2023-01-01",
            "inizio_1": "08:00:00",
            "fine_1": "12:00:00",
            "inizio_2": None,
            "fine_2": None,
            "inizio_3": None,
            "fine_3": None,
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


def test_get_user_by_email_success():
    resp = client.post(
        "/users/",
        json={"email": "lookup@example.com", "password": "secret", "nome": "Lookup"},
    )
    user_id = resp.json()["id"]

    response = client.get("/users/by-email", params={"email": "lookup@example.com"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "lookup@example.com"


def test_get_user_by_email_not_found():
    response = client.get("/users/by-email", params={"email": "missing@example.com"})
    assert response.status_code == 404


def test_get_current_user(setup_db):
    headers, user_id = auth_user("me@example.com")
    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "me@example.com"


def test_get_current_user_missing_header():
    response = client.get("/users/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authorization header missing"
