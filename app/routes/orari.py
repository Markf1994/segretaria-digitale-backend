from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.turno import TurnoIn, TurnoOut
from app.crud import turno as crud_turno

router = APIRouter(prefix="/orari", tags=["Turni"])


@router.post("/", response_model=TurnoOut)
def save_turno(
    payload: TurnoIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update a turno."""
    return crud_turno.upsert_turno(db, payload)


@router.get("/", response_model=list[TurnoOut])
def list_turni(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List turni for the authenticated user."""
    return crud_turno.get_turni(db, current_user)


@router.delete("/{turno_id}")
def delete_turno(
    turno_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a turno."""
    crud_turno.remove_turno(db, turno_id)
    return {"ok": True}
