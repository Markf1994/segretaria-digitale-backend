from fastapi import APIRouter, UploadFile, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import tempfile
import os

from app.dependencies import get_db
from app.schemas.turno import TurnoIn
from app.crud import turno as crud_turno
from app.services.excel_import import parse_excel, df_to_pdf

router = APIRouter(prefix="/import", tags=["Import"])


@router.post("/xlsx")
async def import_xlsx(
    file: UploadFile,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks,
):
    """Import Excel shifts, sync them and return a PDF summary."""
    # 1 – save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 2 – parse Excel -> TurnoIn payloads
    try:
        rows = parse_excel(tmp_path, db=db)
    except HTTPException:
        os.remove(tmp_path)
        raise

    # 3 – store/update each shift (DB + Google Calendar)
    for payload in rows:
        crud_turno.upsert_turno(db, TurnoIn(**payload))

    # 4 – generate PDF summary
    pdf_path, html_path = df_to_pdf(rows)
    background_tasks.add_task(os.remove, pdf_path)
    background_tasks.add_task(os.remove, html_path)
    background_tasks.add_task(os.remove, tmp_path)
    return FileResponse(pdf_path, filename="turni_settimana.pdf")
