from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from app.dependencies import get_db
from app.schemas.pdffile import PDFFileCreate, PDFFileResponse
from app.crud import pdffile as crud_pdffile
import os

router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.get("/", response_model=List[PDFFileResponse])
def list_pdfs(db: Session = Depends(get_db)):
    return crud_pdffile.get_multi(db)


@router.post("/", response_model=PDFFileResponse, status_code=201)
async def upload_pdf(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Il file deve essere un PDF")
    return crud_pdffile.create(db, obj_in=PDFFileCreate(title=title), file=file)


@router.get("/{filename}")
def get_pdf(filename: str):
    """Return a previously uploaded PDF by filename."""
    from pathlib import Path
    from app.crud.pdffile import get_upload_root

    # Prevent path traversal attacks by stripping directory components
    safe_name = Path(filename).name
    if safe_name != filename:
        # Invalid filename with path components
        raise HTTPException(status_code=404)

    root = Path(get_upload_root())
    path = root / safe_name
    if not path.exists():
        raise HTTPException(status_code=404)
    return FileResponse(str(path), media_type="application/pdf", filename=safe_name)
