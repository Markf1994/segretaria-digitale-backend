from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_user(email: str):
    resp = client.post(
        "/users/",
        json={"email": email, "password": "secret", "nome": "Test"},
    )
    user_id = resp.json()["id"]
    token = client.post("/login", json={"email": email, "password": "secret"}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_create_segnalazione(setup_db):
    headers, user_id = auth_user("seg@example.com")
    data = {
        "tipo": "Piante",
        "stato": "aperta",
        "priorita": 1,
        "data_segnalazione": "2024-01-01T10:00:00",
        "descrizione": "Desc",
        "latitudine": 10.0,
        "longitudine": 20.0,
    }
    response = client.post("/segnalazioni/", json=data, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["tipo"] == "Piante"
    assert body["user_id"] == user_id
    assert "id" in body


def test_update_segnalazione(setup_db):
    headers, _ = auth_user("upd@example.com")
    create = client.post(
        "/segnalazioni/",
        json={
            "tipo": "Piante",
            "stato": "aperta",
            "priorita": 1,
            "data_segnalazione": "2024-01-01T10:00:00",
            "descrizione": "Old",
            "latitudine": 1.0,
            "longitudine": 2.0,
        },
        headers=headers,
    )
    seg_id = create.json()["id"]
    response = client.put(
        f"/segnalazioni/{seg_id}",
        json={
            "tipo": "Danneggiamenti",
            "stato": "in lavorazione",
            "priorita": 2,
            "data_segnalazione": "2024-02-01T12:00:00",
            "descrizione": "New",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["stato"] == "in lavorazione"


def test_get_segnalazione(setup_db):
    headers, _ = auth_user("get@example.com")
    res = client.post(
        "/segnalazioni/",
        json={
            "tipo": "Piante",
            "stato": "aperta",
            "priorita": 1,
            "data_segnalazione": "2024-01-01T10:00:00",
            "descrizione": "Desc",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=headers,
    )
    seg_id = res.json()["id"]
    get_res = client.get(f"/segnalazioni/{seg_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == seg_id


def test_patch_stato(setup_db):
    headers, _ = auth_user("patchstato@example.com")
    res = client.post(
        "/segnalazioni/",
        json={
            "tipo": "Piante",
            "stato": "aperta",
            "priorita": 1,
            "data_segnalazione": "2024-01-01T10:00:00",
            "descrizione": "ToPatch",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=headers,
    )
    seg_id = res.json()["id"]
    patch_res = client.patch(
        f"/segnalazioni/{seg_id}",
        json={"stato": "chiusa"},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["stato"] == "chiusa"
    assert patch_res.json()["priorita"] == 1


def test_patch_priorita(setup_db):
    headers, _ = auth_user("patchprio@example.com")
    res = client.post(
        "/segnalazioni/",
        json={
            "tipo": "Piante",
            "stato": "aperta",
            "priorita": 1,
            "data_segnalazione": "2024-01-01T10:00:00",
            "descrizione": "ToPatch",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=headers,
    )
    seg_id = res.json()["id"]
    patch_res = client.patch(
        f"/segnalazioni/{seg_id}",
        json={"priorita": 2},
        headers=headers,
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["priorita"] == 2


def test_list_segnalazioni(setup_db):
    headers, _ = auth_user("list@example.com")
    client.post(
        "/segnalazioni/",
        json={
            "tipo": "Piante",
            "stato": "aperta",
            "priorita": 1,
            "data_segnalazione": "2024-01-01T10:00:00",
            "descrizione": "A",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=headers,
    )
    client.post(
        "/segnalazioni/",
        json={
            "tipo": "Danneggiamenti",
            "stato": "chiusa",
            "priorita": 2,
            "data_segnalazione": "2024-02-01T10:00:00",
            "descrizione": "B",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=headers,
    )
    res = client.get("/segnalazioni/", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_delete_segnalazione(setup_db):
    headers, _ = auth_user("del@example.com")
    res = client.post(
        "/segnalazioni/",
        json={
            "tipo": "Piante",
            "stato": "aperta",
            "priorita": 1,
            "data_segnalazione": "2024-01-01T10:00:00",
            "descrizione": "Del",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=headers,
    )
    seg_id = res.json()["id"]
    response = client.delete(f"/segnalazioni/{seg_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["ok"] is True
    assert client.get("/segnalazioni/", headers=headers).json() == []


def test_user_isolated_segnalazioni(setup_db):
    h1, id1 = auth_user("u1@example.com")
    h2, id2 = auth_user("u2@example.com")

    client.post(
        "/segnalazioni/",
        json={
            "tipo": "Piante",
            "stato": "aperta",
            "priorita": 1,
            "data_segnalazione": "2024-01-01T10:00:00",
            "descrizione": "U1",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=h1,
    )
    client.post(
        "/segnalazioni/",
        json={
            "tipo": "Piante",
            "stato": "aperta",
            "priorita": 1,
            "data_segnalazione": "2024-02-01T10:00:00",
            "descrizione": "U2",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=h2,
    )
    client.post(
        "/segnalazioni/",
        json={
            "tipo": "Piante",
            "stato": "aperta",
            "priorita": 1,
            "data_segnalazione": "2024-03-01T10:00:00",
            "descrizione": "U1B",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=h1,
    )

    res1 = client.get("/segnalazioni/", headers=h1)
    res2 = client.get("/segnalazioni/", headers=h2)

    assert len(res1.json()) == 2
    assert len(res2.json()) == 1
    assert all(s["user_id"] == id1 for s in res1.json())
    assert all(s["user_id"] == id2 for s in res2.json())


def test_list_by_stato(setup_db):
    headers, _ = auth_user("filter@example.com")

    client.post(
        "/segnalazioni/",
        json={
            "tipo": "Piante",
            "stato": "aperta",
            "priorita": 1,
            "data_segnalazione": "2024-01-01T10:00:00",
            "descrizione": "A",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=headers,
    )
    client.post(
        "/segnalazioni/",
        json={
            "tipo": "Piante",
            "stato": "in lavorazione",
            "priorita": 2,
            "data_segnalazione": "2024-02-01T10:00:00",
            "descrizione": "B",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=headers,
    )
    client.post(
        "/segnalazioni/",
        json={
            "tipo": "Piante",
            "stato": "chiusa",
            "priorita": 3,
            "data_segnalazione": "2024-03-01T10:00:00",
            "descrizione": "C",
            "latitudine": 0.0,
            "longitudine": 0.0,
        },
        headers=headers,
    )

    res = client.get(
        "/segnalazioni/by-stato",
        params={"stato": "aperta,in lavorazione"},
        headers=headers,
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert {s["stato"] for s in data} == {"aperta", "in lavorazione"}
