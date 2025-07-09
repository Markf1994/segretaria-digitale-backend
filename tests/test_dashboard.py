from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def auth_user(email: str, nome: str = "Test"):
    resp = client.post(
        "/users/", json={"email": email, "password": "secret", "nome": nome}
    )
    user_id = resp.json()["id"]
    token = client.post("/login", json={"email": email, "password": "secret"}).json()[
        "access_token"
    ]
    return {"Authorization": f"Bearer {token}"}, user_id


def test_dashboard_upcoming(monkeypatch, setup_db):
    headers, _ = auth_user("dash@example.com", nome="Mario")
    other_h, _ = auth_user("other@example.com", nome="Luigi")
    now = datetime.utcnow()

    client.post(
        "/events/",
        json={
            "titolo": "E1",
            "descrizione": "",
            "data_ora": (now + timedelta(days=1)).isoformat(),
            "is_public": True,
        },
        headers=headers,
    )
    client.post(
        "/events/",
        json={
            "titolo": "Late",
            "descrizione": "",
            "data_ora": (now + timedelta(days=8)).isoformat(),
            "is_public": True,
        },
        headers=headers,
    )

    client.post(
        "/todo/",
        json={"descrizione": "T1", "scadenza": (now + timedelta(days=2)).isoformat()},
        headers=headers,
    )
    client.post(
        "/todo/",
        json={
            "descrizione": "Other",
            "scadenza": (now + timedelta(days=1)).isoformat(),
        },
        headers=other_h,
    )

    google_events = [
        {
            "id": "g1",
            "titolo": " 09.00 Mario ",
            "descrizione": "",
            "data_ora": now + timedelta(days=1),
        },
        {
            "id": "g2",
            "titolo": "08:00 Luigi",
            "descrizione": "",
            "data_ora": now + timedelta(days=2),
        },
        {
            "id": "g3",
            "titolo": "Meeting",
            "descrizione": "",
            "data_ora": now + timedelta(days=3),
        },
    ]
    monkeypatch.setattr(
        "app.services.google_calendar.list_upcoming_events", lambda days: google_events
    )

    res = client.get("/dashboard/upcoming?days=5", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 4
    assert [item["kind"] for item in data] == ["event", "google", "todo", "google"]
    times = [item["data_ora"] for item in data]
    assert times == sorted(times)
