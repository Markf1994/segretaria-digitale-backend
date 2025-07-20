from fastapi.testclient import TestClient
from pathlib import Path
from unittest.mock import patch
import os

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


def test_plan_pdf_single_azienda(setup_db, tmp_path):
    client.post(
        "/inventario/signage-horizontal/",
        json={"azienda": "Solo", "descrizione": "Linea 1", "anno": 2024},
    )
    client.post(
        "/inventario/signage-horizontal/",
        json={"azienda": "Solo", "descrizione": "Linea 2", "anno": 2024},
    )

    captured = {}
    real_build = __import__(
        "app.services.segnaletica_orizzontale_pdf",
        fromlist=["build_segnaletica_orizzontale_pdf"],
    ).build_segnaletica_orizzontale_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture_build(db, year):
        pdf_path, html_path = real_build(db, year)
        captured["pdf"] = pdf_path
        captured["html"] = html_path
        captured["text"] = Path(html_path).read_text()
        return pdf_path, html_path

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch(
            "app.routes.signage_horizontal.build_segnaletica_orizzontale_pdf",
            side_effect=capture_build,
        ):
            res = client.get("/inventario/signage-horizontal/pdf?year=2024")

    assert res.status_code == 200
    assert "Linea 1" in captured["text"]
    assert "Linea 2" in captured["text"]
    assert "Solo" in captured["text"]
    assert "Logo.png" in captured["text"]
    assert not os.path.exists(captured["pdf"])
    assert not os.path.exists(captured["html"])


def test_plan_pdf_multiple_aziende(setup_db, tmp_path):
    client.post(
        "/inventario/signage-horizontal/",
        json={"azienda": "A", "descrizione": "Desc", "anno": 2023},
    )
    client.post(
        "/inventario/signage-horizontal/",
        json={"azienda": "B", "descrizione": "Other", "anno": 2023},
    )

    captured = {}
    real_build = __import__(
        "app.services.segnaletica_orizzontale_pdf",
        fromlist=["build_segnaletica_orizzontale_pdf"],
    ).build_segnaletica_orizzontale_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture_build(db, year):
        pdf_path, html_path = real_build(db, year)
        captured["text"] = Path(html_path).read_text()
        captured["pdf"] = pdf_path
        captured["html"] = html_path
        return pdf_path, html_path

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch(
            "app.routes.signage_horizontal.build_segnaletica_orizzontale_pdf",
            side_effect=capture_build,
        ):
            res = client.get("/inventario/signage-horizontal/pdf?year=2023")

    assert res.status_code == 200
    assert "Desc" in captured["text"]
    assert "Other" in captured["text"]
    assert "A" not in captured["text"] or "B" not in captured["text"]
    assert not os.path.exists(captured["pdf"])
    assert not os.path.exists(captured["html"])
