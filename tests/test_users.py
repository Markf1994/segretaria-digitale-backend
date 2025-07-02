import os
from fastapi.testclient import TestClient

# Set test database before importing the app
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={"email": "test@example.com", "password": "secret"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_duplicate_user():
    client.post("/users/", json={"email": "dup@example.com", "password": "secret"})
    response = client.post("/users/", json={"email": "dup@example.com", "password": "secret"})
    assert response.status_code == 409


def test_list_users():
    client.post("/users/", json={"email": "a@example.com", "password": "secret"})
    client.post("/users/", json={"email": "b@example.com", "password": "secret"})
    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert [u["email"] for u in data] == ["a@example.com", "b@example.com"]

