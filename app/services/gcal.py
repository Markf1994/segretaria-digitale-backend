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

# Default behaviour is to avoid sending email notifications when calendar
# events are modified.
DEFAULT_SEND_UPDATES = "none"

# ------------------------------------------------------------------- agent colors
# Mapping of agent email addresses, IDs or names to Google Calendar color IDs.
# These values are used by ``color_for_user`` when the matching key is found.
# Any user not listed here falls back to a hash-based color selection.
AGENT_COLORS = {
    "marco@comune.castione.bg.it": "7",
    "rossella@comune.castione.bg.it": "3",
    "mattia@comune.castione.bg.it": "5",
}

# Short names to use for specific agents in calendar event summaries. When a
# user's email matches one of the keys here, the corresponding value is used in
# place of the full ``nome`` or email address.
AGENT_SHORT_NAMES = {
    "marco@comune.castione.bg.it": "Marco",
    "rossella@comune.castione.bg.it": "Rossella",
    "mattia@comune.castione.bg.it": "Mattia",
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


def shift_event_id(turno_id) -> str:
    """Return the calendar event ID for a given ``turno_id``."""
    return f"shift-{str(turno_id).replace('-', '')}"


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
        name = getattr(user, "nome", None)
        if isinstance(name, str) and name.strip() in AGENT_COLORS:
            return AGENT_COLORS[name.strip()]
        user_id = email or str(identifier) or (name.strip() if isinstance(name, str) else "")
    else:
        if user in AGENT_COLORS:
            return AGENT_COLORS[user]
        user_id = user

    colors = [str(i) for i in range(1, 12)]
    digest = hashlib.sha1(user_id.encode("utf-8")).digest()
    idx = int.from_bytes(digest[:4], "big") % len(colors)
    return colors[idx]


def short_name_for_user(user) -> str:
    """Return a concise name for ``user`` to use in event titles."""
    if not isinstance(user, str):
        email = getattr(user, "email", "")
        if email in AGENT_SHORT_NAMES:
            return AGENT_SHORT_NAMES[email]
        name = getattr(user, "nome", None)
        if isinstance(name, str) and name.strip():
            return name.strip()
        if email:
            return email.split("@")[0]
        return ""
    else:
        return AGENT_SHORT_NAMES.get(user, user.split("@")[0])


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
        logger.info("Removed calendar event for day off: %s", turno.id)
        return

    # Google Calendar limita l'alfabeto degli identificativi degli eventi a
    # lettere, numeri, underscore e trattino. Gli UUID generati dall'ORM
    # contengono "-" che sono consentiti ma in alcuni casi Google restituisce
    # "Invalid resource id value". Rimuoviamo quindi i trattini per maggiore
    # compatibilità e generiamo un ID privo di caratteri speciali.
    evt_id = shift_event_id(turno.id)

    # orari: primo inizio disponibile, ultimo fine disponibile
    start = first_non_null(turno.inizio_1, turno.inizio_2, turno.inizio_3)
    end = last_non_null(turno.fine_3, turno.fine_2, turno.fine_1)

    title_name = short_name_for_user(turno.user)
    body = {
        "id": evt_id,
        "summary": title_name,
        "description": f"Turno servizio {title_name}",
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
            sendUpdates=DEFAULT_SEND_UPDATES,
        ).execute()
        logger.info("Updated event %s", evt_id)
    except gerr.HttpError as e:
        if e.resp.status in (404, 400):
            # status 400 may be returned when Google thinks the event ID is invalid,
            # so treat it like a missing event and create it from scratch
            logger.info(
                "Update of event %s on calendar %s failed (%s), inserting",
                evt_id,
                cal_id,
                e.resp.status,
            )
            try:
                gcal.events().insert(
                    calendarId=cal_id,
                    body=body,
                    sendUpdates=DEFAULT_SEND_UPDATES,
                ).execute()
                logger.info("Inserted event %s", evt_id)
            except gerr.HttpError as e2:
                logger.exception(
                    "Failed to insert event %s on calendar %s", evt_id, cal_id
                )
                raise
        else:
            logger.exception(
                "Failed to update event %s on calendar %s", evt_id, cal_id
            )
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
            eventId=shift_event_id(turno_id),
            sendUpdates=DEFAULT_SEND_UPDATES,
        ).execute()
        logger.info("Deleted event %s", turno_id)
    except gerr.HttpError as e:
        if e.resp.status == 404:
            logger.info("Delete of event %s returned 404", turno_id)
        else:
            logger.exception(
                "Failed to delete event %s on calendar %s", turno_id, cal_id
            )
            raise
