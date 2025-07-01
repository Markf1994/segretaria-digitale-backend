from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.turno import TurnoIn, TurnoResponse
from app.crud import turno as crud_turno

router = APIRouter(prefix="/turni", tags=["Turni"])


@router.post("/", response_model=TurnoResponse)
def upsert_turno_route(
    data: TurnoIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return crud_turno.upsert_turno(db, data)


@router.delete("/{turno_id}")
def delete_turno_route(
    turno_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    crud_turno.remove_turno(db, turno_id)
    return {"ok": True}
