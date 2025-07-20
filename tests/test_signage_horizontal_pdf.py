from fastapi.testclient import TestClient
from pathlib import Path
from unittest.mock import patch
import os

from app.main import app

client = TestClient(app)


def create_record(descr: str, anno: int, azienda: str = "ACME"):  # new helper
    """Create a SegnaleticaOrizzontale entry used by the inventory tests."""
    client.post(
        "/segnaletica-orizzontale/",
        json={"azienda": azienda, "descrizione": descr, "anno": anno},
    )


def test_signage_horizontal_pdf_aggregates_items(setup_db, tmp_path):
    # create records for the requested year
    for _ in range(2):
        create_record("Linee", 2023)
    for _ in range(3):
        create_record("Linee", 2023)
    create_record("Stop", 2023)

    # add some data for other years that should be ignored
    create_record("Stop", 2022)

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
    create_record("First", 2020)
    create_record("Second", 2023)
    create_record("Third", 2023)

    res = client.get("/inventario/signage-horizontal/years")
    assert res.status_code == 200
    assert res.json() == [2020, 2023]


def test_signage_horizontal_items(setup_db):
    for _ in range(5):
        create_record("Linee", 2023)
    create_record("Stop", 2023)
    create_record("Stop", 2022)

    res = client.get("/inventario/signage-horizontal/?year=2023")
    assert res.status_code == 200
    assert sorted(res.json(), key=lambda x: x["name"]) == [
        {"name": "Linee", "count": 5},
        {"name": "Stop", "count": 1},
    ]
