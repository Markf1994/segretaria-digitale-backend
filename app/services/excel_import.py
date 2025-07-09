import pandas as pd
import pdfkit
import tempfile
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException
import os
import html

from app.models.user import User
from app.schemas.turno import DAY_OFF_TYPES, TipoTurno


def get_user_id(db: Session, agente: str) -> str:
    """Return the ``User.id`` for ``agente`` raising ``ValueError`` if missing."""

    if db is None:
        raise ValueError("A database session is required to resolve users")

    name = agente.strip()
    user = db.query(User).filter(User.nome == name).first()
    if not user:
        raise ValueError(f"Unknown user: {agente}")
    return str(user.id)


def _clean(cell: Any) -> Any:
    """Strip whitespace from strings and convert empty/NaN values to ``None``."""
    if pd.isna(cell):
        return None
    if isinstance(cell, str):
        cell = cell.strip()
        if cell == "" or cell.lower() == "nan":
            return None
    return cell


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

    import numpy as np

    # Normalize NaN to None for time and note columns
    time_cols = ["Inizio1", "Fine1", "Inizio2", "Fine2", "Inizio3", "Fine3"]
    all_cols = time_cols + ["Note"]
    for c in all_cols:
        if c in df.columns:
            df[c] = df[c].replace({np.nan: None})

    base_required = {"Giorno", "Inizio1", "Fine1"}

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

        raw_tipo = _clean(row.get("Tipo")) or "NORMALE"
        try:
            row_type = TipoTurno(raw_tipo.strip().upper()).value
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Row {row_num}: Invalid 'Tipo' value: {raw_tipo}"
            )
        inizio1 = _clean(row.get("Inizio1"))
        fine1 = _clean(row.get("Fine1"))
        if (
            inizio1 is None or fine1 is None
        ) and row_type not in {t.value for t in DAY_OFF_TYPES}:
            raise HTTPException(
                status_code=400,
                detail=f"Row {row_num}: Missing 'Inizio1' or 'Fine1'",
            )

        payload: dict[str, Any] = {
            "user_id": user_id,
            "giorno": (
                row["Giorno"].date() if hasattr(row["Giorno"], "date") else row["Giorno"]
            ),
            "inizio_1": inizio1,
            "fine_1": fine1,
            "tipo": row_type,
            "note": _clean(row.get("Note", "")) or "",
        }

        if (
            "Inizio2" in df.columns
            and _clean(row.get("Inizio2")) is not None
            and _clean(row.get("Fine2")) is not None
        ):
            payload["inizio_2"] = _clean(row["Inizio2"])
            payload["fine_2"] = _clean(row["Fine2"])

        if (
            "Straordinario inizio" in df.columns
            and _clean(row.get("Straordinario inizio")) is not None
            and _clean(row.get("Straordinario fine")) is not None
        ):
            payload["inizio_3"] = _clean(row["Straordinario inizio"])
            payload["fine_3"] = _clean(row["Straordinario fine"])
        elif (
            "Inizio3" in df.columns
            and _clean(row.get("Inizio3")) is not None
            and _clean(row.get("Fine3")) is not None
        ):
            payload["inizio_3"] = _clean(row["Inizio3"])
            payload["fine_3"] = _clean(row["Fine3"])

        rows.append(payload)

    return rows


