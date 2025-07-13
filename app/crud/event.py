from sqlalchemy.orm import Session
from app.models.event import Event
from app.models.user import User
import logging

from app.config import settings
from app.services import calendar_events

logger = logging.getLogger(__name__)


def create_event(db: Session, data, user: User):
    """Insert a new :class:`Event` for ``user`` from the given schema."""
    db_event = Event(**data.dict(), user_id=user.id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    try:
        calendar_events.create_event(db_event)
    except Exception as exc:  # pragma: no cover - unexpected errors
        cal_id = settings.GOOGLE_CALENDAR_ID
        logger.error(
            "Errore sync calendario (cal_id=%s, event_id=%s): %s",
            cal_id,
            db_event.id,
            exc,
        )
    return db_event


def get_events(db: Session, user: User | None = None):
    """Retrieve events visible to ``user`` (or public if ``None``)."""
    query = db.query(Event)
    if user is None:
        return query.filter(Event.is_public == True).all()
    return query.filter((Event.is_public == True) | (Event.user_id == user.id)).all()


def update_event(db: Session, event_id: str, data, user: User):
    """Update an ``Event`` owned by ``user`` or return ``None`` if missing."""
    db_event = (
        db.query(Event).filter(Event.id == event_id, Event.user_id == user.id).first()
    )
    if not db_event:
        return None
    for key, value in data.dict().items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event


def delete_event(db: Session, event_id: str, user: User):
    """Delete the event owned by ``user`` with ``event_id`` if it exists."""
    db_event = (
        db.query(Event).filter(Event.id == event_id, Event.user_id == user.id).first()
    )
    if db_event:
        db.delete(db_event)
        db.commit()
    return db_event
