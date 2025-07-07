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


def test_google_login_valid(monkeypatch, setup_db):
    client.post(
        "/users/",
        json={"email": "google@example.com", "password": "secret", "nome": "G"},
    )

    monkeypatch.setenv("GOOGLE_CLIENT_ID", "gid")
    from app import config

    config.reload_settings()

    def fake_verify(token, req, client_id):
        assert token == "tok"
        assert client_id == "gid"
        return {"email": "google@example.com"}

    monkeypatch.setattr(
        "google.oauth2.id_token.verify_oauth2_token", fake_verify
    )

    res = client.post("/google-login", json={"token": "tok"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_google_login_invalid(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "gid")
    from app import config

    config.reload_settings()

    def fake_verify(token, req, client_id):
        raise ValueError("bad")

    monkeypatch.setattr(
        "google.oauth2.id_token.verify_oauth2_token", fake_verify
    )

    res = client.post("/google-login", json={"token": "bad"})
    assert res.status_code == 400
