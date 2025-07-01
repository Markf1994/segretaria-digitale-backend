import importlib
import os

def test_sqlite_connect_args(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    db = importlib.reload(importlib.import_module("app.database"))
    assert db.CONNECT_ARGS == {"check_same_thread": False}

