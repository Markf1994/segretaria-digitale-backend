import os
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app

client = TestClient(app)


class DummyService:
    def __init__(self, events_response=None, raise_error=False):
        self.events_response = events_response or {"items": []}
        self.raise_error = raise_error
        self.received_timeMin = None

    class EventsResource:
        def __init__(self, outer):
            self.outer = outer

        class _ListCall:
            def __init__(self, outer, timeMin=None, **kwargs):
                outer.outer.received_timeMin = timeMin
                self.outer = outer

            def execute(self):
                if self.outer.outer.raise_error:
                    raise Exception("boom")
                return self.outer.outer.events_response

        def list(self, calendarId="primary", timeMin=None, singleEvents=True, orderBy="startTime"):
            return self._ListCall(self, timeMin=timeMin)

    def events(self):
        return self.EventsResource(self)


def test_calendar_list(monkeypatch):
    service = DummyService(events_response={"items": [{"id": "1", "summary": "a"}]})
    monkeypatch.setattr("app.routes.calendar.get_calendar_service", lambda: service)
    res = client.get("/calendar")
    assert res.status_code == 200
    assert res.json() == [{"id": "1", "summary": "a"}]
    assert service.received_timeMin is not None


def test_calendar_error(monkeypatch):
    service = DummyService(raise_error=True)
    monkeypatch.setattr("app.routes.calendar.get_calendar_service", lambda: service)
    res = client.get("/calendar")
    assert res.status_code == 500

