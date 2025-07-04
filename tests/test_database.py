import importlib
import pytest
from app import config

def test_sqlite_connect_args():
    original = config.settings.DATABASE_URL
    config.settings.DATABASE_URL = "sqlite:///./test.db"
    db = importlib.reload(importlib.import_module("app.database"))
    config.settings.DATABASE_URL = original
    assert db.CONNECT_ARGS == {"check_same_thread": False}


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

