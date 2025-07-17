from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_dispositivo_with_note(setup_db):
    data = {"nome": "Tablet", "descrizione": "iPad", "anno": 2024, "note": "demo"}
    res = client.post("/dispositivi/", json=data)
    assert res.status_code == 200
    body = res.json()
    assert body["note"] == "demo"
    assert body["nome"] == "Tablet"


def test_list_dispositivi_shows_note(setup_db):
    client.post(
        "/dispositivi/",
        json={"nome": "Phone", "descrizione": "Pixel", "anno": 2023, "note": "abc"},
    )
    client.post(
        "/dispositivi/",
        json={"nome": "Laptop", "descrizione": "Dell", "anno": 2022, "note": "xyz"},
    )
    res = client.get("/dispositivi/")
    assert res.status_code == 200
    notes = [d["note"] for d in res.json()]
    assert "abc" in notes and "xyz" in notes
