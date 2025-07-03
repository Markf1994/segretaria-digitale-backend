from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse

from app.dependencies import get_db, get_optional_user
from app.models.user import User
from app.schemas.pdf_file import PDFFileCreate, PDFFileResponse
from app.crud import pdf_file as crud_pdf_file

router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.get("/", response_model=List[PDFFileResponse])
def list_pdfs(db: Session = Depends(get_db)):
    return crud_pdf_file.get_multi(db)


@router.post("/", response_model=PDFFileResponse, status_code=201)
async def upload_pdf(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Il file deve essere un PDF")
    return crud_pdf_file.create(
        db, obj_in=PDFFileCreate(title=title), file=file, user=current_user
    )


@router.get("/{filename}")
def get_pdf(
    filename: str,
    current_user: User | None = Depends(get_optional_user),
):
    """Return a previously uploaded PDF by filename."""
    from fastapi import HTTPException
    from pathlib import Path

    try:
        path = crud_pdf_file.get_file_path(filename, user=current_user)
    except FileNotFoundError:
        raise HTTPException(status_code=404) from None

    return FileResponse(
        path, media_type="application/pdf", filename=Path(path).name
    )
