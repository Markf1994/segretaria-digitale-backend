from pathlib import Path
from datetime import date
from fastapi.testclient import TestClient
from unittest.mock import patch
import os
import pandas as pd

from app.main import app

client = TestClient(app)


def test_import_excel_creates_records_and_pdf(setup_db, tmp_path):
    df = pd.DataFrame([
        {"azienda": "ACME", "descrizione": "Linea"},
        {"azienda": "ACME", "descrizione": "Stop"},
    ])
    xlsx = tmp_path / "segna.xlsx"
    df.to_excel(xlsx, index=False)

    captured = {}
    real_build = __import__(
        "app.services.segnaletica_orizzontale_pdf",
        fromlist=["build_segnaletica_orizzontale_pdf"],
    ).build_segnaletica_orizzontale_pdf

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    def capture(descrizioni, azienda, year):
        pdf, html = real_build(descrizioni, azienda, year)
        captured["pdf"] = pdf
        captured["html"] = html
        captured["html_text"] = Path(html).read_text()
        captured["descrizioni"] = descrizioni
        captured["azienda"] = azienda
        captured["year"] = year
        return pdf, html

    with patch("weasyprint.HTML.write_pdf", side_effect=fake_write_pdf):
        with patch(
            "app.routes.segnaletica_orizzontale.build_segnaletica_orizzontale_pdf",
            side_effect=capture,
        ):
            with open(xlsx, "rb") as fh:
                res = client.post(
                    "/segnaletica-orizzontale/import",
                    files={
                        "file": (
                            "segna.xlsx",
                            fh,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
                    },
                )
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"

    list_res = client.get("/segnaletica-orizzontale/")
    records = list_res.json()
    assert len(records) == 2
    assert all(r["anno"] == date.today().year for r in records)

    assert captured["descrizioni"] == ["Linea", "Stop"]
    assert f"Piano Segnaletica Orizzontale Anno {date.today().year}" in captured["html_text"]
    assert "ACME" in captured["html_text"]
    assert "Linea" in captured["html_text"]
    assert "Stop" in captured["html_text"]
    assert not os.path.exists(captured["pdf"])
    assert not os.path.exists(captured["html"])


def test_import_temp_files_removed(setup_db, tmp_path):
    captured = {}

    def fake_parse(path):
        captured["xlsx"] = path
        return [{"azienda": "A", "descrizione": "B", "anno": date.today().year}]

    def fake_build(rows, azienda, year):
        pdf = tmp_path / "out.pdf"
        html = tmp_path / "out.html"
        pdf.write_bytes(b"%PDF-1.4 fake")
        html.write_text("html")
        captured["pdf"] = str(pdf)
        captured["html"] = str(html)
        return str(pdf), str(html)

    with patch("app.routes.segnaletica_orizzontale.parse_excel", side_effect=fake_parse):
        with patch(
            "app.routes.segnaletica_orizzontale.build_segnaletica_orizzontale_pdf",
            side_effect=fake_build,
        ):
            dummy = tmp_path / "s.xlsx"
            dummy.write_bytes(b"data")
            with open(dummy, "rb") as fh:
                res = client.post(
                    "/segnaletica-orizzontale/import",
                    files={
                        "file": (
                            "s.xlsx",
                            fh,
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )
                    },
                )
    assert res.status_code == 200
    assert not os.path.exists(captured["xlsx"])
    assert not os.path.exists(captured["pdf"])
    assert not os.path.exists(captured["html"])
