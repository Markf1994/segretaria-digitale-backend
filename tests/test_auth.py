from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_success(setup_db):
    client.post(
        "/users/",
        json={"email": "auth@example.com", "password": "secret", "nome": "Test"},
    )
    response = client.post(
        "/login", json={"email": "auth@example.com", "password": "secret"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(setup_db):
    client.post(
        "/users/",
        json={"email": "wrong@example.com", "password": "secret", "nome": "Test"},
    )
    response = client.post(
        "/login", json={"email": "wrong@example.com", "password": "bad"}
    )
    assert response.status_code == 400
