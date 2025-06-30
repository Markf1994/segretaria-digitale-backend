from __future__ import annotations

import json
import os
from datetime import datetime

from fastapi import APIRouter, HTTPException
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as SACredentials
from google.oauth2.credentials import Credentials as UserCredentials

router = APIRouter(prefix="/calendar", tags=["Calendar"], trailing_slash=False)


def _load_credentials() -> UserCredentials | SACredentials:
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not creds_json:
        raise HTTPException(status_code=500, detail="Google credentials not configured")
    try:
        if os.path.isfile(creds_json):
            with open(creds_json, "r") as fh:
                info = json.load(fh)
        else:
            info = json.loads(creds_json)
    except Exception as exc:  # pragma: no cover - invalid JSON
        raise HTTPException(status_code=500, detail=f"Invalid credentials: {exc}")

    if info.get("type") == "service_account":
        return SACredentials.from_service_account_info(
            info, scopes=["https://www.googleapis.com/auth/calendar.readonly"]
        )
    return UserCredentials.from_authorized_user_info(info)


def get_calendar_service():
    creds = _load_credentials()
    return build("calendar", "v3", credentials=creds)


@router.get("")
def list_calendar_events():
    try:
        service = get_calendar_service()
        now = datetime.utcnow().isoformat() + "Z"
        result = (
            service.events()
            .list(calendarId="primary", timeMin=now, singleEvents=True, orderBy="startTime")
            .execute()
        )
        return result.get("items", [])
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - unexpected errors
        raise HTTPException(status_code=500, detail=str(exc))
