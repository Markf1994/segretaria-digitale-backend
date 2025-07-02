import pandas as pd
import pdfkit
import tempfile
import os
from typing import List, Dict, Any


def parse_excel(path: str) -> List[Dict[str, Any]]:
    """Parse an Excel file into TurnoIn-compatible payloads.

    Colonne obbligatorie / Required columns: ``Data``, ``User ID``,
    ``Inizio1`` e ``Fine1``. Colonne facoltative / Optional: ``Inizio2``,
    ``Fine2``, ``Inizio3``, ``Fine3``, ``Tipo`` e ``Note``.

    :return: a list of dictionaries ready for the TurnoIn API.
    """
    df = pd.read_excel(path)  # requires openpyxl
    rows: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        payload: dict[str, Any] = {
            "user_id": str(row["User ID"]),
            "giorno": row["Data"].date() if hasattr(row["Data"], "date") else row["Data"],
            "slot1": {"inizio": row["Inizio1"], "fine": row["Fine1"]},
            "tipo": row.get("Tipo", "NORMALE"),
            "note": row.get("Note", ""),
        }
        if not pd.isna(row.get("Inizio2")) and not pd.isna(row.get("Fine2")):
            payload["slot2"] = {"inizio": row["Inizio2"], "fine": row["Fine2"]}
        if not pd.isna(row.get("Inizio3")) and not pd.isna(row.get("Fine3")):
            payload["slot3"] = {"inizio": row["Inizio3"], "fine": row["Fine3"]}
        rows.append(payload)
    return rows


def df_to_pdf(rows: List[Dict[str, Any]]) -> str:
    """Generate a PDF table from row payloads and return its path."""
    df = pd.DataFrame(rows)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_html:
        df.to_html(tmp_html.name, index=False)
        html_path = tmp_html.name
    pdf_path = html_path.replace(".html", ".pdf")
    try:
        pdfkit.from_file(html_path, pdf_path)  # requires wkhtmltopdf installed
    finally:
        os.remove(html_path)
    return pdf_path
