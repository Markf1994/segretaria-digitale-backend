import pandas as pd
import pdfkit
import tempfile
import os
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session


def get_user_id(db: Session, agente: str) -> str:
    """Return the ID of the user whose ``nome`` matches ``agente``.

    The lookup is case-insensitive and ignores surrounding whitespace. If no
    matching user is found, a ``ValueError`` is raised.
    """
    from sqlalchemy import func
    from app.models.user import User

    record = (
        db.query(User)
        .filter(func.lower(User.nome) == agente.strip().lower())
        .first()
    )
    if record is None:
        raise ValueError(f"Agente '{agente}' non trovato")
    return record.id


def parse_excel(db: Session, path: str) -> List[Dict[str, Any]]:
    """Parse an Excel file exported from the shift spreadsheet.

    Required columns: ``Agente``, ``Data``, ``Tipo``, ``Inizio1`` and ``Fine1``.
    Optional columns: ``Inizio2``, ``Fine2`` and ``Straordinario inizio`` /
    ``Straordinario fine``.

    The ``Agente`` value is matched against the ``nome`` field of ``User`` to
    obtain the ``user_id`` for each row.

    :param db: database session used to resolve agent names.
    :param path: path to the Excel file to parse.
    :return: list of dictionaries ready for the TurnoIn API.
    """

    df = pd.read_excel(path)  # requires openpyxl
    rows: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        payload: dict[str, Any] = {
            "user_id": get_user_id(db, str(row["Agente"])),
            "giorno": row["Data"].date() if hasattr(row["Data"], "date") else row["Data"],
            "slot1": {"inizio": row["Inizio1"], "fine": row["Fine1"]},
            "tipo": row.get("Tipo", "NORMALE"),
            "note": "",
        }

        inizio2 = row.get("Inizio2")
        fine2 = row.get("Fine2")
        if not pd.isna(inizio2) and not pd.isna(fine2):
            payload["slot2"] = {"inizio": inizio2, "fine": fine2}

        stra_inizio = row.get("Straordinario inizio")
        stra_fine = row.get("Straordinario fine")
        if not pd.isna(stra_inizio) and not pd.isna(stra_fine):
            payload["slot3"] = {"inizio": stra_inizio, "fine": stra_fine}

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
