from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.determinazione import DeterminazioneCreate, DeterminazioneResponse
from app.crud import determinazione

router = APIRouter(prefix="/determinazioni", tags=["Determinazioni"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=DeterminazioneResponse)
def create_determinazione_route(data: DeterminazioneCreate, db: Session = Depends(get_db)):
    return determinazione.create_determinazione(db, data)

@router.get("/", response_model=list[DeterminazioneResponse])
def list_determinazioni(db: Session = Depends(get_db)):
    return determinazione.get_determinazioni(db)

@router.put("/{determinazione_id}", response_model=DeterminazioneResponse)
def update_determinazione_route(determinazione_id: str, data: DeterminazioneCreate, db: Session = Depends(get_db)):
    db_det = determinazione.update_determinazione(db, determinazione_id, data)
    if not db_det:
        raise HTTPException(status_code=404, detail="Determinazione not found")
    return db_det

@router.delete("/{determinazione_id}")
def delete_determinazione_route(determinazione_id: str, db: Session = Depends(get_db)):
    db_det = determinazione.delete_determinazione(db, determinazione_id)
    if not db_det:
        raise HTTPException(status_code=404, detail="Determinazione not found")
    return {"ok": True}
