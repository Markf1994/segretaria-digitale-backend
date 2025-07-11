from dataclasses import dataclass
import os
import re


@dataclass
class Settings:
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PDF_UPLOAD_ROOT: str = "uploads/pdfs"
    GOOGLE_CREDENTIALS_JSON: str | None = None
    G_SHIFT_CAL_ID: str | None = None
    GOOGLE_CALENDAR_ID: str | None = None
    GOOGLE_CLIENT_ID: str | None = None
    CORS_ORIGINS: str = "*"
    LOG_LEVEL: str = "INFO"


_CAL_ID_RE = re.compile(r"^[A-Za-z0-9_-]+@group\.calendar\.google\.com$")


def _getenv(key: str, default: str | None = None) -> str | None:
    """Retrieve and strip whitespace from an environment variable."""
    value = os.getenv(key, default)
    if value is not None:
        value = value.strip()
    return value


def load_settings() -> Settings:
    missing = []
    database_url = _getenv("DATABASE_URL")
    if not database_url:
        missing.append("DATABASE_URL")
    secret_key = _getenv("SECRET_KEY")
    if not secret_key:
        missing.append("SECRET_KEY")
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )

    g_shift_cal_id = _getenv("G_SHIFT_CAL_ID")
    if g_shift_cal_id and not _CAL_ID_RE.fullmatch(g_shift_cal_id):
        raise RuntimeError("Invalid G_SHIFT_CAL_ID format")

    return Settings(
        DATABASE_URL=database_url,
        SECRET_KEY=secret_key,
        ALGORITHM=_getenv("ALGORITHM", "HS256"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(_getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        PDF_UPLOAD_ROOT=_getenv("PDF_UPLOAD_ROOT", "uploads/pdfs"),
        GOOGLE_CREDENTIALS_JSON=_getenv("GOOGLE_CREDENTIALS_JSON"),
        G_SHIFT_CAL_ID=g_shift_cal_id,
        GOOGLE_CALENDAR_ID=_getenv("GOOGLE_CALENDAR_ID"),
        GOOGLE_CLIENT_ID=_getenv("GOOGLE_CLIENT_ID"),
        CORS_ORIGINS=_getenv("CORS_ORIGINS", "*"),
        LOG_LEVEL=_getenv("LOG_LEVEL", "INFO"),
    )


settings = load_settings()


def reload_settings() -> None:
    """Reload settings from environment variables (mainly for tests)."""
    global settings
    settings = load_settings()
