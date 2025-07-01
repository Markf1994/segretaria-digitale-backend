# app/services/gcal.py
import os, json
from datetime import date, time
from google.oauth2 import service_account
from googleapiclient.discovery import build
import googleapiclient.errors as gerr

# 1.  credenziali ----------------------------------------------------------------
CREDS = service_account.Credentials.from_service_account_file(
    os.getenv("GOOGLE_CREDENTIALS_JSON"),
    scopes=["https://www.googleapis.com/auth/calendar"],
)
GCAL = build("calendar", "v3", credentials=CREDS)

# 2.  ID dei due calendari (ambiente) -------------------------------------------
EVENT_CAL_ID  = os.getenv("G_EVENT_CAL_ID")   # già esistente
SHIFT_CAL_ID  = os.getenv("G_SHIFT_CAL_ID")   # <-- nuovo calendario Turni
def iso_dt(d: date, t: time) -> str:
    """2025-07-01 + 08:30 -> '2025-07-01T08:30:00+02:00'"""
    tz = "+02:00"  # oppure leggi da settings/team
    return f"{d.isoformat()}T{t.strftime('%H:%M')}:00{tz}"

def first_non_null(*vals):
    return next(v for v in vals if v)

def last_non_null(*vals):
    return next(v for v in reversed(vals) if v)
def sync_shift_event(turno):
    """
    Crea o aggiorna l'evento corrispondente a 'turno'
    nel calendario 'Turni di Servizio'.
    """
    evt_id = f"shift-{turno.id}"  # ID stabile = prefisso + UUID DB

    # pick primi/ultimi orari presenti
    start = first_non_null(turno.inizio_1, turno.inizio_2, turno.inizio_3)
    end   = last_non_null(turno.fine_3, turno.fine_2, turno.fine_1)

    body = {
        "id": evt_id,
        "summary": f"{turno.user.cognome} {turno.user.nome}",
        "start": {"dateTime": iso_dt(turno.giorno, start)},
        "end":   {"dateTime": iso_dt(turno.giorno, end)},
        "description": turno.note or "",
        "colorId": "11" if turno.tipo == "STRAORD" else "10",  # rosso/blu
    }

    try:
        GCAL.events().update(calendarId=SHIFT_CAL_ID,
                             eventId=evt_id, body=body).execute()
    except gerr.HttpError as e:
        if e.resp.status == 404:                # evento non esiste ancora
            GCAL.events().insert(calendarId=SHIFT_CAL_ID,
                                 body=body).execute()
        else:
            raise
GCAL.events().delete(calendarId=SHIFT_CAL_ID,
                     eventId=f"shift-{turno.id}").execute()
