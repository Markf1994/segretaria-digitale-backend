import os
from fastapi.testclient import TestClient
import pytest

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app
from tests.test_users import setup_db

client = TestClient(app)

def test_create_determinazione(setup_db):
    data = {
        "capitolo": "A",
        "numero": "1",
        "somma": 100.0,
        "scadenza": "2023-01-01T00:00:00",
    }
    response = client.post("/determinazioni/", json=data)
    assert response.status_code == 200
    body = response.json()
    assert body["capitolo"] == "A"
    assert "id" in body


def test_update_determinazione(setup_db):
    res = client.post(
        "/determinazioni/",
        json={"capitolo": "A", "numero": "1", "somma": 100.0, "scadenza": "2023-01-01T00:00:00"},
    )
    det_id = res.json()["id"]
    response = client.put(
        f"/determinazioni/{det_id}",
        json={"capitolo": "B", "numero": "1", "somma": 200.0, "scadenza": "2023-02-01T00:00:00"},
    )
    assert response.status_code == 200
    assert response.json()["capitolo"] == "B"


def test_list_determinazioni(setup_db):
    client.post("/determinazioni/", json={"capitolo": "A", "numero": "1", "somma": 50.0, "scadenza": "2023-01-01T00:00:00"})
    client.post("/determinazioni/", json={"capitolo": "B", "numero": "2", "somma": 75.0, "scadenza": "2023-01-02T00:00:00"})
    response = client.get("/determinazioni/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_determinazione(setup_db):
    res = client.post("/determinazioni/", json={"capitolo": "A", "numero": "1", "somma": 50.0, "scadenza": "2023-01-01T00:00:00"})
    det_id = res.json()["id"]
    response = client.delete(f"/determinazioni/{det_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert client.get("/determinazioni/").json() == []
