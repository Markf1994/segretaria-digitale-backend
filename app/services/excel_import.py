import pandas as pd
import pdfkit
import tempfile
from typing import Any, Dict, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User


def get_user_id(db: Session, agente: str) -> str:
    """Return the ``User.id`` for ``agente`` raising ``ValueError`` if missing."""

    if db is None:
        raise ValueError("A database session is required to resolve users")

    name = agente.strip()
    user = db.query(User).filter(User.nome == name).first()
    if not user:
        raise ValueError(f"Unknown user: {agente}")
    return str(user.id)


def parse_excel(path: str, db: Session | None = None) -> List[Dict[str, Any]]:
    """Parse an Excel file exported from Google Sheets.

    The file may contain either a ``User ID`` column or an ``Agente`` column.
    When ``Agente`` is present a database session is required in order to
    resolve the user name to the corresponding ``User.id``. ``Inizio2``/``Fine2``
    and ``Inizio3``/``Fine3`` (or ``Straordinario inizio``/``Straordinario fine``)
    are mapped to the ``inizio_2``/``fine_2`` and ``inizio_3``/``fine_3`` fields.

    :return: a list of dictionaries ready for the ``TurnoIn`` API.
    """

    df = pd.read_excel(path)  # requires openpyxl

    base_required = {"Data", "Inizio1", "Fine1"}

    if "User ID" in df.columns:
        required = base_required | {"User ID"}
    elif "Agente" in df.columns:
        required = base_required | {"Agente"}
    else:
        raise HTTPException(
            status_code=400, detail="Missing columns: {'User ID' or 'Agente'}"
        )

    missing = required - set(df.columns)
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

    rows: list[dict[str, Any]] = []

    for idx, row in df.iterrows():
        row_num = idx + 2
        user_col = "User ID" if "User ID" in df.columns else "Agente"
        value = row.get(user_col)
        if pd.isna(value) or str(value).strip() == "":
            raise HTTPException(
                status_code=400,
                detail=f"Row {row_num}: Missing user identifier",
            )

        if user_col == "User ID":
            user_id = str(value)
            if db is not None:
                user = db.query(User).filter(User.id == user_id).first()
                if not user:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Row {row_num}: Unknown user ID: {user_id}",
                    )
        else:
            if db is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Row {row_num}: Database session required to resolve 'Agente'",
                )
            try:
                user_id = get_user_id(db, value)
            except ValueError as err:
                raise HTTPException(status_code=400, detail=f"Row {row_num}: {err}")

        payload: dict[str, Any] = {
            "user_id": user_id,
            "giorno": (
                row["Data"].date() if hasattr(row["Data"], "date") else row["Data"]
            ),
            "inizio_1": row["Inizio1"],
            "fine_1": row["Fine1"],
            "tipo": row.get("Tipo", "NORMALE"),
            "note": row.get("Note", ""),
        }

        if (
            "Inizio2" in df.columns
            and not pd.isna(row.get("Inizio2"))
            and not pd.isna(row.get("Fine2"))
        ):
            payload["inizio_2"] = row["Inizio2"]
            payload["fine_2"] = row["Fine2"]

        if (
            "Straordinario inizio" in df.columns
            and not pd.isna(row.get("Straordinario inizio"))
            and not pd.isna(row.get("Straordinario fine"))
        ):
            payload["inizio_3"] = row["Straordinario inizio"]
            payload["fine_3"] = row["Straordinario fine"]
        elif (
            "Inizio3" in df.columns
            and not pd.isna(row.get("Inizio3"))
            and not pd.isna(row.get("Fine3"))
        ):
            payload["inizio_3"] = row["Inizio3"]
            payload["fine_3"] = row["Fine3"]

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
    try:
        pdfkit.from_file(html_path, pdf_path)  # requires wkhtmltopdf installed
    except OSError as err:
        if "wkhtmltopdf" in str(err):
            raise HTTPException(
                status_code=500,
                detail="wkhtmltopdf not installed",
            )
        raise
    return pdf_path, html_path
