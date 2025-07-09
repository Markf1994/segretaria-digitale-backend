# app/services/gcal.py
"""
Helper unico per interagire con Google Calendar per i turni di servizio.
Richiede:
  GOOGLE_CREDENTIALS_JSON=/percorso/service_account.json
  G_SHIFT_CAL_ID=…@group.calendar.google.com
"""

from datetime import date, time, datetime
from functools import lru_cache
import hashlib
from app.config import settings
import logging

import json
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
import googleapiclient.errors as gerr

from app.schemas.turno import DAY_OFF_TYPES, TipoTurno

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------- agent colors
# Mapping of agent email addresses to Google Calendar color IDs.  These values
# are used by ``color_for_user`` when the matching email is found.  Any user not
# listed here falls back to a hash-based color selection.
AGENT_COLORS = {
    "marco@comune.castione.bg.it": "1",
    "rossella@comune.castione.bg.it": "6",
    "mattia@comune.castione.bg.it": "7",
}


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


# ------------------------------------------------------------------- utilità
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


def color_for_user(user) -> str:
    """Return a Google Calendar color ID for ``user``.

    ``user`` may be a user object or a string containing an ID or email
    address.  The function first checks :data:`AGENT_COLORS` for a matching
    email or identifier before falling back to a deterministic hash-based
    selection.
    """

    if not isinstance(user, str):
        email = getattr(user, "email", None)
        if email and email in AGENT_COLORS:
            return AGENT_COLORS[email]
        identifier = getattr(user, "id", None)
        if identifier is not None and str(identifier) in AGENT_COLORS:
            return AGENT_COLORS[str(identifier)]
        user_id = email or str(identifier)
    else:
        if user in AGENT_COLORS:
            return AGENT_COLORS[user]
        user_id = user

    colors = [str(i) for i in range(1, 12)]
    digest = hashlib.sha1(user_id.encode("utf-8")).digest()
    idx = int.from_bytes(digest[:4], "big") % len(colors)
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
    evt_id = f"shift-{str(turno.id).replace('-', '')}"

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
        "colorId": color_for_user(turno.user),
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
            logger.warning("Update of event %s failed (%s), inserting", evt_id, e.resp.status)
            try:
                gcal.events().insert(
                    calendarId=cal_id,
                    body=body,
                    sendUpdates="none",
                ).execute()
            except gerr.HttpError as e2:
                logger.error("Failed to insert event %s: %s", evt_id, e2)
                raise
        else:
            logger.error("Failed to update event %s: %s", evt_id, e)
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
            eventId=f"shift-{str(turno_id).replace('-', '')}",
            sendUpdates="none",
        ).execute()
    except gerr.HttpError as e:
        if e.resp.status == 404:
            logger.warning("Delete of event %s returned 404", turno_id)
        else:
            logger.error("Failed to delete event %s: %s", turno_id, e)
            raise
