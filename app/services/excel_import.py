import pandas as pd
import pdfkit
import tempfile
import os
from typing import Any, Dict, List, Tuple
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_id(db: Session, agente: str) -> str:
    """Return the ``User.id`` for ``agente`` raising ``ValueError`` if missing."""

    if not db:
        raise ValueError("A database session is required to resolve users")

    name = agente.strip()
    user = db.query(User).filter(User.nome == name).first()
    if not user:
        raise ValueError(f"Unknown user: {agente}")
    return str(user.id)


def parse_excel(path: str, db: Session) -> List[Dict[str, Any]]:
    """Parse an Excel file exported from Google Sheets.

    The sheet must contain the columns ``Agente``, ``Data`` and ``Tipo`` in
    addition to ``Inizio1``/``Fine1``. If present, ``Inizio2``/``Fine2`` will be
    mapped to ``slot2`` while ``Straordinario inizio``/``Straordinario fine`` are
    mapped to ``slot3``. ``Agente`` is resolved to a ``User.id`` using the
    provided ``Session``.

    :return: a list of dictionaries ready for the TurnoIn API.
    """

    df = pd.read_excel(path)  # requires openpyxl
    rows: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        user_id = get_user_id(db, row["Agente"])

        payload: dict[str, Any] = {
            "user_id": user_id,
            "giorno": row["Data"].date() if hasattr(row["Data"], "date") else row["Data"],
            "slot1": {"inizio": row["Inizio1"], "fine": row["Fine1"]},
            "tipo": row.get("Tipo", "NORMALE"),
            "note": "",
        }

        if "Inizio2" in df.columns and not pd.isna(row.get("Inizio2")) and not pd.isna(row.get("Fine2")):
            payload["slot2"] = {"inizio": row["Inizio2"], "fine": row["Fine2"]}

        if (
            "Straordinario inizio" in df.columns
            and not pd.isna(row.get("Straordinario inizio"))
            and not pd.isna(row.get("Straordinario fine"))
        ):
            payload["slot3"] = {
                "inizio": row["Straordinario inizio"],
                "fine": row["Straordinario fine"],
            }

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
