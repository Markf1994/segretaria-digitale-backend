from dataclasses import dataclass
import os


@dataclass
class Settings:
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    PDF_UPLOAD_ROOT: str = "uploads/pdfs"
    GOOGLE_CREDENTIALS_JSON: str | None = None
    G_EVENT_CAL_ID: str | None = None
    G_SHIFT_CAL_ID: str | None = None
    GOOGLE_CALENDAR_ID: str | None = None
    CORS_ORIGINS: str = "*"
    LOG_LEVEL: str = "INFO"


def load_settings() -> Settings:
    missing = []
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        missing.append("DATABASE_URL")
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        missing.append("SECRET_KEY")
    if missing:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )

    return Settings(
        DATABASE_URL=database_url,
        SECRET_KEY=secret_key,
        ALGORITHM=os.getenv("ALGORITHM", "HS256"),
        ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
        PDF_UPLOAD_ROOT=os.getenv("PDF_UPLOAD_ROOT", "uploads/pdfs"),
        GOOGLE_CREDENTIALS_JSON=os.getenv("GOOGLE_CREDENTIALS_JSON"),
        G_EVENT_CAL_ID=os.getenv("G_EVENT_CAL_ID"),
        G_SHIFT_CAL_ID=os.getenv("G_SHIFT_CAL_ID"),
        GOOGLE_CALENDAR_ID=os.getenv("GOOGLE_CALENDAR_ID"),
        CORS_ORIGINS=os.getenv("CORS_ORIGINS", "*"),
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
    )


settings = load_settings()


def reload_settings() -> None:
    """Reload settings from environment variables (mainly for tests)."""
    global settings
    settings = load_settings()
