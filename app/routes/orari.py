from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.turno import TurnoIn, TurnoOut
from app.crud import turno as crud_turno

router = APIRouter(prefix="/orari", tags=["Orari"])

@router.post("", response_model=TurnoOut)
def save_turno(payload: TurnoIn, db: Session = Depends(get_db)):
    """Create or update a turno."""
    return crud_turno.upsert_turno(db, payload)

@router.delete("/{turno_id}")
def delete_turno(turno_id: str, db: Session = Depends(get_db)):
    """Delete a turno."""
    crud_turno.remove_turno(db, turno_id)
    return {"ok": True}

