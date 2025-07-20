from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import tempfile
import logging
import datetime

from app.dependencies import get_db
from app.schemas.segnaletica_orizzontale import (
    SegnaleticaOrizzontaleCreate,
    SegnaleticaOrizzontaleResponse,
    SegnaleticaOrizzontaleUpdate,
)
from app.crud import segnaletica_orizzontale as crud
from app.services.segnaletica_orizzontale_pdf import (
    build_segnaletica_orizzontale_pdf,
)
from app.services.segnaletica_orizzontale_import import parse_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/segnaletica-orizzontale", tags=["Segnaletica Orizzontale"])


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
def update_record(
    record_id: str, data: SegnaleticaOrizzontaleUpdate, db: Session = Depends(get_db)
):
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


@router.post("/import")
async def import_signage_horizontal(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Import signage entries from a spreadsheet and return a PDF summary."""
    tmp_path = None
    year = datetime.date.today().year
    try:
        suffix = os.path.splitext(file.filename or "")[1].lower()
        if suffix not in {".csv", ".xlsx"}:
            suffix = ".xlsx"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        rows = parse_file(tmp_path)

        for payload in rows:
            crud.create_segnaletica_orizzontale(
                db, SegnaleticaOrizzontaleCreate(**payload)
            )

        pdf_path, html_path = build_segnaletica_orizzontale_pdf(db, year)
        background_tasks.add_task(os.remove, pdf_path)
        background_tasks.add_task(os.remove, html_path)
        logger.info(
            "Import segnaletica orizzontale: %d record creati per anno %d",
            len(rows),
            year,
        )
        filename = f"signage_horizontal_{year}.pdf"
        return FileResponse(pdf_path, filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Errore import")
        raise HTTPException(500, f"Errore import: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)



