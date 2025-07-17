from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_update_item(setup_db):
    # Create piano
    res = client.post(
        "/piani-orizzontali/",
        json={"descrizione": "Piano", "anno": 2024},
    )
    piano_id = res.json()["id"]

    # Add item
    item_res = client.post(
        f"/piani-orizzontali/{piano_id}/items",
        json={"descrizione": "Old", "quantita": 1},
    )
    item_id = item_res.json()["id"]

    # Update only quantita
    update_res = client.put(
        f"/piani-orizzontali/items/{item_id}",
        json={"quantita": 5},
    )
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["quantita"] == 5
    assert data["descrizione"] == "Old"


def test_update_item_not_found(setup_db):
    response = client.put(
        "/piani-orizzontali/items/unknown",
        json={"descrizione": "X"},
    )
    assert response.status_code == 404
