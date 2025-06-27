import os
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app
from tests.test_users import setup_db

client = TestClient(app)

def test_create_event(setup_db):
    data = {
        "titolo": "Meeting",
        "descrizione": "Desc",
        "data_ora": "2023-01-01T09:00:00",
        "is_public": True,
    }
    response = client.post("/events/", json=data)
    assert response.status_code == 200
    body = response.json()
    assert body["titolo"] == "Meeting"
    assert "id" in body


def test_update_event(setup_db):
    res = client.post(
        "/events/",
        json={
            "titolo": "Old",
            "descrizione": "",
            "data_ora": "2023-01-01T09:00:00",
            "is_public": False,
        },
    )
    event_id = res.json()["id"]
    response = client.put(
        f"/events/{event_id}",
        json={
            "titolo": "New",
            "descrizione": "",
            "data_ora": "2023-01-02T10:00:00",
            "is_public": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["titolo"] == "New"


def test_list_events(setup_db):
    client.post(
        "/events/",
        json={"titolo": "A", "descrizione": "", "data_ora": "2023-01-01T09:00:00", "is_public": False},
    )
    client.post(
        "/events/",
        json={"titolo": "B", "descrizione": "", "data_ora": "2023-01-02T09:00:00", "is_public": False},
    )
    response = client.get("/events/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_event(setup_db):
    res = client.post(
        "/events/",
        json={"titolo": "A", "descrizione": "", "data_ora": "2023-01-01T09:00:00", "is_public": False},
    )
    event_id = res.json()["id"]
    response = client.delete(f"/events/{event_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert client.get("/events/").json() == []
