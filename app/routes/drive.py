from __future__ import annotations

import json
import os
from typing import Any

from fastapi import APIRouter, HTTPException
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials as SACredentials
from google.oauth2.credentials import Credentials as UserCredentials

router = APIRouter(prefix="/drive", tags=["Drive"], trailing_slash=False)


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
            info, scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )
    return UserCredentials.from_authorized_user_info(info)


def get_drive_service():
    creds = _load_credentials()
    return build("drive", "v3", credentials=creds)


@router.get("")
def list_drive_files():
    try:
        service = get_drive_service()
        folder_id = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
        query = f"'{folder_id}' in parents" if folder_id else None
        result = (
            service.files()
            .list(q=query, fields="files(id, name, mimeType)")
            .execute()
        )
        return result.get("files", [])
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - unexpected errors
        raise HTTPException(status_code=500, detail=str(exc))
