from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_inventory_pdf_from_db(setup_db, tmp_path):
    # create a plan with items for year 2023
    res = client.post("/piani-orizzontali/", json={"descrizione": "Piano", "anno": 2023})
    piano_id = res.json()["id"]
    client.post(f"/piani-orizzontali/{piano_id}/items", json={"descrizione": "Segnale", "quantita": 2})
    client.post(f"/piani-orizzontali/{piano_id}/items", json={"descrizione": "Segnale", "quantita": 3})
    client.post(f"/piani-orizzontali/{piano_id}/items", json={"descrizione": "Altro", "quantita": 1})

    captured = {}
    real_func = __import__("app.services.inventory_pdf", fromlist=["build_inventory_pdf"]).build_inventory_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture(items, year):
        captured["items"] = items
        pdf_path, html_path = real_func(items, year)
        captured["html"] = html_path
        captured["pdf"] = pdf_path
        captured["html_text"] = Path(html_path).read_text()
        return pdf_path, html_path

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch("app.routes.inventory.build_inventory_pdf", side_effect=capture):
            res = client.get("/inventory/pdf?year=2023")

    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert sorted(captured["items"], key=lambda x: x["name"]) == [
        {"name": "Altro", "count": 1},
        {"name": "Segnale", "count": 5},
    ]
    assert "Inventario 2023" in captured["html_text"]
