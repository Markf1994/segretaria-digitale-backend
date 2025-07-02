import pandas as pd
import pdfkit
import tempfile
from typing import Any


def parse_excel(path: str) -> list[dict[str, Any]]:
    """Parse an Excel file into TurnoIn-compatible payloads."""
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


def df_to_pdf(rows: list[dict[str, Any]]) -> str:
    """Generate a PDF table from row payloads and return its path."""
    df = pd.DataFrame(rows)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_html:
        df.to_html(tmp_html.name, index=False)
        html_path = tmp_html.name
    pdf_path = html_path.replace(".html", ".pdf")
    pdfkit.from_file(html_path, pdf_path)  # requires wkhtmltopdf installed
    return pdf_path
