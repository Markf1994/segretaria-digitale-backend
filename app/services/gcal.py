# app/services/gcal.py
"""
Helper unico per interagire con Google Calendar per i turni di servizio.
Richiede:
  GOOGLE_CREDENTIALS_JSON=/percorso/service_account.json
  G_SHIFT_CAL_ID=…@group.calendar.google.com
"""

from datetime import date, time, datetime
from functools import lru_cache
from uuid import UUID
from app.config import settings

import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import googleapiclient.errors as gerr

from app.schemas.turno import DAY_OFF_TYPES, TipoTurno


# ------------------------------------------------------------------- credenziali
@lru_cache()
def get_client():
    """Return a Google Calendar client built from service account credentials."""
    creds_json = settings.GOOGLE_CREDENTIALS_JSON
    if creds_json is None:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON is not configured")

    if os.path.isfile(creds_json):
        creds = service_account.Credentials.from_service_account_file(
            creds_json,
            scopes=["https://www.googleapis.com/auth/calendar"],
        )
    else:
        info = json.loads(creds_json)
        creds = service_account.Credentials.from_service_account_info(
            info,
            scopes=["https://www.googleapis.com/auth/calendar"],
        )

    return build("calendar", "v3", credentials=creds)


# ------------------------------------------------------------------- calendar ID
SHIFT_CAL_ID = settings.G_SHIFT_CAL_ID  # calendario "Turni di Servizio"


# ------------------------------------------------------------------- utilità
def make_event_id(turno_id: UUID | str) -> str:
    """Return the Google Calendar event ID for ``turno_id``."""
    return f"shift-{str(turno_id).replace('-', '')}"


def iso_dt(d: date, t: time) -> str:
    """2025-07-01 + 08:30 -> '2025-07-01T08:30:00+02:00'"""
    dt = datetime.combine(d, t)
    offset = dt.astimezone().utcoffset()
    if offset is None:
        tz = "+00:00"
    else:
        total_minutes = int(offset.total_seconds() // 60)
        sign = "+" if total_minutes >= 0 else "-"
        h, m = divmod(abs(total_minutes), 60)
        tz = f"{sign}{h:02d}:{m:02d}"
    return f"{d.isoformat()}T{t.strftime('%H:%M')}:00{tz}"


def first_non_null(*vals):
    return next(v for v in vals if v)


def last_non_null(*vals):
    return next(v for v in reversed(vals) if v)


def color_for_user(user_id: str) -> str:
    """Return a Google Calendar color ID derived from ``user_id``."""
    colors = [str(i) for i in range(1, 12)]
    idx = abs(hash(user_id)) % len(colors)
    return colors[idx]


# ------------------------------------------------------------------- sync turni
def sync_shift_event(turno):
    """
    Crea o aggiorna l'evento relativo a un turno
    nel calendario 'Turni di Servizio'.
    """
    cal_id = settings.G_SHIFT_CAL_ID
    if not cal_id:
        raise RuntimeError("G_SHIFT_CAL_ID is not configured")
    try:
        tipo = TipoTurno(turno.tipo)
    except ValueError:
        tipo = None

    if tipo in DAY_OFF_TYPES:
        # remove any existing calendar event for day-off records
        delete_shift_event(turno.id)
        return

    # Google Calendar limita l'alfabeto degli identificativi degli eventi a
    # lettere, numeri, underscore e trattino. Gli UUID generati dall'ORM
    # contengono "-" che sono consentiti ma in alcuni casi Google restituisce
    # "Invalid resource id value". Rimuoviamo quindi i trattini per maggiore
    # compatibilità e generiamo un ID privo di caratteri speciali.
    evt_id = make_event_id(turno.id)

    # orari: primo inizio disponibile, ultimo fine disponibile
    start = first_non_null(turno.inizio_1, turno.inizio_2, turno.inizio_3)
    end = last_non_null(turno.fine_3, turno.fine_2, turno.fine_1)

    title_name = turno.user.nome or turno.user.email.split("@")[0]
    body = {
        "id": evt_id,
        "summary": f"{start.strftime('%H:%M')} {title_name}",
        "description": turno.note or "",
        "start": {"dateTime": iso_dt(turno.giorno, start)},
        "end": {"dateTime": iso_dt(turno.giorno, end)},
        "colorId": color_for_user(str(turno.user.id)),
    }

    gcal = get_client()
    try:
        gcal.events().update(
            calendarId=cal_id,
            eventId=evt_id,
            body=body,
        ).execute()
    except gerr.HttpError as e:
        if e.resp.status in (404, 400):
            # status 400 may be returned when Google thinks the event ID is invalid,
            # so treat it like a missing event and create it from scratch
            gcal.events().insert(
                calendarId=cal_id,
                body=body,
                sendUpdates="none",
            ).execute()
        else:
            raise


def delete_shift_event(turno_id):
    """
    Elimina dal calendario Turni l'evento legato al turno rimosso.
    Ignora l'errore 404 se l'evento era già assente.
    """
    cal_id = settings.G_SHIFT_CAL_ID
    if not cal_id:
        raise RuntimeError("G_SHIFT_CAL_ID is not configured")

    gcal = get_client()
    try:
        gcal.events().delete(
            calendarId=cal_id,
            eventId=make_event_id(turno_id),
        ).execute()
    except gerr.HttpError as e:
        if e.resp.status != 404:
            raise
