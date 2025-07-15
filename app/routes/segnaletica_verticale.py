from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.segnaletica_verticale import (
    SegnaleticaVerticaleCreate,
    SegnaleticaVerticaleResponse,
)
from app.crud import segnaletica_verticale as crud

router = APIRouter(prefix="/segnaletica-verticale", tags=["Segnaletica Verticale"])


@router.post("/", response_model=SegnaleticaVerticaleResponse)
def create_segnaletica_verticale_route(
    data: SegnaleticaVerticaleCreate, db: Session = Depends(get_db)
):
    return crud.create_segnaletica_verticale(db, data)


@router.get("/", response_model=list[SegnaleticaVerticaleResponse])
def list_segnaletica_verticale(
    search: str | None = None,
    anno: int | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_segnaletica_verticale(db, search=search, anno=anno)


@router.put("/{sv_id}", response_model=SegnaleticaVerticaleResponse)
def update_segnaletica_verticale_route(
    sv_id: str, data: SegnaleticaVerticaleCreate, db: Session = Depends(get_db)
):
    db_obj = crud.update_segnaletica_verticale(db, sv_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Segnaletica verticale not found")
    return db_obj


@router.delete("/{sv_id}")
def delete_segnaletica_verticale_route(sv_id: str, db: Session = Depends(get_db)):
    db_obj = crud.delete_segnaletica_verticale(db, sv_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Segnaletica verticale not found")
    return {"ok": True}
