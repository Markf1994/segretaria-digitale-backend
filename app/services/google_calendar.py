from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from fastapi import HTTPException
from app.config import settings
import os


def list_upcoming_events(days: int) -> list[dict[str, Any]]:
    """Return upcoming Google Calendar events within ``days``.

    The function expects ``GOOGLE_CREDENTIALS_JSON`` and ``GOOGLE_CALENDAR_ID``
    environment variables. When they are missing, an empty list is returned.
    ``data_ora`` fields in the returned dictionaries are ``datetime`` objects.
    """
    creds_json = settings.GOOGLE_CREDENTIALS_JSON
    calendar_id = settings.GOOGLE_CALENDAR_ID
    if not creds_json or not calendar_id:
        return []

    try:
        from googleapiclient.discovery import build  # type: ignore
        from google.oauth2.service_account import Credentials as SACredentials  # type: ignore
        from google.oauth2.credentials import Credentials as UserCredentials  # type: ignore

        if os.path.isfile(creds_json):
            with open(creds_json, "r") as fh:
                info = json.load(fh)
        else:
            info = json.loads(creds_json)

        if info.get("type") == "service_account":
            creds = SACredentials.from_service_account_info(
                info,
                scopes=["https://www.googleapis.com/auth/calendar.readonly"],
            )
        else:
            creds = UserCredentials.from_authorized_user_info(info)

        service = build("calendar", "v3", credentials=creds)
        now = datetime.utcnow()
        time_min = now.isoformat() + "Z"
        time_max = (now + timedelta(days=days)).isoformat() + "Z"
        result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        items = []
        for ev in result.get("items", []):
            start = ev.get("start", {})
            when = start.get("dateTime") or start.get("date")
            if not when:
                continue
            try:
                dt = datetime.fromisoformat(when.replace("Z", "+00:00"))
            except ValueError:
                continue
            items.append(
                {
                    "id": ev.get("id"),
                    "titolo": ev.get("summary"),
                    "descrizione": ev.get("description"),
                    "data_ora": dt,
                }
            )
        return items
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - unexpected errors
        raise HTTPException(status_code=500, detail=str(exc))


def list_events_between(start: datetime, end: datetime) -> list[dict[str, Any]]:
    """Return Google Calendar events between ``start`` and ``end``.

    Credentials and calendar ID are loaded from ``settings`` in the same way as
    :func:`list_upcoming_events`.  When either is missing an empty list is
    returned. ``data_ora`` fields in the returned dictionaries are ``datetime``
    objects.
    """

    creds_json = settings.GOOGLE_CREDENTIALS_JSON
    calendar_id = settings.GOOGLE_CALENDAR_ID
    if not creds_json or not calendar_id:
        return []

    try:
        from googleapiclient.discovery import build  # type: ignore
        from google.oauth2.service_account import Credentials as SACredentials  # type: ignore
        from google.oauth2.credentials import Credentials as UserCredentials  # type: ignore

        if os.path.isfile(creds_json):
            with open(creds_json, "r") as fh:
                info = json.load(fh)
        else:
            info = json.loads(creds_json)

        if info.get("type") == "service_account":
            creds = SACredentials.from_service_account_info(
                info,
                scopes=["https://www.googleapis.com/auth/calendar.readonly"],
            )
        else:
            creds = UserCredentials.from_authorized_user_info(info)

        service = build("calendar", "v3", credentials=creds)
        time_min = start.isoformat() + "Z"
        time_max = end.isoformat() + "Z"
        result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        items = []
        for ev in result.get("items", []):
            start_obj = ev.get("start", {})
            when = start_obj.get("dateTime") or start_obj.get("date")
            if not when:
                continue
            try:
                dt = datetime.fromisoformat(when.replace("Z", "+00:00"))
            except ValueError:
                continue
            items.append(
                {
                    "id": ev.get("id"),
                    "titolo": ev.get("summary"),
                    "descrizione": ev.get("description"),
                    "data_ora": dt,
                }
            )
        return items
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - unexpected errors
        raise HTTPException(status_code=500, detail=str(exc))
