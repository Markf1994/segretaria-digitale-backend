from fastapi import APIRouter, Depends, HTTPException, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import tempfile
import os
from datetime import date

from app.dependencies import get_db
from app.schemas.segnaletica_orizzontale import (
    SegnaleticaOrizzontaleCreate,
    SegnaleticaOrizzontaleResponse,
)
from app.crud import segnaletica_orizzontale as crud
from app.services.segnaletica_orizzontale_import import parse_excel
from app.services.segnaletica_orizzontale_pdf import build_segnaletica_orizzontale_pdf

router = APIRouter(prefix="/segnaletica-orizzontale", tags=["Segnaletica Orizzontale"])


@router.post("/", response_model=SegnaleticaOrizzontaleResponse)
def create_segnaletica_orizzontale_route(
    data: SegnaleticaOrizzontaleCreate, db: Session = Depends(get_db)
):
    if data.anno is None:
        data.anno = date.today().year
    return crud.create_segnaletica_orizzontale(db, data)


@router.get("/", response_model=list[SegnaleticaOrizzontaleResponse])
def list_segnaletica_orizzontale(
    search: str | None = None,
    anno: int | None = None,
    db: Session = Depends(get_db),
):
    return crud.get_segnaletica_orizzontale(db, search=search, anno=anno)


@router.put("/{so_id}", response_model=SegnaleticaOrizzontaleResponse)
def update_segnaletica_orizzontale_route(
    so_id: str, data: SegnaleticaOrizzontaleCreate, db: Session = Depends(get_db)
):
    db_obj = crud.update_segnaletica_orizzontale(db, so_id, data)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Segnaletica orizzontale not found")
    return db_obj


@router.delete("/{so_id}")
def delete_segnaletica_orizzontale_route(so_id: str, db: Session = Depends(get_db)):
    db_obj = crud.delete_segnaletica_orizzontale(db, so_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Segnaletica orizzontale not found")
    return {"ok": True}


@router.post("/import")
async def import_segnaletica_orizzontale(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        rows = parse_excel(tmp_path)
        descrizioni = []
        azienda = rows[0]["azienda"] if rows else ""
        for payload in rows:
            create_segnaletica_orizzontale_route(
                SegnaleticaOrizzontaleCreate(**payload), db
            )
            descrizioni.append(payload["descrizione"])
        pdf_path, html_path = build_segnaletica_orizzontale_pdf(descrizioni, azienda, date.today().year)
        background_tasks.add_task(os.remove, pdf_path)
        background_tasks.add_task(os.remove, html_path)
        return FileResponse(pdf_path, filename="segnaletica_orizzontale.pdf")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
