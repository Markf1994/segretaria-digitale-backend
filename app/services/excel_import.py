import pandas as pd
from weasyprint import HTML
import tempfile
from datetime import datetime, timedelta, time
from typing import Any, Dict, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
import os
import html as html_utils
import re

from app.models.user import User
from app.models.event import Event
from app.schemas.turno import DAY_OFF_TYPES, TipoTurno
from app.services.google_calendar import list_events_between


def get_user_id(db: Session, agente: str) -> str:
    """Return the ``User.id`` for ``agente`` raising ``ValueError`` if missing."""

    if db is None:
        raise ValueError("A database session is required to resolve users")

    name = agente.strip()
    user = (
        db.query(User)
        .filter(func.lower(User.nome) == name.lower())
        .first()
    )
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


def _not_nan(value: Any) -> bool:
    """Return ``False`` when ``value`` is ``None`` or NaN."""

    if value is None:
        return False
    return not pd.isna(value)


EMAIL_RE = re.compile(r"\S+@\S+")


def _strip_emails(text: str) -> str:
    """Remove email addresses from ``text`` and return the cleaned string."""

    if not text:
        return ""
    cleaned = EMAIL_RE.sub("", text).strip()
    return cleaned


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

    if "Data" in df.columns:
        df.rename(columns={"Data": "Giorno"}, inplace=True)

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
                detail=f"Row {row_num}: Invalid 'Tipo' value: {raw_tipo}",
            )
        inizio1 = _clean(row.get("Inizio1"))
        fine1 = _clean(row.get("Fine1"))
        if (inizio1 is None or fine1 is None) and row_type not in {
            t.value for t in DAY_OFF_TYPES
        }:
            raise HTTPException(
                status_code=400,
                detail=f"Row {row_num}: Missing 'Inizio1' or 'Fine1'",
            )

        payload: dict[str, Any] = {
            "user_id": user_id,
            "giorno": (
                row["Giorno"].date()
                if hasattr(row["Giorno"], "date")
                else row["Giorno"]
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

    def fmt(t: Any) -> str:
        """Return ``t`` formatted as HH:MM when it is a time or string value."""
        if t is None or t == "":
            return ""
        if isinstance(t, time):
            return t.strftime("%H:%M")
        if isinstance(t, str):
            for fmt_str in ("%H:%M:%S", "%H:%M"):
                try:
                    return datetime.strptime(t, fmt_str).strftime("%H:%M")
                except ValueError:
                    continue
            return t
        return str(t)

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
                segments.append(f"{fmt(row['inizio_1'])} – {fmt(row['fine_1'])}")
            if _not_nan(row.get("inizio_2")) and _not_nan(row.get("fine_2")):
                segments.append(f"{fmt(row['inizio_2'])} – {fmt(row['fine_2'])}")
            if _not_nan(row.get("inizio_3")) and _not_nan(row.get("fine_3")):
                segments.append(
                    f"<span class='extra'>{fmt(row['inizio_3'])} – {fmt(row['fine_3'])} STRAORDINARIO</span>"
                )
            cell = "<br>".join(segments)

        if agent:
            by_date[day][agent] = cell
        if row.get("note"):
            note_text = _strip_emails(str(row.get("note")))
            if note_text:
                notes[day].append(html_utils.escape(note_text))

    # Load Google Calendar events for the week
    gcal_notes: dict[str, list[str]] = {}
    try:
        events = list_events_between(
            datetime.combine(week_start_date, time.min),
            datetime.combine(week_end_date, time.max),
        )
    except HTTPException:
        raise
    except Exception:
        events = []

    for ev in events:
        if str(ev.get("id", "")).startswith("shift-"):
            continue
        title = ev.get("titolo")
        if isinstance(title, str) and title.strip().lower().startswith("turno"):
            continue
        day = ev.get("data_ora")
        if isinstance(day, datetime):
            key = day.date().strftime("%d/%m/%Y")
            if title:
                clean = _strip_emails(str(title))
                if clean:
                    gcal_notes.setdefault(key, []).append(
                        html_utils.escape(clean)
                    )

    # Load public events from the database
    event_notes: dict[str, list[str]] = {}
    if db is not None:
        public_events = (
            db.query(Event.titolo, Event.data_ora)
            .filter(Event.is_public == True)
            .filter(Event.data_ora >= datetime.combine(week_start_date, time.min))
            .filter(Event.data_ora <= datetime.combine(week_end_date, time.max))
            .all()
        )
        for titolo, dt in public_events:
            key = dt.date().strftime("%d/%m/%Y")
            clean = _strip_emails(str(titolo))
            if clean:
                event_notes.setdefault(key, []).append(html_utils.escape(clean))

    # Generate HTML
    logo_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "static", "Logo.png")
    )
    if not os.path.exists(logo_path):
        raise HTTPException(status_code=500, detail="Logo file missing")
    styles = """
    <style>
    @page { size: A4 landscape; margin: 10mm; }
    body { font-family: Aptos, sans-serif; font-size: 10pt; }
    table { border-collapse: collapse; width: 100%; page-break-inside: avoid; }
    th, td { border: 1px solid #000; padding: 4px; text-align: center; }
    td.notes { text-align: left; }
    .dayoff { color: red; font-weight: bold; }
    .extra { color: red; }
    </style>
    """

    header = f"""
    <div style='display:flex; align-items:center; margin-bottom:10px;'>
        <img src='{logo_path}' alt='logo' style='width:70px; margin-right:8px;' />
        <div style='display:flex; flex-direction:column;'>
            <span>COMUNE DI CASTIONE DELLA PRESOLANA – SERVIZIO DI POLIZIA LOCALE</span>
            <span style='font-weight:bold; font-style:italic;'>ORARIO DI SERVIZIO – {start_date} – {end_date}</span>
        </div>
    </div>
    """

    table_header = (
        "<tr><th>DATA</th>"
        + "".join(f"<th>{html_utils.escape(str(a))}</th>" for a in agents)
        + "<th>ANNOTAZIONI DI SERVIZIO</th></tr>"
    )

    rows_html = []
    weekday_map = {
        0: "LUNEDI",
        1: "MARTEDI",
        2: "MERCOLEDI",
        3: "GIOVEDI",
        4: "VENERDI",
        5: "SABATO",
        6: "DOMENICA",
    }

    for day in sorted(by_date.keys()):
        date_obj = datetime.strptime(day, "%d/%m/%Y").date()
        weekday = weekday_map[date_obj.weekday()]
        cells = [f"<td>{weekday}<br>{day}</td>"]
        for a in agents:
            cells.append(f"<td>{by_date[day].get(a, '')}</td>")
        note_lines = notes.get(day, []) + gcal_notes.get(day, []) + event_notes.get(day, [])
        if note_lines:
            note_text = "<ul>" + "".join(f"<li>{l}</li>" for l in note_lines) + "</ul>"
        else:
            note_text = ""
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
    HTML(filename=html_path).write_pdf(pdf_path)

    return pdf_path, html_path
