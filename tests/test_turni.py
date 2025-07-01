import os
from fastapi.testclient import TestClient

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


def base_payload(user_id: str):
    return {
        "user_id": user_id,
        "giorno": "2023-01-01",
        "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
        "tipo": "NORMALE",
        "note": "test",
    }


def test_create_turno(monkeypatch, setup_db):
    headers, user_id = auth_user("turno_create@example.com")
    monkeypatch.setattr("app.services.gcal.sync_shift_event", lambda turno: None)
    payload = base_payload(user_id)
    res = client.post("/turni/", json=payload, headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["user_id"] == user_id
    assert body["tipo"] == "NORMALE"
    assert "id" in body


def test_update_turno(monkeypatch, setup_db):
    headers, user_id = auth_user("turno_update@example.com")
    monkeypatch.setattr("app.services.gcal.sync_shift_event", lambda turno: None)
    first = client.post("/turni/", json=base_payload(user_id), headers=headers)
    turno_id = first.json()["id"]
    update_payload = base_payload(user_id)
    update_payload["slot1"] = {"inizio": "09:00:00", "fine": "13:00:00"}
    update_payload["tipo"] = "STRAORD"
    res = client.post("/turni/", json=update_payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == turno_id
    assert data["tipo"] == "STRAORD"
    assert data["inizio_1"] == "09:00:00"


def test_delete_turno(monkeypatch, setup_db):
    headers, user_id = auth_user("turno_delete@example.com")
    monkeypatch.setattr("app.services.gcal.sync_shift_event", lambda turno: None)
    monkeypatch.setattr("app.services.gcal.delete_shift_event", lambda tid: None)
    create = client.post("/turni/", json=base_payload(user_id), headers=headers)
    turno_id = create.json()["id"]
    res = client.delete(f"/turni/{turno_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["ok"] is True
    res2 = client.delete(f"/turni/{turno_id}", headers=headers)
    assert res2.status_code == 404
