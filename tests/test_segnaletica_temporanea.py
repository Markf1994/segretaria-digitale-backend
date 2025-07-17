from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_segnaletica_temporanea(setup_db):
    data = {
        "descrizione": "Cartello",
        "anno": 2024,
        "luogo": "Via Roma",
        "fine_validita": "2024-06-30",
        "quantita": 2,
    }
    response = client.post("/segnaletica-temporanea/", json=data)
    assert response.status_code == 200
    body = response.json()
    assert body["descrizione"] == "Cartello"
    assert body["luogo"] == "Via Roma"
    assert body["fine_validita"] == "2024-06-30"
    assert body["quantita"] == 2
    assert "id" in body


def test_update_segnaletica_temporanea(setup_db):
    create = client.post(
        "/segnaletica-temporanea/",
        json={
            "descrizione": "Old",
            "anno": 2023,
            "luogo": "Old",
            "fine_validita": "2023-06-01",
            "quantita": 1,
        },
    )
    st_id = create.json()["id"]
    response = client.put(
        f"/segnaletica-temporanea/{st_id}",
        json={
            "descrizione": "New",
            "anno": 2024,
            "luogo": "New",
            "fine_validita": "2024-07-01",
            "quantita": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["descrizione"] == "New"
    assert data["luogo"] == "New"
    assert data["fine_validita"] == "2024-07-01"
    assert data["quantita"] == 5


def test_list_segnaletica_temporanea(setup_db):
    client.post(
        "/segnaletica-temporanea/",
        json={
            "descrizione": "A",
            "anno": 2024,
            "luogo": "A",
            "fine_validita": "2024-05-01",
            "quantita": 1,
        },
    )
    client.post(
        "/segnaletica-temporanea/",
        json={
            "descrizione": "B",
            "anno": 2023,
            "luogo": "B",
            "fine_validita": "2023-05-01",
            "quantita": 2,
        },
    )
    response = client.get("/segnaletica-temporanea/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_delete_segnaletica_temporanea(setup_db):
    res = client.post(
        "/segnaletica-temporanea/",
        json={
            "descrizione": "Del",
            "anno": 2022,
            "luogo": "Del",
            "fine_validita": "2022-05-01",
            "quantita": 1,
        },
    )
    st_id = res.json()["id"]
    response = client.delete(f"/segnaletica-temporanea/{st_id}")
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert client.get("/segnaletica-temporanea/").json() == []
