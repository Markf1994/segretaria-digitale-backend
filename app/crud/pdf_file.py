import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.pdf_file import PdfFile
from app.schemas.pdf_file import PdfFileIn


def get_upload_root() -> str:
    """Return the path where PDF files are stored."""
    root = os.getenv("PDF_UPLOAD_ROOT", "uploads/pdfs")
    os.makedirs(root, exist_ok=True)
    return root


def create(db: Session, *, obj_in: PdfFileIn, file: UploadFile) -> PdfFile:
    ext = os.path.splitext(file.filename)[1]
    fname = f"{uuid.uuid4()}{ext}"
    path = os.path.join(get_upload_root(), fname)
    with open(path, "wb") as fh:
        shutil.copyfileobj(file.file, fh)

    file.file.close()

    db_obj = PdfFile(title=obj_in.title, filename=fname)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_multi(db: Session):
    return db.query(PdfFile).order_by(PdfFile.uploaded_at.desc()).all()


def get(db: Session, pdf_id: str) -> PdfFile | None:
    return db.query(PdfFile).filter(PdfFile.id == pdf_id).first()
