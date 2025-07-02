import types
from datetime import date, time, timedelta

from app.services import gcal


def test_iso_dt_current_offset():
    d = date(2023, 7, 1)
    t = time(8, 30)
    result = gcal.iso_dt(d, t)
    offset = gcal.datetime.now().astimezone().utcoffset()
    if offset is None:
        expected = "+00:00"
    else:
        minutes = int(offset.total_seconds() // 60)
        sign = "+" if minutes >= 0 else "-"
        h, m = divmod(abs(minutes), 60)
        expected = f"{sign}{h:02d}:{m:02d}"
    assert result.endswith(expected)


def test_iso_dt_uses_patched_timezone(monkeypatch):
    class DummyNow:
        def astimezone(self):
            class DummyOffset:
                def utcoffset(self, *args, **kwargs):
                    return timedelta(hours=9, minutes=30)
            return DummyOffset()

    class DummyDateTime:
        @classmethod
        def now(cls):
            return DummyNow()

    monkeypatch.setattr(gcal, "datetime", DummyDateTime)

    res = gcal.iso_dt(date(2023, 1, 1), time(0, 0))
    assert res.endswith("+09:30")
