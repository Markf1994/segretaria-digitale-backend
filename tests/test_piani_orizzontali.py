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


def test_list_items(setup_db):
    res = client.post(
        "/piani-orizzontali/",
        json={"descrizione": "Piano", "anno": 2024},
    )
    piano_id = res.json()["id"]

    item1 = client.post(
        f"/piani-orizzontali/{piano_id}/items",
        json={"descrizione": "A", "quantita": 1},
    ).json()
    item2 = client.post(
        f"/piani-orizzontali/{piano_id}/items",
        json={"descrizione": "B", "quantita": 2},
    ).json()

    list_res = client.get(f"/piani-orizzontali/{piano_id}/items")
    assert list_res.status_code == 200
    assert sorted(list_res.json(), key=lambda x: x["id"]) == sorted(
        [item1, item2], key=lambda x: x["id"]
    )


def test_create_item_with_extra_fields(setup_db):
    res = client.post(
        "/piani-orizzontali/",
        json={"descrizione": "Piano", "anno": 2024},
    )
    piano_id = res.json()["id"]

    item_res = client.post(
        f"/piani-orizzontali/{piano_id}/items",
        json={
            "descrizione": "Segn",
            "quantita": 1,
            "luogo": "Via",
            "data": "2024-05-01",
        },
    )
    assert item_res.status_code == 200
    item = item_res.json()
    assert item["luogo"] == "Via"
    assert item["data"] == "2024-05-01"
