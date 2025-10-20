from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.schemas.turno import TipoTurno

from app.main import app

client = TestClient(app)


def auth_user(email: str, nome: str = "Test"):
    resp = client.post(
        "/users/", json={"email": email, "password": "secret", "nome": nome}
    )
    user_id = resp.json()["id"]
    token = client.post(
        "/login",
        json={"email": email, "password": "secret"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_create_turno(setup_db):
    headers, user_id = auth_user("shift@example.com")
    data = {
        "user_id": user_id,
        "giorno": "2023-01-01",
        "inizio_1": "08:00:00",
        "fine_1": "12:00:00",
        "inizio_2": "13:00:00",
        "fine_2": "17:00:00",
        "inizio_3": None,
        "fine_3": None,
        "tipo": TipoTurno.NORMALE.value,
        "note": "test",
    }
    res = client.post("/orari/", json=data, headers=headers)
    assert res.status_code == 200
    body = res.json()
    assert body["user_id"] == user_id
    assert body["giorno"] == "2023-01-01"
    assert body["inizio_1"] == "08:00:00"
    assert body["fine_1"] == "12:00:00"
    assert body["inizio_2"] == "13:00:00"
    assert body["fine_2"] == "17:00:00"
    assert body["inizio_3"] is None
    assert body["fine_3"] is None


def test_update_turno(setup_db):
    headers, user_id = auth_user("update@example.com")
    base = {
        "user_id": user_id,
        "giorno": "2023-01-02",
        "inizio_1": "08:00:00",
        "fine_1": "12:00:00",
        "inizio_2": None,
        "fine_2": None,
        "inizio_3": None,
        "fine_3": None,
        "tipo": TipoTurno.NORMALE.value,
        "note": "",
    }
    first = client.post("/orari/", json=base, headers=headers)
    turno_id = first.json()["id"]
    base["inizio_1"] = "09:00:00"
    base["fine_1"] = "13:00:00"
    base["tipo"] = TipoTurno.STRAORD.value
    update = client.post("/orari/", json=base, headers=headers)
    assert update.status_code == 200
    updated = update.json()
    assert updated["id"] == turno_id
    assert updated["inizio_1"] == "09:00:00"
    assert updated["fine_1"] == "13:00:00"
    assert updated["tipo"] == "STRAORD"


def test_delete_turno(setup_db):
    headers, user_id = auth_user("delete@example.com")
    data = {
        "user_id": user_id,
        "giorno": "2023-01-03",
        "inizio_1": "08:00:00",
        "fine_1": "12:00:00",
        "inizio_2": None,
        "fine_2": None,
        "inizio_3": None,
        "fine_3": None,
        "tipo": TipoTurno.NORMALE.value,
        "note": "",
    }
    res = client.post("/orari/", json=data, headers=headers)
    turno_id = res.json()["id"]
    del_res = client.delete(f"/orari/{turno_id}", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["ok"] is True
    list_res = client.get("/orari/", headers=headers)
    assert list_res.status_code == 200
    assert list_res.json() == []


def test_shift_event_summary_email(setup_db):
    headers, user_id = auth_user("cal@example.com", nome="Calendar User")

    captured = {}

    class DummyClient:
        def events(self):
            class Events:
                def update(self, calendarId=None, eventId=None, body=None):
                    captured["body"] = body
                    return MagicMock(execute=MagicMock())

            return Events()

    with patch("app.services.gcal.get_client", return_value=DummyClient()):
        client.post(
            "/orari/",
            json={
                "user_id": user_id,
                "giorno": "2023-05-05",
                "inizio_1": "08:00:00",
                "fine_1": "12:00:00",
                "inizio_2": None,
                "fine_2": None,
                "inizio_3": None,
                "fine_3": None,
                "tipo": TipoTurno.NORMALE.value,
                "note": "",
            },
            headers=headers,
        )

    assert captured["body"]["summary"] == "Turno Calendar User"


def test_shift_event_summary_short_name(setup_db):
    headers, user_id = auth_user(
        "marco@comune.castione.bg.it", nome="Ag.Sc. Fenaroli Marco"
    )

    captured = {}

    class DummyClient:
        def events(self):
            class Events:
                def update(self, calendarId=None, eventId=None, body=None):
                    captured["body"] = body
                    return MagicMock(execute=MagicMock())

            return Events()

    with patch("app.services.gcal.get_client", return_value=DummyClient()):
        client.post(
            "/orari/",
            json={
                "user_id": user_id,
                "giorno": "2023-05-05",
                "inizio_1": "08:00:00",
                "fine_1": "12:00:00",
                "inizio_2": None,
                "fine_2": None,
                "inizio_3": None,
                "fine_3": None,
                "tipo": TipoTurno.NORMALE.value,
                "note": "",
            },
            headers=headers,
        )

    assert captured["body"]["summary"] == "Turno Ag.Sc. Fenaroli Marco"


def test_create_turno_unknown_user_returns_400(setup_db):
    headers, _ = auth_user("u@example.com")

    data = {
        "user_id": "unknown-id",
        "giorno": "2023-06-01",
        "inizio_1": "08:00:00",
        "fine_1": "12:00:00",
        "inizio_2": None,
        "fine_2": None,
        "inizio_3": None,
        "fine_3": None,
        "tipo": TipoTurno.NORMALE.value,
        "note": "",
    }

    res = client.post("/orari/", json=data, headers=headers)
    assert res.status_code == 400
    assert res.json()["detail"] == "Unknown user"


def test_create_turno_day_off_allows_missing_times(setup_db):
    headers, user_id = auth_user("dayoff@example.com")
    data = {
        "user_id": user_id,
        "giorno": "2023-12-25",
        "inizio_1": None,
        "fine_1": None,
        "inizio_2": None,
        "fine_2": None,
        "inizio_3": None,
        "fine_3": None,
        "tipo": TipoTurno.RECUPERO.value,
        "note": "",
    }

    with patch("app.services.gcal.sync_shift_event") as fake_sync:
        res = client.post("/orari/", json=data, headers=headers)
    assert res.status_code == 200
    fake_sync.assert_not_called()
    body = res.json()
    assert body["inizio_1"] is None
    assert body["fine_1"] is None


def test_create_turno_recupero_skips_gcal_sync(setup_db):
    """Creating a RECUPERO turno should not trigger calendar sync."""
    headers, user_id = auth_user("recupero@example.com")
    data = {
        "user_id": user_id,
        "giorno": "2023-12-26",
        "inizio_1": None,
        "fine_1": None,
        "inizio_2": None,
        "fine_2": None,
        "inizio_3": None,
        "fine_3": None,
        "tipo": "RECUPERO",
        "note": "",
    }

    with patch("app.services.gcal.sync_shift_event") as fake_sync:
        res = client.post("/orari/", json=data, headers=headers)

    assert res.status_code == 200
    fake_sync.assert_not_called()
    payload = res.json()
    assert payload["tipo"] == "RECUPERO"


def test_delete_turno_calls_gcal(setup_db):
    """Deleting a turno should remove the matching Google Calendar event."""
    headers, user_id = auth_user("gcaldelete@example.com")
    data = {
        "user_id": user_id,
        "giorno": "2024-01-01",
        "inizio_1": "08:00:00",
        "fine_1": "12:00:00",
        "inizio_2": None,
        "fine_2": None,
        "inizio_3": None,
        "fine_3": None,
        "tipo": TipoTurno.NORMALE.value,
        "note": "",
    }

    res = client.post("/orari/", json=data, headers=headers)
    turno_id = res.json()["id"]

    with patch("app.services.gcal.delete_shift_event") as fake_delete:
        del_res = client.delete(f"/orari/{turno_id}", headers=headers)

    assert del_res.status_code == 200
    fake_delete.assert_called_once_with(turno_id)


def test_delete_turno_day_off_skips_gcal(setup_db):
    """Day-off turni should not trigger calendar deletion."""
    headers, user_id = auth_user("dayoffdel@example.com")
    data = {
        "user_id": user_id,
        "giorno": "2024-02-01",
        "inizio_1": None,
        "fine_1": None,
        "inizio_2": None,
        "fine_2": None,
        "inizio_3": None,
        "fine_3": None,
        "tipo": TipoTurno.RECUPERO.value,
        "note": "",
    }

    res = client.post("/orari/", json=data, headers=headers)
    turno_id = res.json()["id"]

    with patch("app.services.gcal.delete_shift_event") as fake_delete:
        del_res = client.delete(f"/orari/{turno_id}", headers=headers)

    assert del_res.status_code == 200
    fake_delete.assert_not_called()


def test_delete_turno_invalid_id_skips_gcal(setup_db):
    """Deleting a non-existent turno should not call Google Calendar."""
    headers, _ = auth_user("missing@example.com")
    fake_id = "11111111-1111-1111-1111-111111111111"

    with patch("app.services.gcal.delete_shift_event") as fake_delete:
        res = client.delete(f"/orari/{fake_id}", headers=headers)

    assert res.status_code == 404
    fake_delete.assert_not_called()
