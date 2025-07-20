from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_signage_horizontal(setup_db):
    data = {"azienda": "ACME", "descrizione": "Linea", "anno": 2024}
    res = client.post("/inventario/signage-horizontal/", json=data)
    assert res.status_code == 200
    body = res.json()
    assert body["azienda"] == "ACME"
    assert body["descrizione"] == "Linea"
    assert body["anno"] == 2024
    assert "id" in body


def test_update_signage_horizontal(setup_db):
    base = {"azienda": "ACME", "descrizione": "Old", "anno": 2023}
    res = client.post("/inventario/signage-horizontal/", json=base)
    rec_id = res.json()["id"]
    update = {"azienda": "Beta", "descrizione": "New", "anno": 2024}
    res = client.put(f"/inventario/signage-horizontal/{rec_id}", json=update)
    assert res.status_code == 200
    data = res.json()
    assert data["azienda"] == "Beta"
    assert data["descrizione"] == "New"
    assert data["anno"] == 2024


def test_list_signage_horizontal(setup_db):
    client.post("/inventario/signage-horizontal/", json={"azienda": "A", "descrizione": "A", "anno": 2023})
    client.post("/inventario/signage-horizontal/", json={"azienda": "B", "descrizione": "B", "anno": 2024})

    res = client.get("/inventario/signage-horizontal/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2

    res = client.get("/inventario/signage-horizontal/?year=2023")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["anno"] == 2023


def test_delete_signage_horizontal(setup_db):
    res = client.post("/inventario/signage-horizontal/", json={"azienda": "C", "descrizione": "C", "anno": 2022})
    rec_id = res.json()["id"]
    del_res = client.delete(f"/inventario/signage-horizontal/{rec_id}")
    assert del_res.status_code == 200
    assert del_res.json()["ok"] is True
    assert client.get("/inventario/signage-horizontal/").json() == []


def test_get_years(setup_db):
    client.post("/inventario/signage-horizontal/", json={"azienda": "A", "descrizione": "A", "anno": 2022})
    client.post("/inventario/signage-horizontal/", json={"azienda": "B", "descrizione": "B", "anno": 2024})
    res = client.get("/inventario/signage-horizontal/years")
    assert res.status_code == 200
    assert res.json() == [2022, 2024]
