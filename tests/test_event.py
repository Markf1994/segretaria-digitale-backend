from datetime import datetime
from app.crud import event as event_crud
from app.schemas.event import EventCreate


def test_create_event(db_session):
    data = EventCreate(titolo="Test", descrizione="desc", data_ora=datetime.utcnow(), is_public=True)
    new_event = event_crud.create_event(db_session, data)
    assert new_event.titolo == "Test"
    assert new_event.id is not None
