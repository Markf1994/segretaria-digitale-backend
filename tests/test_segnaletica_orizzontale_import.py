import pandas as pd
import pytest
from fastapi import HTTPException
from app.services.segnaletica_orizzontale_import import parse_excel


def test_parse_excel_valid(tmp_path):
    df = pd.DataFrame([
        {"azienda": "ACME", "descrizione": "Linea"},
        {"azienda": "ACME", "descrizione": "Stop"},
    ])
    xls = tmp_path / "segna.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls))

    assert rows == [
        {"azienda": "ACME", "descrizione": "Linea"},
        {"azienda": "ACME", "descrizione": "Stop"},
    ]


def test_parse_excel_missing_column(tmp_path):
    df = pd.DataFrame([
        {"azienda": "ACME"},
    ])
    xls = tmp_path / "bad.xlsx"
    df.to_excel(xls, index=False)

    with pytest.raises(HTTPException) as exc:
        parse_excel(str(xls))

    assert exc.value.status_code == 400
    assert "Missing columns" in exc.value.detail
