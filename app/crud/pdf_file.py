import os
import uuid
import shutil
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.models.pdf_file import PDFFile
from app.schemas.pdf_file import PDFFileCreate


def get_upload_root() -> str:
    """Return the path where PDF files should be stored."""
    root = os.getenv("PDF_UPLOAD_ROOT", "uploads/pdfs")
    os.makedirs(root, exist_ok=True)
    return root


def create(db: Session, *, obj_in: PDFFileCreate, file: UploadFile) -> PDFFile:
    ext = os.path.splitext(file.filename)[1]
    fname = f"{uuid.uuid4()}{ext}"
    path = os.path.join(get_upload_root(), fname)
    with open(path, "wb") as fp:
        shutil.copyfileobj(file.file, fp)

    # Explicitly close the uploaded file to release resources
    file.file.close()

    db_obj = PDFFile(title=obj_in.title, filename=fname)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_multi(db: Session):
    return db.query(PDFFile).order_by(PDFFile.uploaded_at.desc()).all()
