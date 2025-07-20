from fastapi.testclient import TestClient
from pathlib import Path
from unittest.mock import patch
import os

from app.main import app

client = TestClient(app)


def create_piano(descr, anno):
    res = client.post("/piani-orizzontali/", json={"descrizione": descr, "anno": anno})
    return res.json()["id"]


def add_item(piano_id, descr, qty):
    client.post(
        f"/piani-orizzontali/{piano_id}/items",
        json={"descrizione": descr, "quantita": qty},
    )


def test_signage_horizontal_pdf_aggregates_items(setup_db, tmp_path):
    p1 = create_piano("P1", 2023)
    p2 = create_piano("P2", 2023)
    p_old = create_piano("Old", 2022)

    add_item(p1, "Linee", 2)
    add_item(p2, "Linee", 3)
    add_item(p1, "Stop", 1)
    add_item(p_old, "Stop", 5)

    captured = {}
    real_build = __import__(
        "app.services.inventory_pdf", fromlist=["build_inventory_pdf"]
    ).build_inventory_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture_build(items, year):
        pdf_path, html_path = real_build(items, year)
        captured["items"] = items
        captured["pdf"] = pdf_path
        captured["html"] = html_path
        captured["html_text"] = Path(html_path).read_text()
        return pdf_path, html_path

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch(
            "app.services.signage_horizontal.build_inventory_pdf",
            side_effect=capture_build,
        ):
            res = client.get("/inventario/signage-horizontal/pdf?year=2023")

    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert sorted(captured["items"], key=lambda x: x["name"]) == [
        {"name": "Linee", "count": 5},
        {"name": "Stop", "count": 1},
    ]
    assert "Inventario 2023" in captured["html_text"]
    assert "Linee" in captured["html_text"]
    assert "5" in captured["html_text"]
    assert not os.path.exists(captured["pdf"])
    assert not os.path.exists(captured["html"])


def test_signage_horizontal_years(setup_db):
    create_piano("First", 2020)
    create_piano("Second", 2023)
    create_piano("Third", 2023)

    res = client.get("/inventario/signage-horizontal/years")
    assert res.status_code == 200
    assert res.json() == [2020, 2023]


def test_signage_horizontal_items(setup_db):
    p1 = create_piano("P1", 2023)
    p2 = create_piano("P2", 2023)
    old = create_piano("Old", 2022)

    add_item(p1, "Linee", 2)
    add_item(p2, "Linee", 3)
    add_item(p1, "Stop", 1)
    add_item(old, "Stop", 5)

    res = client.get("/inventario/signage-horizontal/?year=2023")
    assert res.status_code == 200
    assert sorted(res.json(), key=lambda x: x["name"]) == [
        {"name": "Linee", "count": 5},
        {"name": "Stop", "count": 1},
    ]