def df_to_pdf(rows: List[Dict[str, Any]], db: Session | None = None) -> Tuple[str, str]:
    """Generate a PDF table from row payloads and return its paths.

    When a database session is provided, the ``user_id`` field is replaced
    with the corresponding agent name in an ``Agente`` column.

    :return: A tuple ``(pdf_path, html_path)`` pointing to the generated files.
    """

    df = pd.DataFrame(rows)

    if db is not None and "user_id" in df.columns:
        ids = [uid for uid in df["user_id"].unique() if uid is not None]
        mapping: dict[str, str] = {}
        if ids:
            users = db.query(User.id, User.nome).filter(User.id.in_(ids)).all()
            mapping = {str(u.id): u.nome for u in users}
        df["Agente"] = df["user_id"].map(mapping)
        df = df.drop(columns=["user_id"])

    # Resolve agent list and ISO week date range
    agents = sorted(a for a in df.get("Agente", []).unique() if a)
    df["giorno"] = pd.to_datetime(df["giorno"])
    first_day = df["giorno"].min().date()
    week_start_date = first_day - timedelta(days=first_day.weekday())
    week_end_date = week_start_date + timedelta(days=6)
    start_date = week_start_date.strftime("%d/%m/%Y")
    end_date = week_end_date.strftime("%d/%m/%Y")

    # Build rows grouped by date
    by_date: dict[str, dict[str, str]] = {}
    notes: dict[str, list[str]] = {}
    for _, row in df.iterrows():
        day = row["giorno"].date().strftime("%d/%m/%Y")
        by_date.setdefault(day, {a: "" for a in agents})
        notes.setdefault(day, [])
        agent = row.get("Agente", "")

        if row["tipo"] in {t.value for t in DAY_OFF_TYPES}:
            cell = f"<span class='dayoff'>{row['tipo']}</span>"
        else:
            segments: list[str] = []
            if row.get("inizio_1") and row.get("fine_1"):
                segments.append(f"{row['inizio_1']} – {row['fine_1']}")
            if row.get("inizio_2") and row.get("fine_2"):
                segments.append(f"{row['inizio_2']} – {row['fine_2']}")
            if row.get("inizio_3") and row.get("fine_3"):
                segments.append(
                    f"<span class='extra'>{row['inizio_3']} – {row['fine_3']} STRAORDINARIO</span>"
                )
            cell = "<br>".join(segments)

        if agent:
            by_date[day][agent] = cell
        if row.get("note"):
            notes[day].append(html.escape(str(row.get("note"))))

    # Generate HTML
    logo_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "static", "Logo.png")
    )
    if not os.path.exists(logo_path):
        raise HTTPException(status_code=500, detail="Logo file missing")
    styles = """
    <style>
    body { font-family: Aptos, sans-serif; font-size: 12pt; }
    table { border-collapse: collapse; width: 100%; }
    th, td { border: 1px solid #000; padding: 4px; text-align: center; }
    td.notes { text-align: left; }
    .dayoff { color: red; font-weight: bold; }
    .extra { color: red; }
    </style>
    """

    header = f"""
    <div style='text-align:center;'>
        <img src='{logo_path}' alt='logo' /><br>
        COMUNE DI CASTIONE DELLA PRESOLANA – SERVIZIO DI POLIZIA LOCALE<br>
        ORARIO DI SERVIZIO – {start_date} – {end_date}
    </div>
    """

    table_header = "<tr><th>DATA</th>" + "".join(
        f"<th>{html.escape(str(a))}</th>" for a in agents
    ) + "<th>ANNOTAZIONI DI SERVIZIO</th></tr>"

    rows_html = []
    for day in sorted(by_date.keys()):
        date_obj = datetime.strptime(day, "%d/%m/%Y").date()
        weekday = date_obj.strftime("%A").upper()
        cells = [f"<td>{weekday}<br>{day}</td>"]
        for a in agents:
            cells.append(f"<td>{by_date[day].get(a, '')}</td>")
        note_text = "<br>".join(notes.get(day, []))
        cells.append(f"<td class='notes'>{note_text}</td>")
        rows_html.append("<tr>" + "".join(cells) + "</tr>")

    html_content = f"""
    <html>
    <head>
    <meta charset='utf-8'>
    {styles}
    </head>
    <body>
    {header}
    <table>
    {table_header}
    {''.join(rows_html)}
    </table>
    </body>
    </html>
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_html:
        tmp_html.write(html_content.encode("utf-8"))
        html_path = tmp_html.name

    pdf_path = html_path.replace(".html", ".pdf")
    try:
        pdfkit.from_file(html_path, pdf_path, options={"orientation": "Landscape"})
    except OSError as err:
        if "wkhtmltopdf" in str(err):
            raise HTTPException(status_code=500, detail="wkhtmltopdf not installed")
        raise

    return pdf_path, html_path
