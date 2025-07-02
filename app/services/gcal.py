# app/services/gcal.py
"""
Helper unico per interagire con i due calendari Google:
– calendario Eventi   (G_EVENT_CAL_ID)
– calendario Turni    (G_SHIFT_CAL_ID)
Richiede:
  GOOGLE_CREDENTIALS_JSON=/percorso/service_account.json
  G_EVENT_CAL_ID=…@group.calendar.google.com
  G_SHIFT_CAL_ID=…@group.calendar.google.com
"""

import os
from datetime import date, time, datetime
from functools import lru_cache

from google.oauth2 import service_account
from googleapiclient.discovery import build
import googleapiclient.errors as gerr

# ------------------------------------------------------------------- credenziali
@lru_cache()
def get_client():
    """Return a Google Calendar client built from service account credentials."""
    creds = service_account.Credentials.from_service_account_file(
        os.getenv("GOOGLE_CREDENTIALS_JSON"),
        scopes=["https://www.googleapis.com/auth/calendar"],
    )
    return build("calendar", "v3", credentials=creds)

# ------------------------------------------------------------------- calendar ID
EVENT_CAL_ID = os.getenv("G_EVENT_CAL_ID")   # già in uso per gli altri eventi
SHIFT_CAL_ID = os.getenv("G_SHIFT_CAL_ID")   # nuovo calendario “Turni di Servizio”

# ------------------------------------------------------------------- utilità
def iso_dt(d: date, t: time) -> str:
    """2025-07-01 + 08:30 -> '2025-07-01T08:30:00+02:00'"""
    offset = datetime.now().astimezone().utcoffset()
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

# ------------------------------------------------------------------- sync turni
def sync_shift_event(turno):
    """
    Crea o aggiorna l'evento relativo a un turno
    nel calendario 'Turni di Servizio'.
    """
    evt_id = f"shift-{turno.id}"  # chiave stabile = prefisso + UUID DB

    # orari: primo inizio disponibile, ultimo fine disponibile
    start = first_non_null(turno.inizio_1, turno.inizio_2, turno.inizio_3)
    end   = last_non_null(turno.fine_3, turno.fine_2, turno.fine_1)

    body = {
        "id": evt_id,
        "summary": turno.user.nome or turno.user.email.split("@")[0],
        "description": turno.note or "",
        "start": {"dateTime": iso_dt(turno.giorno, start)},
        "end":   {"dateTime": iso_dt(turno.giorno, end)},
        "colorId": "11" if turno.tipo == "STRAORD" else "10",  # rosso / blu
    }

    gcal = get_client()
    try:
        gcal.events().update(
            calendarId=SHIFT_CAL_ID,
            eventId=evt_id,
            body=body,
        ).execute()
    except gerr.HttpError as e:
        if e.resp.status == 404:              # evento non esiste → crealo
            gcal.events().insert(
                calendarId=SHIFT_CAL_ID,
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
    gcal = get_client()
    try:
        gcal.events().delete(
            calendarId=SHIFT_CAL_ID,
            eventId=f"shift-{turno_id}",
        ).execute()
    except gerr.HttpError as e:
        if e.resp.status != 404:
            raise
