from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.dependencies import get_db
from app.schemas.segnaletica_orizzontale import (
    SegnaleticaOrizzontaleCreate,
    SegnaleticaOrizzontaleResponse,
)
from app.crud import segnaletica_orizzontale as crud
from app.services.segnaletica_orizzontale_pdf import (
    build_segnaletica_orizzontale_pdf,
)

router = APIRouter(prefix="/inventario/signage-horizontal", tags=["Inventario"])


@router.get("/years", response_model=list[int])
def get_years_route(db: Session = Depends(get_db)):
    """Return all distinct years found in ``segnaletica_orizzontale``."""
    return crud.get_years(db)


@router.get("/", response_model=list[SegnaleticaOrizzontaleResponse])
def list_records(year: int | None = None, db: Session = Depends(get_db)):
    """List signage records, optionally filtering by ``year``."""
    return crud.get_segnaletica_orizzontale(db, search=None, anno=year)


@router.post("/", response_model=SegnaleticaOrizzontaleResponse)
def create_record(data: SegnaleticaOrizzontaleCreate, db: Session = Depends(get_db)):
    return crud.create_segnaletica_orizzontale(db, data)


@router.put("/{record_id}", response_model=SegnaleticaOrizzontaleResponse)
def update_record(record_id: str, data: SegnaleticaOrizzontaleCreate, db: Session = Depends(get_db)):
    db_obj = crud.update_segnaletica_orizzontale(db, record_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Segnaletica orizzontale not found")
    return db_obj


@router.delete("/{record_id}")
def delete_record(record_id: str, db: Session = Depends(get_db)):
    db_obj = crud.delete_segnaletica_orizzontale(db, record_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Segnaletica orizzontale not found")
    return {"ok": True}


@router.get("/pdf")
def signage_horizontal_pdf(
    year: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Return a signage plan PDF for the given ``year``."""
    pdf_path, html_path = build_segnaletica_orizzontale_pdf(db, year)
    background_tasks.add_task(os.remove, pdf_path)
    background_tasks.add_task(os.remove, html_path)
    filename = f"signage_horizontal_{year}.pdf"
    return FileResponse(pdf_path, filename=filename)
