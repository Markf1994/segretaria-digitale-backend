from fastapi import APIRouter, UploadFile, Depends, BackgroundTasks, HTTPException
import logging
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import tempfile
import os

from pydantic import ValidationError
from app.dependencies import get_db
from app.schemas.turno import TurnoIn
from app.crud import turno as crud_turno
from app.services.excel_import import parse_excel, df_to_pdf

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/import", tags=["Import"])


@router.post("/xlsx")
async def import_xlsx(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Import Excel shifts, sync them and return a PDF summary."""
    tmp_path = None
    try:
        # 1 – save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # 2 – parse Excel -> TurnoIn payloads
        rows = parse_excel(tmp_path, db)

        # 3 – store/update each shift (DB + Google Calendar)
        for idx, payload in enumerate(rows):
            try:
                turno = TurnoIn(**payload)
            except ValidationError as err:
                raise HTTPException(status_code=400, detail=f"Row {idx+2}: {err}")
            crud_turno.upsert_turno(db, turno)

        # 4 – generate PDF summary
        pdf_path, html_path = df_to_pdf(rows, db)
        background_tasks.add_task(os.remove, pdf_path)
        background_tasks.add_task(os.remove, html_path)
        return FileResponse(pdf_path, filename="turni_settimana.pdf")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Errore import")
        raise HTTPException(500, f"Errore import: {e}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


@router.post("/excel", include_in_schema=False)
async def import_excel(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Alias for :func:`import_xlsx`"""
    return await import_xlsx(file=file, background_tasks=background_tasks, db=db)
