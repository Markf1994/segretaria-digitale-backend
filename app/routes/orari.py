from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.turno import TurnoIn, TurnoOut
from app.crud import turno as crud

router = APIRouter(prefix="/orari", tags=["Orari"])


@router.post("/", response_model=TurnoOut)
def save_turno(payload: TurnoIn, db: Session = Depends(get_db)):
    """Create or update a shift record."""
    return crud.upsert_turno(db, payload)


@router.delete("/{turno_id}")
def delete_turno(turno_id: UUID, db: Session = Depends(get_db)):
    """Remove a shift by id."""
    crud.remove_turno(db, turno_id)
    return {"ok": True}
