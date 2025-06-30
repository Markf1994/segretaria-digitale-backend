import os
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.main import app

client = TestClient(app)


class DummyService:
    def __init__(self, files_response=None, raise_error=False):
        self.files_response = files_response or {"files": []}
        self.raise_error = raise_error
        self.received_q = None

    class FilesResource:
        def __init__(self, outer):
            self.outer = outer

        class _ListCall:
            def __init__(self, outer, q):
                outer.outer.received_q = q
                self.outer = outer

            def execute(self):
                if self.outer.outer.raise_error:
                    raise Exception("boom")
                return self.outer.outer.files_response

        def list(self, q=None, fields=None):
            return self._ListCall(self, q)

    def files(self):
        return self.FilesResource(self)


def test_drive_list(monkeypatch):
    service = DummyService(files_response={"files": [{"id": "1", "name": "a"}]})
    monkeypatch.setattr("app.routes.drive.get_drive_service", lambda: service)
    os.environ["GOOGLE_DRIVE_FOLDER_ID"] = "folder"
    res = client.get("/drive")
    assert res.status_code == 200
    assert res.json() == [{"id": "1", "name": "a"}]
    assert service.received_q == "'folder' in parents"


def test_drive_error(monkeypatch):
    service = DummyService(raise_error=True)
    monkeypatch.setattr("app.routes.drive.get_drive_service", lambda: service)
    if "GOOGLE_DRIVE_FOLDER_ID" in os.environ:
        del os.environ["GOOGLE_DRIVE_FOLDER_ID"]
    res = client.get("/drive")
    assert res.status_code == 500
