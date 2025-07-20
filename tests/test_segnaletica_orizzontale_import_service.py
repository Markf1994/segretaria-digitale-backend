import os
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest
from fastapi import HTTPException

from app.database import SessionLocal
from app.schemas.segnaletica_orizzontale import SegnaleticaOrizzontaleCreate
from app.crud import segnaletica_orizzontale as crud
from app.services.segnaletica_orizzontale_import import parse_excel
from app.services.segnaletica_orizzontale_pdf import build_segnaletica_orizzontale_pdf


def test_parse_and_pdf_generation(setup_db, tmp_path):
    df = pd.DataFrame([
        {"azienda": "ACME", "descrizione": "Linea"},
        {"azienda": "ACME", "descrizione": "Stop"},
    ])
    xls = tmp_path / "imp.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls))

    db = SessionLocal()
    for row in rows:
        crud.create_segnaletica_orizzontale(db, SegnaleticaOrizzontaleCreate(**row))

    def fake_write_pdf(self, target, *args, **kwargs):
        Path(target).write_bytes(b"%PDF-1.4 fake")

    with patch("weasyprint_stub.HTML.write_pdf", side_effect=fake_write_pdf):
        pdf_path, html_path = build_segnaletica_orizzontale_pdf(db, date.today().year)

    html_text = Path(html_path).read_text()
    assert "ACME" in html_text
    assert "Linea" in html_text
    assert "Stop" in html_text
    assert "Logo.png" in html_text

    os.remove(pdf_path)
    os.remove(html_path)
    assert not os.path.exists(pdf_path)
    assert not os.path.exists(html_path)

    records = crud.get_segnaletica_orizzontale(db)
    assert len(records) == 2
    db.close()


def test_parse_excel_missing_column(tmp_path):
    df = pd.DataFrame([{"azienda": "ACME"}])
    xls = tmp_path / "bad.xlsx"
    df.to_excel(xls, index=False)

    with pytest.raises(HTTPException) as exc:
        parse_excel(str(xls))

    assert exc.value.status_code == 400
    assert "Missing columns" in exc.value.detail


def test_parse_excel_empty_cells(tmp_path):
    df = pd.DataFrame([
        {"azienda": "", "descrizione": "Segno"},
        {"azienda": "ACME", "descrizione": ""},
    ])
    xls = tmp_path / "empty.xlsx"
    df.to_excel(xls, index=False)

    with pytest.raises(HTTPException) as exc:
        parse_excel(str(xls))

    assert exc.value.status_code == 400
    assert "Row 2" in exc.value.detail or "Row 3" in exc.value.detail

