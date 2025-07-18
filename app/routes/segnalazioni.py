from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.segnalazione import (
    SegnalazioneCreate,
    SegnalazioneResponse,
    SegnalazioneUpdate,
    StatoSegnalazione,
)
from app.crud import segnalazione as crud

router = APIRouter(prefix="/segnalazioni", tags=["Segnalazioni"])


@router.post("/", response_model=SegnalazioneResponse)
def create_segnalazione_route(
    data: SegnalazioneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.create_segnalazione(db, data, current_user)


@router.get("/", response_model=list[SegnalazioneResponse])
def list_segnalazioni(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.get_segnalazioni(db, current_user)


@router.get("/by-stato", response_model=list[SegnalazioneResponse])
def list_segnalazioni_by_stato(
    stato: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    parts = [s.strip() for s in stato.split(",") if s.strip()]
    try:
        stati = [StatoSegnalazione(p).value for p in parts]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return crud.get_segnalazioni_by_stato(db, current_user, stati)


@router.get("/{segnalazione_id}", response_model=SegnalazioneResponse)
def get_segnalazione_route(
    segnalazione_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_obj = crud.get_segnalazione(db, segnalazione_id, current_user)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Segnalazione not found")
    return db_obj


@router.put("/{segnalazione_id}", response_model=SegnalazioneResponse)
def update_segnalazione_route(
    segnalazione_id: str,
    data: SegnalazioneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_obj = crud.update_segnalazione(db, segnalazione_id, data, current_user)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Segnalazione not found")
    return db_obj


@router.patch("/{segnalazione_id}", response_model=SegnalazioneResponse)
def patch_segnalazione_route(
    segnalazione_id: str,
    data: SegnalazioneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_obj = crud.patch_segnalazione(db, segnalazione_id, data, current_user)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Segnalazione not found")
    return db_obj


@router.delete("/{segnalazione_id}")
def delete_segnalazione_route(
    segnalazione_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_obj = crud.delete_segnalazione(db, segnalazione_id, current_user)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Segnalazione not found")
    return {"ok": True}
