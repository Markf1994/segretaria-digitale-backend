from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.event import EventCreate, EventResponse
from app.crud import event
router = APIRouter(prefix="/events", tags=["Events"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.post("/", response_model=EventResponse)
def create_event_route(data: EventCreate, db: Session = Depends(get_db)):
    return event.create_event(db, data)
@router.get("/", response_model=list[EventResponse])
def list_events(db: Session = Depends(get_db)):
    return event.get_events(db)
@router.put("/{event_id}", response_model=EventResponse)
def update_event_route(event_id: str, data: EventCreate, db: Session = Depends(get_db)):
    db_event = event.update_event(db, event_id, data)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return db_event
@router.delete("/{event_id}")
def delete_event_route(event_id: str, db: Session = Depends(get_db)):
    db_event = event.delete_event(db, event_id)
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"ok": True}
