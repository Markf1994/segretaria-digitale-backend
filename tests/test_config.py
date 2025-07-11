import pytest
from app import config


def test_load_settings_rejects_bad_calendar_id(monkeypatch):
    monkeypatch.setenv("G_SHIFT_CAL_ID", "bad")
    with pytest.raises(RuntimeError, match="G_SHIFT_CAL_ID"):
        config.load_settings()


def test_load_settings_accepts_valid_calendar_id(monkeypatch):
    good = "ok123@group.calendar.google.com"
    monkeypatch.setenv("G_SHIFT_CAL_ID", good)
    settings = config.load_settings()
    assert settings.G_SHIFT_CAL_ID == good


def test_load_settings_trims_whitespace(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./db  ")
    monkeypatch.setenv("SECRET_KEY", "  secret ")
    settings = config.load_settings()
    assert settings.DATABASE_URL == "sqlite:///./db"
    assert settings.SECRET_KEY == "secret"
