import os
import pytest
from fastapi.testclient import TestClient

# Set test database before importing the app
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app
from app.database import Base, engine

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

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

