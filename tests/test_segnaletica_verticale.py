from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_segnaletica_verticale(setup_db):
    data = {
        "descrizione": "Cartello stop",
        "tipo": "Cartello",
        "quantita": 2,
        "luogo": "Via Roma",
        "anno": 2024,
    }
    response = client.post("/segnaletica-verticale/", json=data)
    assert response.status_code == 200
    body = response.json()
    assert body["descrizione"] == "Cartello stop"
    assert body["tipo"] == "Cartello"
    assert body["quantita"] == 2
    assert body["luogo"] == "Via Roma"
    assert body["anno"] == 2024
    assert "id" in body


def test_update_segnaletica_verticale(setup_db):
    base = {
        "descrizione": "Segnale",
        "tipo": "Cartello",
        "quantita": 1,
        "luogo": "Piazza",
        "anno": 2023,
    }
    res = client.post("/segnaletica-verticale/", json=base)
    sv_id = res.json()["id"]
    base["descrizione"] = "Segnale nuovo"
    base["quantita"] = 3
    base["luogo"] = "Centro"
    update = client.put(f"/segnaletica-verticale/{sv_id}", json=base)
    assert update.status_code == 200
    data = update.json()
    assert data["descrizione"] == "Segnale nuovo"
    assert data["quantita"] == 3
    assert data["luogo"] == "Centro"


def test_list_segnaletica_verticale(setup_db):
    client.post(
        "/segnaletica-verticale/",
        json={
            "descrizione": "A",
            "tipo": "Cartello",
            "quantita": 1,
            "luogo": "Via A",
            "anno": 2023,
        },
    )
    client.post(
        "/segnaletica-verticale/",
        json={
            "descrizione": "B",
            "tipo": "Cartello",
            "quantita": 2,
            "luogo": "Via B",
            "anno": 2024,
        },
    )
    res = client.get("/segnaletica-verticale/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert {item["descrizione"] for item in data} == {"A", "B"}


def test_delete_segnaletica_verticale(setup_db):
    res = client.post(
        "/segnaletica-verticale/",
        json={
            "descrizione": "X",
            "tipo": "Cartello",
            "quantita": 1,
            "luogo": "Zona",
            "anno": 2022,
        },
    )
    sv_id = res.json()["id"]
    del_res = client.delete(f"/segnaletica-verticale/{sv_id}")
    assert del_res.status_code == 200
    assert del_res.json()["ok"] is True
    assert client.get("/segnaletica-verticale/").json() == []
