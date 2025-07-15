from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.segnaletica_temporanea import (
    SegnaleticaTemporaneaCreate,
    SegnaleticaTemporaneaResponse,
)
from app.crud import segnaletica_temporanea as crud

router = APIRouter(prefix="/segnaletica-temporanea", tags=["Segnaletica Temporanea"])


@router.post("/", response_model=SegnaleticaTemporaneaResponse)
def create_segnaletica_temporanea_route(
    data: SegnaleticaTemporaneaCreate, db: Session = Depends(get_db)
):
    return crud.create_segnaletica_temporanea(db, data)


@router.get("/", response_model=list[SegnaleticaTemporaneaResponse])
def list_segnaletica_temporanea(
    search: str | None = None,
    anno: int | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_segnaletica_temporanea(db, search=search, anno=anno)


@router.put("/{st_id}", response_model=SegnaleticaTemporaneaResponse)
def update_segnaletica_temporanea_route(
    st_id: str, data: SegnaleticaTemporaneaCreate, db: Session = Depends(get_db)
):
    db_obj = crud.update_segnaletica_temporanea(db, st_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Segnaletica temporanea not found")
    return db_obj


@router.delete("/{st_id}")
def delete_segnaletica_temporanea_route(st_id: str, db: Session = Depends(get_db)):
    db_obj = crud.delete_segnaletica_temporanea(db, st_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Segnaletica temporanea not found")
    return {"ok": True}
