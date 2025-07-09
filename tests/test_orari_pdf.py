from pathlib import Path
from unittest.mock import patch
import os
from datetime import datetime
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.turno import TipoTurno

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


def test_week_pdf_filters_turni(setup_db, tmp_path):
    headers, user_id = auth_user("week@example.com")

    shift1 = {
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
    shift2 = {
        "user_id": user_id,
        "giorno": "2023-01-08",
        "inizio_1": "09:00:00",
        "fine_1": "13:00:00",
        "inizio_2": None,
        "fine_2": None,
        "inizio_3": None,
        "fine_3": None,
        "tipo": TipoTurno.NORMALE.value,
        "note": "",
    }
    shift3 = {
        "user_id": user_id,
        "giorno": "2023-01-09",
        "inizio_1": "10:00:00",
        "fine_1": "14:00:00",
        "inizio_2": None,
        "fine_2": None,
        "inizio_3": None,
        "fine_3": None,
        "tipo": TipoTurno.NORMALE.value,
        "note": "",
    }

    client.post("/orari/", json=shift1, headers=headers)
    client.post("/orari/", json=shift2, headers=headers)
    client.post("/orari/", json=shift3, headers=headers)

    captured = {}
    real_df_to_pdf = __import__(
        "app.services.excel_import", fromlist=["df_to_pdf"]
    ).df_to_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture_df_to_pdf(rows, db):
        captured["rows"] = rows
        pdf_path, html_path = real_df_to_pdf(rows, db)
        captured["html"] = html_path
        captured["pdf"] = pdf_path
        captured["html_text"] = Path(html_path).read_text()
        return pdf_path, html_path

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch("app.routes.orari.df_to_pdf", side_effect=capture_df_to_pdf):
            res = client.get("/orari/pdf?week=2023-W01", headers=headers)

    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(captured["rows"]) == 2
    days = {r["giorno"] for r in captured["rows"]}
    assert days == {"2023-01-02", "2023-01-08"}
    assert "02/01/2023 – 08/01/2023" in captured["html_text"]
    assert "LUNEDI<br>02/01/2023" in captured["html_text"]
    assert "DOMENICA<br>08/01/2023" in captured["html_text"]
    assert "<th>Test</th>" in captured["html_text"]
    assert "Logo.png" in captured["html_text"]
    assert (
        "COMUNE DI CASTIONE DELLA PRESOLANA – SERVIZIO DI POLIZIA LOCALE"
        in captured["html_text"]
    )


def test_week_pdf_invalid_format(setup_db):
    """Requesting an invalid week string should return a 400 error."""
    headers, _ = auth_user("badweek@example.com")

    res = client.get("/orari/pdf?week=bad", headers=headers)

    assert res.status_code == 400
    assert "Invalid week format" in res.json()["detail"]


def test_week_pdf_temp_files_removed(setup_db, tmp_path):
    """Temporary PDF and HTML files should be cleaned up after the request."""
    headers, user_id = auth_user("clean@example.com")

    shift = {
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

    client.post("/orari/", json=shift, headers=headers)

    captured = {}
    real_df_to_pdf = __import__(
        "app.services.excel_import", fromlist=["df_to_pdf"]
    ).df_to_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture_df_to_pdf(rows, db):
        pdf_path, html_path = real_df_to_pdf(rows, db)
        captured["pdf"] = pdf_path
        captured["html"] = html_path
        captured["html_text"] = Path(html_path).read_text()
        return pdf_path, html_path

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch("app.routes.orari.df_to_pdf", side_effect=capture_df_to_pdf):
            res = client.get("/orari/pdf?week=2023-W01", headers=headers)

    assert res.status_code == 200
    assert "02/01/2023 – 08/01/2023" in captured["html_text"]
    assert "LUNEDI<br>02/01/2023" in captured["html_text"]
    assert "<th>Test</th>" in captured["html_text"]
    assert "Logo.png" in captured["html_text"]
    assert (
        "COMUNE DI CASTIONE DELLA PRESOLANA – SERVIZIO DI POLIZIA LOCALE"
        in captured["html_text"]
    )
    assert not os.path.exists(captured["pdf"])
    assert not os.path.exists(captured["html"])


def test_week_pdf_escapes_html(setup_db, tmp_path):
    headers, user_id = auth_user("escape@example.com", nome="<Agent>")

    shift = {
        "user_id": user_id,
        "giorno": "2023-01-02",
        "inizio_1": "08:00:00",
        "fine_1": "12:00:00",
        "inizio_2": None,
        "fine_2": None,
        "inizio_3": None,
        "fine_3": None,
        "tipo": TipoTurno.NORMALE.value,
        "note": "<b>note</b>",
    }

    client.post("/orari/", json=shift, headers=headers)

    captured = {}
    real_df_to_pdf = __import__(
        "app.services.excel_import", fromlist=["df_to_pdf"]
    ).df_to_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture_df_to_pdf(rows, db):
        pdf_path, html_path = real_df_to_pdf(rows, db)
        captured["html_text"] = Path(html_path).read_text()
        return pdf_path, html_path

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch("app.routes.orari.df_to_pdf", side_effect=capture_df_to_pdf):
            res = client.get("/orari/pdf?week=2023-W01", headers=headers)

    assert res.status_code == 200
    assert "&lt;Agent&gt;" in captured["html_text"]
    assert "&lt;b&gt;note&lt;/b&gt;" in captured["html_text"]
    assert "<Agent>" not in captured["html_text"]
    assert "<b>note</b>" not in captured["html_text"]


def test_week_pdf_includes_gcal_events(setup_db, tmp_path):
    headers, user_id = auth_user("gcal@example.com")

    shift = {
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

    client.post("/orari/", json=shift, headers=headers)

    gcal_events = [
        {
            "id": "ev1",
            "titolo": "Evento",
            "descrizione": "",
            "data_ora": datetime(2023, 1, 2, 10, 0),
        },
        {
            "id": "shift-xyz",
            "titolo": "Turno",
            "descrizione": "",
            "data_ora": datetime(2023, 1, 2, 8, 0),
        },
    ]

    captured = {}
    real_df_to_pdf = __import__("app.services.excel_import", fromlist=["df_to_pdf"]).df_to_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture_df_to_pdf(rows, db):
        pdf_path, html_path = real_df_to_pdf(rows, db)
        captured["html_text"] = Path(html_path).read_text()
        return pdf_path, html_path

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch("app.services.google_calendar.list_events_between", lambda s, e: gcal_events):
            with patch("app.routes.orari.df_to_pdf", side_effect=capture_df_to_pdf):
                res = client.get("/orari/pdf?week=2023-W01", headers=headers)

    assert res.status_code == 200
    assert "<li>Evento</li>" in captured["html_text"]
    assert "Turno" not in captured["html_text"]


def test_week_pdf_ignores_empty_gcal_titles(setup_db, tmp_path):
    headers, user_id = auth_user("gcalnone@example.com")

    shift = {
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

    client.post("/orari/", json=shift, headers=headers)

    gcal_events = [
        {
            "id": "ev1",
            "titolo": None,
            "descrizione": "",
            "data_ora": datetime(2023, 1, 2, 10, 0),
        }
    ]

    captured = {}
    real_df_to_pdf = __import__("app.services.excel_import", fromlist=["df_to_pdf"]).df_to_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture_df_to_pdf(rows, db):
        pdf_path, html_path = real_df_to_pdf(rows, db)
        captured["html_text"] = Path(html_path).read_text()
        return pdf_path, html_path

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch("app.services.google_calendar.list_events_between", lambda s, e: gcal_events):
            with patch("app.routes.orari.df_to_pdf", side_effect=capture_df_to_pdf):
                res = client.get("/orari/pdf?week=2023-W01", headers=headers)

    assert res.status_code == 200
    assert "<li>None</li>" not in captured["html_text"]


def test_week_pdf_includes_public_events(setup_db, tmp_path):
    headers, user_id = auth_user("events@example.com")

    shift = {
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

    client.post("/orari/", json=shift, headers=headers)

    client.post(
        "/events/",
        json={
            "titolo": "Pubblico",
            "descrizione": "",
            "data_ora": "2023-01-02T10:00:00",
            "is_public": True,
        },
        headers=headers,
    )

    client.post(
        "/events/",
        json={
            "titolo": "Privato",
            "descrizione": "",
            "data_ora": "2023-01-02T11:00:00",
            "is_public": False,
        },
        headers=headers,
    )

    captured = {}
    real_df_to_pdf = __import__("app.services.excel_import", fromlist=["df_to_pdf"]).df_to_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture_df_to_pdf(rows, db):
        pdf_path, html_path = real_df_to_pdf(rows, db)
        captured["html_text"] = Path(html_path).read_text()
        return pdf_path, html_path

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch("app.services.google_calendar.list_events_between", lambda s, e: []):
            with patch("app.routes.orari.df_to_pdf", side_effect=capture_df_to_pdf):
                res = client.get("/orari/pdf?week=2023-W01", headers=headers)

    assert res.status_code == 200
    assert "<li>Pubblico</li>" in captured["html_text"]
    assert "Privato" not in captured["html_text"]


def test_week_pdf_strips_emails_from_notes(setup_db, tmp_path):
    headers, user_id = auth_user("emailsnote@example.com")

    shift = {
        "user_id": user_id,
        "giorno": "2023-01-02",
        "inizio_1": "08:00:00",
        "fine_1": "12:00:00",
        "inizio_2": None,
        "fine_2": None,
        "inizio_3": None,
        "fine_3": None,
        "tipo": TipoTurno.NORMALE.value,
        "note": "contattare foo@example.com",
    }

    client.post("/orari/", json=shift, headers=headers)

    captured = {}
    real_df_to_pdf = __import__("app.services.excel_import", fromlist=["df_to_pdf"]).df_to_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture_df_to_pdf(rows, db):
        pdf_path, html_path = real_df_to_pdf(rows, db)
        captured["html_text"] = Path(html_path).read_text()
        return pdf_path, html_path

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch("app.routes.orari.df_to_pdf", side_effect=capture_df_to_pdf):
            res = client.get("/orari/pdf?week=2023-W01", headers=headers)

    assert res.status_code == 200
    assert "foo@example.com" not in captured["html_text"]
    assert "contattare" in captured["html_text"]


def test_week_pdf_strips_emails_from_gcal_and_events(setup_db, tmp_path):
    headers, user_id = auth_user("emailsgcal@example.com")

    shift = {
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

    client.post("/orari/", json=shift, headers=headers)

    gcal_events = [
        {
            "id": "ev1",
            "titolo": "Riunione foo@example.com",
            "descrizione": "",
            "data_ora": datetime(2023, 1, 2, 10, 0),
        }
    ]

    client.post(
        "/events/",
        json={
            "titolo": "Pubblico foo@example.com",
            "descrizione": "",
            "data_ora": "2023-01-02T11:00:00",
            "is_public": True,
        },
        headers=headers,
    )

    captured = {}
    real_df_to_pdf = __import__("app.services.excel_import", fromlist=["df_to_pdf"]).df_to_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture_df_to_pdf(rows, db):
        pdf_path, html_path = real_df_to_pdf(rows, db)
        captured["html_text"] = Path(html_path).read_text()
        return pdf_path, html_path

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch("app.services.google_calendar.list_events_between", lambda s, e: gcal_events):
            with patch("app.routes.orari.df_to_pdf", side_effect=capture_df_to_pdf):
                res = client.get("/orari/pdf?week=2023-W01", headers=headers)

    assert res.status_code == 200
    assert "foo@example.com" not in captured["html_text"]
    assert "Riunione" in captured["html_text"]
    assert "Pubblico" in captured["html_text"]
