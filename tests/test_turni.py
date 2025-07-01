import os
from unittest.mock import patch, MagicMock
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
    token = client.post(
        "/login",
        json={"email": email, "password": "secret"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_create_turno(setup_db):
    _, user_id = auth_user("shift@example.com")
    data = {
        "user_id": user_id,
        "giorno": "2023-01-01",
        "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
        "slot2": {"inizio": "13:00:00", "fine": "17:00:00"},
        "slot3": None,
        "tipo": "NORMALE",
        "note": "test",
    }
    res = client.post("/orari/", json=data)
    assert res.status_code == 200
    body = res.json()
    assert body["user_id"] == user_id
    assert body["giorno"] == "2023-01-01"
    assert body["slot1"] == {"inizio": "08:00:00", "fine": "12:00:00"}
    assert body["slot2"] == {"inizio": "13:00:00", "fine": "17:00:00"}
    assert body["slot3"] is None


def test_update_turno(setup_db):
    _, user_id = auth_user("update@example.com")
    base = {
        "user_id": user_id,
        "giorno": "2023-01-02",
        "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
        "slot2": None,
        "slot3": None,
        "tipo": "NORMALE",
        "note": "",
    }
    first = client.post("/orari/", json=base)
    turno_id = first.json()["id"]
    base["slot1"] = {"inizio": "09:00:00", "fine": "13:00:00"}
    base["tipo"] = "STRAORD"
    update = client.post("/orari/", json=base)
    assert update.status_code == 200
    updated = update.json()
    assert updated["id"] == turno_id
    assert updated["slot1"] == {"inizio": "09:00:00", "fine": "13:00:00"}
    assert updated["tipo"] == "STRAORD"


def test_delete_turno(setup_db):
    _, user_id = auth_user("delete@example.com")
    data = {
        "user_id": user_id,
        "giorno": "2023-01-03",
        "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
        "slot2": None,
        "slot3": None,
        "tipo": "NORMALE",
        "note": "",
    }
    res = client.post("/orari/", json=data)
    turno_id = res.json()["id"]
    del_res = client.delete(f"/orari/{turno_id}")
    assert del_res.status_code == 200
    assert del_res.json()["ok"] is True
    list_res = client.get("/orari/")
    assert list_res.status_code == 200
    assert list_res.json() == []


def test_shift_event_summary_email(setup_db):
    headers, user_id = auth_user("cal@example.com")

    captured = {}

    class DummyClient:
        def events(self):
            class Events:
                def update(self, calendarId=None, eventId=None, body=None):
                    captured["body"] = body
                    return MagicMock(execute=MagicMock())

            return Events()

    with patch("app.services.gcal.get_client", return_value=DummyClient()):
        client.post(
            "/orari/",
            json={
                "user_id": user_id,
                "giorno": "2023-05-05",
                "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
                "slot2": None,
                "slot3": None,
                "tipo": "NORMALE",
                "note": "",
            },
            headers=headers,
        )

    assert captured["body"]["summary"] == "cal@example.com"
