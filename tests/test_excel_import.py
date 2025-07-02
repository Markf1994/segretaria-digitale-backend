import os
from pathlib import Path
from unittest.mock import patch

import pandas as pd

from app.services.excel_import import parse_excel, df_to_pdf


def test_parse_excel(tmp_path):
    df = pd.DataFrame([
        {
            "User ID": 1,
            "Data": "2023-01-01",
            "Inizio1": "08:00:00",
            "Fine1": "12:00:00",
            "Tipo": "NORMALE",
            "Note": "n1",
        },
        {
            "User ID": "2",
            "Data": "2023-01-02",
            "Inizio1": "09:00:00",
            "Fine1": "13:00:00",
            "Inizio2": "14:00:00",
            "Fine2": "18:00:00",
            "Inizio3": "19:00:00",
            "Fine3": "21:00:00",
            "Tipo": "EXTRA",
            "Note": "n2",
        },
    ])
    xls = tmp_path / "sample.xlsx"
    df.to_excel(xls, index=False)

    rows = parse_excel(str(xls))

    assert rows == [
        {
            "user_id": "1",
            "giorno": "2023-01-01",
            "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
            "tipo": "NORMALE",
            "note": "n1",
        },
        {
            "user_id": "2",
            "giorno": "2023-01-02",
            "slot1": {"inizio": "09:00:00", "fine": "13:00:00"},
            "slot2": {"inizio": "14:00:00", "fine": "18:00:00"},
            "slot3": {"inizio": "19:00:00", "fine": "21:00:00"},
            "tipo": "EXTRA",
            "note": "n2",
        },
    ]


def test_df_to_pdf_creates_files_and_cleanup(tmp_path):
    rows = [
        {
            "user_id": "1",
            "giorno": "2023-01-01",
            "slot1": {"inizio": "08:00:00", "fine": "12:00:00"},
            "tipo": "NORMALE",
            "note": "",
        }
    ]

    def fake_from_file(html_path, pdf_path):
        Path(pdf_path).write_bytes(b"%PDF-1.4 fake")
        return True

    with patch("app.services.excel_import.pdfkit.from_file", side_effect=fake_from_file):
        pdf_path, html_path = df_to_pdf(rows)

    assert os.path.exists(pdf_path)
    assert os.path.exists(html_path)

    os.remove(pdf_path)
    os.remove(html_path)

    assert not os.path.exists(pdf_path)
    assert not os.path.exists(html_path)
