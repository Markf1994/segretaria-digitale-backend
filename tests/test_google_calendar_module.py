import json
from datetime import datetime
import types


from app.services import google_calendar


def test_list_events_between_success(monkeypatch):
    google_calendar.get_service.cache_clear()
    dummy_info = {"type": "service_account"}
    monkeypatch.setattr(google_calendar.settings, "GOOGLE_CREDENTIALS_JSON", json.dumps(dummy_info))
    monkeypatch.setattr(google_calendar.settings, "GOOGLE_CALENDAR_ID", "CAL")

    monkeypatch.setattr(
        "google.oauth2.service_account.Credentials.from_service_account_info",
        lambda info, scopes=None: "CREDS",
    )
    monkeypatch.setattr(
        "google.oauth2.credentials.Credentials.from_authorized_user_info",
        lambda info: "CREDS",
    )

    captured = {}

    class DummyEvents:
        def list(self, **kwargs):
            captured["params"] = kwargs

            class Runner:
                def execute(self_inner):
                    return {
                        "items": [
                            {
                                "id": "1",
                                "summary": "A",
                                "description": "desc",
                                "start": {"dateTime": "2023-01-02T10:00:00Z"},
                                "colorId": "1",
                            },
                            {
                                "id": "2",
                                "summary": "B",
                                "description": "",
                                "start": {"date": "2023-01-03"},
                                "colorId": "2",
                            },
                        ]
                    }

            return Runner()

    class DummyService:
        def events(self):
            return types.SimpleNamespace(list=DummyEvents().list)

    monkeypatch.setattr("googleapiclient.discovery.build", lambda *a, **k: DummyService())

    start = datetime(2023, 1, 1)
    end = datetime(2023, 1, 7)

    result = google_calendar.list_events_between(start, end)

    assert captured["params"]["calendarId"] == "CAL"
    assert captured["params"]["timeMin"].startswith("2023-01-01T")
    assert captured["params"]["timeMax"].startswith("2023-01-07T")
    assert len(result) == 2
    assert result[0]["id"] == "1"
    assert isinstance(result[0]["data_ora"], datetime)
    assert result[1]["data_ora"].date() == datetime(2023, 1, 3).date()
    assert result[0]["colorId"] == "1"
    assert result[1]["colorId"] == "2"


def test_list_events_between_missing_config(monkeypatch):
    google_calendar.get_service.cache_clear()
    monkeypatch.setattr(google_calendar.settings, "GOOGLE_CREDENTIALS_JSON", None)
    monkeypatch.setattr(google_calendar.settings, "GOOGLE_CALENDAR_ID", None)

    called = {}

    def fail_build(*a, **k):
        called["yes"] = True
        raise AssertionError

    monkeypatch.setattr("googleapiclient.discovery.build", fail_build)

    result = google_calendar.list_events_between(datetime.utcnow(), datetime.utcnow())

    assert result == []
    assert "yes" not in called
