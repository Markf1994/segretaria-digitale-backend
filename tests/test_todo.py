import os
from fastapi.testclient import TestClient

# Use same test database
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app

client = TestClient(app)


def auth_user(email: str):
    resp = client.post(
        "/users/",
        json={"email": email, "password": "secret", "nome": "User"},
    )
    user_id = resp.json()["id"]
    token = client.post(
        "/login", json={"email": email, "password": "secret"}
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_create_todo(setup_db):
    headers, user_id = auth_user("todo@example.com")
    response = client.post(
        "/todo/",
        json={"descrizione": "Task", "scadenza": "2023-01-01T10:00:00"},
        headers=headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["descrizione"] == "Task"
    assert data["user_id"] == user_id
    assert "id" in data


def test_update_todo(setup_db):
    headers, _ = auth_user("edit@example.com")
    create = client.post(
        "/todo/",
        json={"descrizione": "Old", "scadenza": "2023-01-01T10:00:00"},
        headers=headers,
    )
    todo_id = create.json()["id"]
    response = client.put(
        f"/todo/{todo_id}",
        json={"descrizione": "New", "scadenza": "2023-02-01T10:00:00"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["descrizione"] == "New"


def test_list_todos(setup_db):
    headers, _ = auth_user("list@example.com")
    client.post(
        "/todo/",
        json={"descrizione": "A", "scadenza": "2023-01-01T10:00:00"},
        headers=headers,
    )
    client.post(
        "/todo/",
        json={"descrizione": "B", "scadenza": "2023-01-02T10:00:00"},
        headers=headers,
    )
    response = client.get("/todo/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_delete_todo(setup_db):
    headers, _ = auth_user("del@example.com")
    res = client.post(
        "/todo/",
        json={"descrizione": "A", "scadenza": "2023-01-01T10:00:00"},
        headers=headers,
    )
    todo_id = res.json()["id"]
    response = client.delete(f"/todo/{todo_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert client.get("/todo/", headers=headers).json() == []


def test_user_isolated_todos(setup_db):
    h1, id1 = auth_user("u1@example.com")
    h2, id2 = auth_user("u2@example.com")

    client.post(
        "/todo/",
        json={"descrizione": "U1", "scadenza": "2023-01-01T10:00:00"},
        headers=h1,
    )
    client.post(
        "/todo/",
        json={"descrizione": "U2", "scadenza": "2023-01-02T10:00:00"},
        headers=h2,
    )
    client.post(
        "/todo/",
        json={"descrizione": "U1B", "scadenza": "2023-01-03T10:00:00"},
        headers=h1,
    )

    res1 = client.get("/todo/", headers=h1)
    res2 = client.get("/todo/", headers=h2)

    assert len(res1.json()) == 2
    assert len(res2.json()) == 1
    assert all(t["user_id"] == id1 for t in res1.json())
    assert all(t["user_id"] == id2 for t in res2.json())

