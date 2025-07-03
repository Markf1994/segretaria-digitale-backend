from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.schemas.pdf_file import PdfFileOut, PdfFileIn
from app.crud import pdf_file as crud_pdf_file

router = APIRouter(prefix="/pdf-files", tags=["PDF Files"])


@router.post("/", response_model=PdfFileOut, status_code=201)
async def upload_pdf_file(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Il file deve essere un PDF")
    obj_in = PdfFileIn(title=title, file=file)
    return crud_pdf_file.create(db, obj_in=obj_in, file=file)


@router.get("/", response_model=List[PdfFileOut])
def list_pdf_files(db: Session = Depends(get_db)):
    return crud_pdf_file.get_multi(db)


@router.get("/{pdf_id}")
def download_pdf_file(pdf_id: str, db: Session = Depends(get_db)):
    pdf = crud_pdf_file.get(db, pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="PDF not found")

    path = Path(crud_pdf_file.get_upload_root()) / pdf.filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    return FileResponse(str(path), media_type="application/pdf", filename=pdf.filename)
