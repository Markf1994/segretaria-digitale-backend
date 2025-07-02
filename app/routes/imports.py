from fastapi import APIRouter, UploadFile, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.background import BackgroundTask
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
):
    """Import Excel shifts, sync them and return a PDF summary."""
    # 1 – save temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # 2 – parse Excel -> TurnoIn payloads
    rows = parse_excel(tmp_path)

    # 3 – store/update each shift (DB + Google Calendar)
    for payload in rows:
        crud_turno.upsert_turno(db, TurnoIn(**payload))

    # 4 – generate PDF summary
    pdf_path, html_path = df_to_pdf(rows)

    def cleanup(*paths: str) -> None:
        for p in paths:
            try:
                os.remove(p)
            except FileNotFoundError:
                pass

    background = BackgroundTask(cleanup, tmp_path, pdf_path, html_path)
    return FileResponse(
        pdf_path,
        filename="turni_settimana.pdf",
        background=background,
    )
