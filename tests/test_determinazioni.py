from fastapi.testclient import TestClient


from app.main import app

client = TestClient(app)

def test_create_determinazione(setup_db):
    data = {
        "capitolo": "A",
        "numero": "1",
        "descrizione": "Det",
        "somma": 100.0,
        "scadenza": "2023-01-01T00:00:00",
    }
    response = client.post("/determinazioni/", json=data)
    assert response.status_code == 200
    body = response.json()
    assert body["capitolo"] == "A"
    assert body["descrizione"] == "Det"
    assert "id" in body


def test_update_determinazione(setup_db):
    res = client.post(
        "/determinazioni/",
        json={"capitolo": "A", "numero": "1", "descrizione": "Old", "somma": 100.0, "scadenza": "2023-01-01T00:00:00"},
    )
    det_id = res.json()["id"]
    response = client.put(
        f"/determinazioni/{det_id}",
        json={"capitolo": "B", "numero": "1", "descrizione": "New", "somma": 200.0, "scadenza": "2023-02-01T00:00:00"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["capitolo"] == "B"
    assert data["descrizione"] == "New"


def test_list_determinazioni(setup_db):
    client.post("/determinazioni/", json={"capitolo": "A", "numero": "1", "descrizione": "", "somma": 50.0, "scadenza": "2023-01-01T00:00:00"})
    client.post("/determinazioni/", json={"capitolo": "B", "numero": "2", "descrizione": "", "somma": 75.0, "scadenza": "2023-01-02T00:00:00"})
    response = client.get("/determinazioni/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_determinazione(setup_db):
    res = client.post("/determinazioni/", json={"capitolo": "A", "numero": "1", "descrizione": "", "somma": 50.0, "scadenza": "2023-01-01T00:00:00"})
    det_id = res.json()["id"]
    response = client.delete(f"/determinazioni/{det_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert client.get("/determinazioni/").json() == []
