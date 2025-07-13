from __future__ import annotations

import json
import logging
import os
from datetime import timedelta

from googleapiclient.discovery import build  # type: ignore
from google.oauth2.service_account import Credentials as SACredentials  # type: ignore
from google.oauth2.credentials import Credentials as UserCredentials  # type: ignore

from app.config import settings
from app.models.event import Event

logger = logging.getLogger(__name__)


def create_event(event: Event) -> None:
    """Insert ``event`` into Google Calendar if configuration is present."""
    creds_json = settings.GOOGLE_CREDENTIALS_JSON
    calendar_id = settings.GOOGLE_CALENDAR_ID
    if not creds_json or not calendar_id:
        return

    if os.path.isfile(creds_json):
        with open(creds_json, "r") as fh:
            info = json.load(fh)
    else:
        info = json.loads(creds_json)

    if info.get("type") == "service_account":
        creds = SACredentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/calendar"]
        )
    else:
        creds = UserCredentials.from_authorized_user_info(info)

    service = build("calendar", "v3", credentials=creds)

    body = {
        "summary": event.titolo,
        "description": event.descrizione,
        "start": {"dateTime": event.data_ora.isoformat()},
        "end": {"dateTime": (event.data_ora + timedelta(hours=1)).isoformat()},
    }

    try:
        service.events().insert(calendarId=calendar_id, body=body).execute()
        logger.info("Inserted event %s into calendar %s", event.id, calendar_id)
    except Exception as exc:  # pragma: no cover - unexpected errors
        logger.error(
            "Failed to create Google Calendar event (cal_id=%s): %s",
            calendar_id,
            exc,
        )
        raise
