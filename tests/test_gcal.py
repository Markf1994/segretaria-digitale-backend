import json
from datetime import date, time, timedelta
import types
import logging
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


def test_sync_shift_event_insert_on_bad_event_id(monkeypatch):
    """``sync_shift_event`` should insert when update fails with 400."""

    class FakeHttpError(Exception):
        def __init__(self, status):
            self.resp = types.SimpleNamespace(status=status)

    update_called = {}
    insert_called = {}

    def fake_update(**kwargs):
        class Runner:
            def execute(self_inner):
                raise FakeHttpError(400)

        update_called["called"] = True
        return Runner()

    def fake_insert(**kwargs):
        class Runner:
            def execute(self_inner):
                insert_called["called"] = True

        return Runner()

    class DummyClient:
        def events(self):
            return types.SimpleNamespace(update=fake_update, insert=fake_insert)

    monkeypatch.setattr(gcal, "get_client", lambda: DummyClient())
    monkeypatch.setattr(gcal.gerr, "HttpError", FakeHttpError, raising=False)
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "CAL")

    turno = types.SimpleNamespace(
        id="1",
        user=types.SimpleNamespace(nome="", email="bot@example.com"),
        giorno=date(2024, 1, 1),
        inizio_1=time(8, 0),
        fine_1=time(12, 0),
        inizio_2=None,
        fine_2=None,
        inizio_3=None,
        fine_3=None,
        tipo="NORMALE",
        note="",
    )

    gcal.sync_shift_event(turno)

    assert update_called.get("called") is True
    assert insert_called.get("called") is True


def test_sync_shift_event_sets_color_from_user(monkeypatch):
    captured = {}

    class DummyEvents:
        def update(self, calendarId=None, eventId=None, body=None):
            captured["color"] = body.get("colorId")
            return types.SimpleNamespace(execute=lambda: None)

    class DummyClient:
        def events(self):
            return DummyEvents()

    monkeypatch.setattr(gcal, "get_client", lambda: DummyClient())
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "CAL")

    user = types.SimpleNamespace(id="u1", nome="", email="a@example.com")
    turno = types.SimpleNamespace(
        id="1",
        user=user,
        giorno=date(2024, 1, 2),
        inizio_1=time(9, 0),
        fine_1=time(11, 0),
        inizio_2=None,
        fine_2=None,
        inizio_3=None,
        fine_3=None,
        tipo="NORMALE",
        note="",
    )

    gcal.sync_shift_event(turno)

    assert captured["color"] == gcal.color_for_user(user)


@pytest.mark.parametrize(
    "email,expected",
    [
        ("marco@comune.castione.bg.it", "1"),
        ("rossella@comune.castione.bg.it", "6"),
        ("mattia@comune.castione.bg.it", "7"),
    ],
)
def test_color_for_user_predefined_agents(email, expected):
    assert gcal.color_for_user(email) == expected


def test_color_for_user_unknown_is_deterministic():
    """Colors for unknown users should be stable."""
    assert gcal.color_for_user("bot@example.com") == "6"



class FakeHttpError(Exception):
    def __init__(self, status):
        self.resp = types.SimpleNamespace(status=status)


def _dummy_turno():
    return types.SimpleNamespace(
        id="1",
        user=types.SimpleNamespace(nome="", email="bot@example.com"),
        giorno=date(2024, 1, 1),
        inizio_1=time(8, 0),
        fine_1=time(12, 0),
        inizio_2=None,
        fine_2=None,
        inizio_3=None,
        fine_3=None,
        tipo="NORMALE",
        note="",
    )


def test_sync_shift_event_logs_day_off(monkeypatch, caplog):
    """Day-off turni should remove any calendar event and log the action."""

    deleted = {}

    def fake_delete(turno_id):
        deleted["id"] = turno_id

    monkeypatch.setattr(gcal, "delete_shift_event", fake_delete)
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "CAL")

    turno = _dummy_turno()
    turno.tipo = gcal.TipoTurno.RECUPERO.value

    with caplog.at_level(logging.INFO):
        gcal.sync_shift_event(turno)

    assert deleted.get("id") == turno.id
    assert "Removed calendar event for day off" in caplog.text


def test_sync_shift_event_logs_info_on_update_404(monkeypatch, caplog):
    """An update failure with status 404 should log an info message and insert."""

    insert_called = {}

    def fake_update(**kwargs):
        class Runner:
            def execute(self_inner):
                raise FakeHttpError(404)

        return Runner()

    def fake_insert(**kwargs):
        class Runner:
            def execute(self_inner):
                insert_called["called"] = True

        return Runner()

    class DummyClient:
        def events(self):
            return types.SimpleNamespace(update=fake_update, insert=fake_insert)

    monkeypatch.setattr(gcal, "get_client", lambda: DummyClient())
    monkeypatch.setattr(gcal.gerr, "HttpError", FakeHttpError, raising=False)
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "CAL")

    turno = _dummy_turno()

    with caplog.at_level(logging.INFO):
        gcal.sync_shift_event(turno)

    assert insert_called.get("called") is True
    assert "Update of event" in caplog.text


