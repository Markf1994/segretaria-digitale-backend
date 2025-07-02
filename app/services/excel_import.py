import pandas as pd
import pdfkit
import tempfile
import os
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.models.user import User


def parse_excel(path: str, db: Session | None = None) -> List[Dict[str, Any]]:
    """Parse an Excel file into TurnoIn-compatible payloads.

    The function accepts either a ``User ID`` column directly or an ``Agente``
    column. When ``Agente`` is used, a SQLAlchemy ``Session`` must be provided
    to resolve user names.

    Colonne obbligatorie / Required columns: ``Data``, ``Inizio1`` and
    ``Fine1``. Provide either ``User ID`` or ``Agente`` to associate the shift.
    Optional columns: ``Inizio2``, ``Fine2``, ``Inizio3``, ``Fine3``, ``Tipo`` e
    ``Note``.

    :return: a list of dictionaries ready for the TurnoIn API.
    """
    df = pd.read_excel(path)  # requires openpyxl
    rows: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        if db is not None and "Agente" in df.columns:
            user = db.query(User).filter(User.nome == row["Agente"]).first()
            if not user:
                raise ValueError(f"Unknown user: {row['Agente']}")
            user_id = str(user.id)
        elif "User ID" in df.columns:
            user_id = str(row["User ID"])
        else:
            raise ValueError("User information missing: provide 'User ID' column or a DB session with 'Agente'.")

        payload: dict[str, Any] = {
            "user_id": user_id,
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


def df_to_pdf(rows: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Generate a PDF table from row payloads and return its paths.

    :return: A tuple ``(pdf_path, html_path)`` pointing to the generated files.
    """
    df = pd.DataFrame(rows)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_html:
        df.to_html(tmp_html.name, index=False)
        html_path = tmp_html.name
    pdf_path = html_path.replace(".html", ".pdf")
    pdfkit.from_file(html_path, pdf_path)  # requires wkhtmltopdf installed
    return pdf_path, html_path
