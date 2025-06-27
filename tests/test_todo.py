import os
from datetime import datetime
from fastapi.testclient import TestClient
import pytest

# Use same test database
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app

from tests.test_users import setup_db  # reuse fixture

client = TestClient(app)

def test_create_todo(setup_db):
    response = client.post(
        "/todo/",
        json={"descrizione": "Task", "scadenza": "2023-01-01T10:00:00"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["descrizione"] == "Task"
    assert "id" in data


def test_update_todo(setup_db):
    create = client.post(
        "/todo/",
        json={"descrizione": "Old", "scadenza": "2023-01-01T10:00:00"},
    )
    todo_id = create.json()["id"]
    response = client.put(
        f"/todo/{todo_id}",
        json={"descrizione": "New", "scadenza": "2023-02-01T10:00:00"},
    )
    assert response.status_code == 200
    assert response.json()["descrizione"] == "New"


def test_list_todos(setup_db):
    client.post("/todo/", json={"descrizione": "A", "scadenza": "2023-01-01T10:00:00"})
    client.post("/todo/", json={"descrizione": "B", "scadenza": "2023-01-02T10:00:00"})
    response = client.get("/todo/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_delete_todo(setup_db):
    res = client.post(
        "/todo/",
        json={"descrizione": "A", "scadenza": "2023-01-01T10:00:00"},
    )
    todo_id = res.json()["id"]
    response = client.delete(f"/todo/{todo_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert client.get("/todo/").json() == []
