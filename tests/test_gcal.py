import json
from datetime import date, time, timedelta

import pytest

from app.services import gcal


def test_iso_dt_current_offset():
    d = date(2023, 7, 1)
    t = time(8, 30)
    result = gcal.iso_dt(d, t)
    offset = gcal.datetime.combine(d, t).astimezone().utcoffset()
    if offset is None:
        expected = "+00:00"
    else:
        minutes = int(offset.total_seconds() // 60)
        sign = "+" if minutes >= 0 else "-"
        h, m = divmod(abs(minutes), 60)
        expected = f"{sign}{h:02d}:{m:02d}"
    assert result.endswith(expected)


def test_iso_dt_uses_patched_timezone(monkeypatch):
    class DummyCombined:
        def astimezone(self):
            class DummyOffset:
                def utcoffset(self, *args, **kwargs):
                    return timedelta(hours=9, minutes=30)

            return DummyOffset()

    class DummyDateTime:
        @classmethod
        def combine(cls, d, t):
            return DummyCombined()

    monkeypatch.setattr(gcal, "datetime", DummyDateTime)

    res = gcal.iso_dt(date(2023, 1, 1), time(0, 0))
    assert res.endswith("+09:30")


def test_get_client_from_json_string(monkeypatch):
    """``get_client`` should parse JSON credentials strings."""
    dummy_info = {
        "type": "service_account",
        "client_email": "bot@example.com",
        "private_key": "---KEY---",
        "token_uri": "https://oauth2.example/token",
    }

    captured = {}

    def fake_from_info(info, scopes=None):
        captured["info"] = info
        return "CREDS"

    monkeypatch.setattr(
        gcal.service_account.Credentials,
        "from_service_account_info",
        fake_from_info,
    )
    monkeypatch.setattr(gcal, "build", lambda *a, **k: "CLIENT")
    monkeypatch.setattr(
        gcal.settings, "GOOGLE_CREDENTIALS_JSON", json.dumps(dummy_info)
    )

    gcal.get_client.cache_clear()
    result = gcal.get_client()
    assert result == "CLIENT"
    assert captured["info"] == dummy_info


def test_sync_shift_event_requires_calendar_id(monkeypatch):
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", None)
    with pytest.raises(RuntimeError, match="G_SHIFT_CAL_ID is not configured"):
        gcal.sync_shift_event(object())


def test_delete_shift_event_requires_calendar_id(monkeypatch):
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", None)
    with pytest.raises(RuntimeError, match="G_SHIFT_CAL_ID is not configured"):
        gcal.delete_shift_event("dummy")


@pytest.mark.parametrize("status", [404, 400])
def test_delete_shift_event_ignores_known_errors(monkeypatch, status):
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "cal")

    class DummyEvents:
        def delete(self, calendarId=None, eventId=None):
            resp = type("Resp", (), {"status": status})()
            raise gcal.gerr.HttpError(resp=resp, content=b"")

    class DummyClient:
        def events(self):
            return DummyEvents()

    monkeypatch.setattr(gcal, "get_client", lambda: DummyClient())

    # Should not raise for 404 or 400
    gcal.delete_shift_event("dummy")


def test_delete_shift_event_propagates_other_errors(monkeypatch):
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "cal")

    class DummyEvents:
        def delete(self, calendarId=None, eventId=None):
            resp = type("Resp", (), {"status": 500})()
            raise gcal.gerr.HttpError(resp=resp, content=b"")

    class DummyClient:
        def events(self):
            return DummyEvents()

    monkeypatch.setattr(gcal, "get_client", lambda: DummyClient())

    with pytest.raises(gcal.gerr.HttpError):
        gcal.delete_shift_event("dummy")