def test_sync_shift_event_update_error_reraised(monkeypatch, caplog):
    """Non-404 errors during update should be re-raised and logged."""

    def fake_update(**kwargs):
        class Runner:
            def execute(self_inner):
                raise FakeHttpError(500)

        return Runner()

    class DummyClient:
        def events(self):
            return types.SimpleNamespace(update=fake_update)

    monkeypatch.setattr(gcal, "get_client", lambda: DummyClient())
    monkeypatch.setattr(gcal.gerr, "HttpError", FakeHttpError, raising=False)
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "CAL")

    turno = _dummy_turno()

    with caplog.at_level(logging.ERROR):
        with pytest.raises(FakeHttpError):
            gcal.sync_shift_event(turno)

    assert "Failed to update event" in caplog.text


def test_sync_shift_event_insert_failure_reraised(monkeypatch, caplog):
    """Errors during insert should be logged and re-raised."""

    def fake_update(**kwargs):
        class Runner:
            def execute(self_inner):
                raise FakeHttpError(404)

        return Runner()

    def fake_insert(**kwargs):
        class Runner:
            def execute(self_inner):
                raise FakeHttpError(500)

        return Runner()

    class DummyClient:
        def events(self):
            return types.SimpleNamespace(update=fake_update, insert=fake_insert)

    monkeypatch.setattr(gcal, "get_client", lambda: DummyClient())
    monkeypatch.setattr(gcal.gerr, "HttpError", FakeHttpError, raising=False)
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "CAL")

    turno = _dummy_turno()

    with caplog.at_level(logging.ERROR):
        with pytest.raises(FakeHttpError):
            gcal.sync_shift_event(turno)

    assert "Failed to insert event" in caplog.text


def test_delete_shift_event_logs_info_on_404(monkeypatch, caplog):
    """Deletion errors with 404 should only log an info message."""

    def fake_delete(**kwargs):
        class Runner:
            def execute(self_inner):
                raise FakeHttpError(404)

        return Runner()

    class DummyClient:
        def events(self):
            return types.SimpleNamespace(delete=fake_delete)

    monkeypatch.setattr(gcal, "get_client", lambda: DummyClient())
    monkeypatch.setattr(gcal.gerr, "HttpError", FakeHttpError, raising=False)
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "CAL")

    with caplog.at_level(logging.INFO):
        gcal.delete_shift_event("1")

    assert "Delete of event" in caplog.text


def test_delete_shift_event_reraises_errors(monkeypatch, caplog):
    """Deletion errors other than 404 should be re-raised and logged."""

    def fake_delete(**kwargs):
        class Runner:
            def execute(self_inner):
                raise FakeHttpError(500)

        return Runner()

    class DummyClient:
        def events(self):
            return types.SimpleNamespace(delete=fake_delete)

    monkeypatch.setattr(gcal, "get_client", lambda: DummyClient())
    monkeypatch.setattr(gcal.gerr, "HttpError", FakeHttpError, raising=False)
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "CAL")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(FakeHttpError):
            gcal.delete_shift_event("1")

    assert "Failed to delete event" in caplog.text


def test_sync_shift_event_logs_info_on_update_success(monkeypatch, caplog):
    """Successful update should log an info message."""

    def fake_update(**kwargs):
        class Runner:
            def execute(self_inner):
                pass

        return Runner()

    class DummyClient:
        def events(self):
            return types.SimpleNamespace(update=fake_update)

    monkeypatch.setattr(gcal, "get_client", lambda: DummyClient())
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "CAL")

    turno = _dummy_turno()

    with caplog.at_level(logging.INFO):
        gcal.sync_shift_event(turno)

    assert "Updated event" in caplog.text


def test_sync_shift_event_logs_info_on_insert_success(monkeypatch, caplog):
    """When update fails but insert succeeds, an info message should be logged."""

    def fake_update(**kwargs):
        class Runner:
            def execute(self_inner):
                raise FakeHttpError(404)

        return Runner()

    def fake_insert(**kwargs):
        class Runner:
            def execute(self_inner):
                pass

        return Runner()

    class DummyClient:
        def events(self):
            return types.SimpleNamespace(update=fake_update, insert=fake_insert)

    monkeypatch.setattr(gcal, "get_client", lambda: DummyClient())
    monkeypatch.setattr(gcal.gerr, "HttpError", FakeHttpError, raising=False)
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "CAL")

    turno = _dummy_turno()

    with caplog.at_level(logging.INFO):
        gcal.sync_shift_event(turno)

    assert "Inserted event" in caplog.text


def test_delete_shift_event_logs_info_on_success(monkeypatch, caplog):
    """Successful deletions should be logged at info level."""

    def fake_delete(**kwargs):
        class Runner:
            def execute(self_inner):
                pass

        return Runner()

    class DummyClient:
        def events(self):
            return types.SimpleNamespace(delete=fake_delete)

    monkeypatch.setattr(gcal, "get_client", lambda: DummyClient())
    monkeypatch.setattr(gcal.settings, "G_SHIFT_CAL_ID", "CAL")

    with caplog.at_level(logging.INFO):
        gcal.delete_shift_event("1")

    assert "Deleted event" in caplog.text
