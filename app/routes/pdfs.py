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
    from app.crud.pdffile import get_upload_root
    path = os.path.join(get_upload_root(), filename)
    if not os.path.exists(path):
        raise HTTPException(404)
    return FileResponse(path, media_type="application/pdf", filename=filename)
