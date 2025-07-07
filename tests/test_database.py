import importlib
import pytest
from app import config


def test_sqlite_connect_args():
    original = config.settings.DATABASE_URL
    config.settings.DATABASE_URL = "sqlite:///./test.db"
    db = importlib.reload(importlib.import_module("app.database"))
    config.settings.DATABASE_URL = original
    assert db.CONNECT_ARGS == {"check_same_thread": False}


def test_postgres_default_sslmode(monkeypatch):
    original = config.settings.DATABASE_URL
    config.settings.DATABASE_URL = "postgresql://user:pass@localhost/db"
    db = importlib.reload(importlib.import_module("app.database"))
    config.settings.DATABASE_URL = original
    assert db.CONNECT_ARGS == {"sslmode": "require"}


def test_postgres_url_has_sslmode(monkeypatch):
    original = config.settings.DATABASE_URL
    config.settings.DATABASE_URL = "postgresql://user:pass@localhost/db?sslmode=disable"
    db = importlib.reload(importlib.import_module("app.database"))
    config.settings.DATABASE_URL = original
    assert db.CONNECT_ARGS == {}


def test_postgres_env_override(monkeypatch):
    original = config.settings.DATABASE_URL
    config.settings.DATABASE_URL = "postgresql://user:pass@localhost/db"
    monkeypatch.setenv("DATABASE_SSLMODE", "disable")
    db = importlib.reload(importlib.import_module("app.database"))
    monkeypatch.delenv("DATABASE_SSLMODE", raising=False)
    config.settings.DATABASE_URL = original
    assert db.CONNECT_ARGS == {"sslmode": "disable"}


def test_turno_invalid_user_fk(setup_db):
    from datetime import date, time
    from sqlalchemy.exc import IntegrityError
    from app.database import SessionLocal
    from app.models.turno import Turno

    db = SessionLocal()
    bad_turno = Turno(
        user_id="missing",
        giorno=date(2023, 1, 1),
        inizio_1=time(8, 0, 0),
        fine_1=time(12, 0, 0),
        tipo="NORMALE",
        note="",
    )
    db.add(bad_turno)
    with pytest.raises(IntegrityError):
        db.commit()
    db.close()
