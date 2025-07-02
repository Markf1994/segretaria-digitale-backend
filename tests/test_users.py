import os
from fastapi.testclient import TestClient

# Set test database before importing the app
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app

client = TestClient(app)

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

def test_duplicate_user():
    client.post(
        "/users/",
        json={"email": "dup@example.com", "password": "secret", "nome": "Dup"},
    )
    response = client.post(
        "/users/",
        json={"email": "dup@example.com", "password": "secret", "nome": "Dup"},
    )
    assert response.status_code == 409


def test_list_users():
    client.post(
        "/users/",
        json={"email": "a@example.com", "password": "secret", "nome": "A"},
    )
    client.post(
        "/users/",
        json={"email": "b@example.com", "password": "secret", "nome": "B"},
    )
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert [u["email"] for u in data] == ["a@example.com", "b@example.com"]
    assert [u["nome"] for u in data] == ["A", "B"]

