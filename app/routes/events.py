from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.event import EventCreate, EventResponse
from app.crud import event
router = APIRouter(prefix="/events", tags=["Events"],trailing_slash=False)

@router.post("/", response_model=EventResponse)
def create_event_route(data: EventCreate, db: Session = Depends(get_db)):
    """Create a new event and return the stored model."""
    return event.create_event(db, data)
@router.get("/", response_model=list[EventResponse])
def list_events(db: Session = Depends(get_db)):
    """Retrieve all events from the database."""
    return event.get_events(db)
@router.put("/{event_id}", response_model=EventResponse)
def update_event_route(event_id: str, data: EventCreate, db: Session = Depends(get_db)):
    """Update an event by ``event_id`` or raise 404 if missing."""
    db_event = event.update_event(db, event_id, data)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event
@router.delete("/{event_id}")
def delete_event_route(event_id: str, db: Session = Depends(get_db)):
    """Delete an event if present and confirm deletion."""
    db_event = event.delete_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"ok": True}
