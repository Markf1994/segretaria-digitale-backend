from fastapi.testclient import TestClient
from pathlib import Path
from unittest.mock import patch
import os
import datetime

from app.main import app

client = TestClient(app)


def test_create_signage_horizontal(setup_db):
    data = {"azienda": "ACME", "descrizione": "Linea"}
    res = client.post("/inventario/signage-horizontal/", json=data)
    assert res.status_code == 200
    body = res.json()
    assert body["azienda"] == "ACME"
    assert body["descrizione"] == "Linea"
    assert body["anno"] == datetime.date.today().year
    assert "id" in body


def test_update_signage_horizontal(setup_db):
    base = {"azienda": "ACME", "descrizione": "Old"}
    res = client.post("/inventario/signage-horizontal/", json=base)
    rec_id = res.json()["id"]
    year = res.json()["anno"]
    update = {"azienda": "Beta", "descrizione": "New"}
    res = client.put(f"/inventario/signage-horizontal/{rec_id}", json=update)
    assert res.status_code == 200
    data = res.json()
    assert data["azienda"] == "Beta"
    assert data["descrizione"] == "New"
    assert data["anno"] == year


def test_list_signage_horizontal(setup_db):
    client.post(
        "/inventario/signage-horizontal/",
        json={"azienda": "A", "descrizione": "A", "anno": 2023},
    )
    client.post(
        "/inventario/signage-horizontal/",
        json={"azienda": "B", "descrizione": "B", "anno": 2024},
    )

    res = client.get("/inventario/signage-horizontal/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2

    res = client.get("/inventario/signage-horizontal/?year=2023")
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["anno"] == 2023


def test_delete_signage_horizontal(setup_db):
    res = client.post(
        "/inventario/signage-horizontal/",
        json={"azienda": "C", "descrizione": "C", "anno": 2022},
    )
    rec_id = res.json()["id"]
    del_res = client.delete(f"/inventario/signage-horizontal/{rec_id}")
    assert del_res.status_code == 200
    assert del_res.json()["ok"] is True
    assert client.get("/inventario/signage-horizontal/").json() == []


def test_get_years(setup_db):
    client.post(
        "/inventario/signage-horizontal/",
        json={"azienda": "A", "descrizione": "A", "anno": 2022},
    )
    client.post(
        "/inventario/signage-horizontal/",
        json={"azienda": "B", "descrizione": "B", "anno": 2024},
    )
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

    with patch("weasyprint_stub.HTML.write_pdf", side_effect=fake_write_pdf):
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

    with patch("weasyprint_stub.HTML.write_pdf", side_effect=fake_write_pdf):
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


def test_import_signage_horizontal_creates_records_and_returns_pdf(setup_db, tmp_path):
    captured = {}

    def fake_parse(path):
        captured["xlsx"] = path
        return [
            {"azienda": "A", "descrizione": "One", "anno": 2024},
            {"azienda": "A", "descrizione": "Two", "anno": 2024},
        ]

    def fake_build(db, year):
        pdf = tmp_path / "plan.pdf"
        html = tmp_path / "plan.html"
        pdf.write_bytes(b"%PDF-1.4 fake")
        html.write_text("x")
        captured["pdf"] = str(pdf)
        captured["html"] = str(html)
        return str(pdf), str(html)

    with patch("app.routes.signage_horizontal.parse_file", side_effect=fake_parse):
        with patch(
            "app.routes.signage_horizontal.build_segnaletica_orizzontale_pdf",
            side_effect=fake_build,
        ):
            dummy = tmp_path / "imp.xlsx"
            dummy.write_bytes(b"data")
            with open(dummy, "rb") as fh:
                res = client.post(
                    "/inventario/signage-horizontal/import",
                    files={
                        "file": (
                            "imp.xlsx",
                            fh,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
                    },
                )

    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert not os.path.exists(captured["xlsx"])
    assert not os.path.exists(captured["pdf"])
    assert not os.path.exists(captured["html"])
    assert len(client.get("/inventario/signage-horizontal/").json()) == 2


def test_import_signage_horizontal_parse_error_returns_400(tmp_path):
    captured = {}

    def fake_parse(path):
        captured["xlsx"] = path
        raise HTTPException(status_code=400, detail="bad")

    with patch("app.routes.signage_horizontal.parse_file", side_effect=fake_parse):
        dummy = tmp_path / "imp.xlsx"
        dummy.write_bytes(b"data")
        with open(dummy, "rb") as fh:
            res = client.post(
                "/inventario/signage-horizontal/import",
                files={
                    "file": (
                        "imp.xlsx",
                        fh,
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                },
            )

    assert res.status_code == 400
    assert not os.path.exists(captured["xlsx"])


def test_import_signage_horizontal_tmp_removed_on_late_failure(tmp_path):
    captured = {}

    def fake_parse(path):
        captured["xlsx"] = path
        return [{"azienda": "A", "descrizione": "X", "anno": 2024}]

    with patch("app.routes.signage_horizontal.parse_file", side_effect=fake_parse):
        with patch(
            "app.routes.signage_horizontal.crud.create_segnaletica_orizzontale",
            side_effect=RuntimeError("boom"),
        ):
            dummy = tmp_path / "imp.xlsx"
            dummy.write_bytes(b"data")
            with open(dummy, "rb") as fh:
                res = client.post(
                    "/inventario/signage-horizontal/import",
                    files={
                        "file": (
                            "imp.xlsx",
                            fh,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
                    },
                )

    assert res.status_code == 500
    assert not os.path.exists(captured["xlsx"])


