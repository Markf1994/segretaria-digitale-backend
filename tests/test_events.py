from fastapi.testclient import TestClient
import logging

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


def test_create_event(setup_db):
    headers, user_id = auth_user("ev@example.com")
    data = {
        "titolo": "Meeting",
        "descrizione": "Desc",
        "data_ora": "2023-01-01T09:00:00",
        "is_public": True,
    }
    response = client.post("/events/", json=data, headers=headers)
    assert response.status_code == 201
    body = response.json()
    assert body["titolo"] == "Meeting"
    assert body["user_id"] == user_id
    assert "id" in body


def test_update_event(setup_db):
    headers, _ = auth_user("edit@example.com")
    res = client.post(
        "/events/",
        json={
            "titolo": "Old",
            "descrizione": "Start",
            "data_ora": "2023-01-01T09:00:00",
            "is_public": False,
        },
        headers=headers,
    )
    event_id = res.json()["id"]
    response = client.put(
        f"/events/{event_id}",
        json={
            "titolo": "New",
            "descrizione": "Updated",
            "data_ora": "2023-01-02T10:00:00",
            "is_public": True,
        },
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["titolo"] == "New"
    assert data["descrizione"] == "Updated"


def test_list_events(setup_db):
    h1, _ = auth_user("a@example.com")
    h2, _ = auth_user("b@example.com")
    client.post(
        "/events/",
        json={
            "titolo": "A",
            "descrizione": "",
            "data_ora": "2023-01-01T09:00:00",
            "is_public": False,
        },
        headers=h1,
    )
    client.post(
        "/events/",
        json={
            "titolo": "B",
            "descrizione": "",
            "data_ora": "2023-01-02T09:00:00",
            "is_public": False,
        },
        headers=h2,
    )
    client.post(
        "/events/",
        json={
            "titolo": "Pub",
            "descrizione": "",
            "data_ora": "2023-01-03T09:00:00",
            "is_public": True,
        },
        headers=h2,
    )
    res1 = client.get("/events/", headers=h1)
    res2 = client.get("/events/", headers=h2)
    res3 = client.get("/events/")
    assert len(res1.json()) == 2
    assert len(res2.json()) == 2
    assert len(res3.json()) == 1


def test_delete_event(setup_db):
    headers, _ = auth_user("del@example.com")
    res = client.post(
        "/events/",
        json={
            "titolo": "A",
            "descrizione": "",
            "data_ora": "2023-01-01T09:00:00",
            "is_public": False,
        },
        headers=headers,
    )
    event_id = res.json()["id"]
    response = client.delete(f"/events/{event_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert client.get("/events/", headers=headers).json() == []


def test_google_calendar_called_on_create(monkeypatch, setup_db):
    headers, _ = auth_user("gcal@example.com")
    called = {}

    def fake_create(event):
        called["id"] = event.id

    monkeypatch.setattr("app.services.calendar_events.create_event", fake_create)

    data = {
        "titolo": "Meeting",
        "descrizione": "Desc",
        "data_ora": "2025-01-01T09:00:00",
        "is_public": True,
    }

    res = client.post("/events/", json=data, headers=headers)

    assert res.status_code == 201
    assert "id" in called


def test_google_calendar_error_does_not_fail(monkeypatch, setup_db, caplog):
    headers, _ = auth_user("gerr@example.com")

    def fail_create(event):
        raise RuntimeError("boom")

    monkeypatch.setattr("app.services.calendar_events.create_event", fail_create)

    data = {
        "titolo": "Meeting",
        "descrizione": "Desc",
        "data_ora": "2025-01-01T10:00:00",
        "is_public": False,
    }

    with caplog.at_level(logging.ERROR):
        res = client.post("/events/", json=data, headers=headers)

    assert res.status_code == 201
    assert "Errore sync calendario" in caplog.text
