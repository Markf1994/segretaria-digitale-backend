from sqlalchemy.orm import Session
from app.models.event import Event
def create_event(db: Session, data):
    db_event = Event(**data.dict())
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event
def get_events(db: Session):
    return db.query(Event).all()
def update_event(db: Session, event_id: str, data):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if not db_event:
        return None
    for key, value in data.dict().items():
        setattr(db_event, key, value)
    db.commit()
    return db_event
def delete_event(db: Session, event_id: str):
    db_event = db.query(Event).filter(Event.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
    return db_event