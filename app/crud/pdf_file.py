import os
import uuid
import shutil
from sqlalchemy.orm import Session
from fastapi import UploadFile
import aiofiles
from app.models.pdf_file import PDFFile
from app.schemas.pdf_file import PDFFileCreate


def get_upload_root() -> str:
    """Return the path where PDF files should be stored."""
    root = os.getenv("PDF_UPLOAD_ROOT", "uploads/pdfs")
    os.makedirs(root, exist_ok=True)
    return root


async def create(db: Session, *, obj_in: PDFFileCreate, file: UploadFile) -> PDFFile:
    ext = os.path.splitext(file.filename)[1]
    fname = f"{uuid.uuid4()}{ext}"
    path = os.path.join(get_upload_root(), fname)

    async with aiofiles.open(path, "wb") as fp:
        while True:
            chunk = await file.read(1024 * 1024)
            if not chunk:
                break
            await fp.write(chunk)

    await file.close()

    db_obj = PDFFile(title=obj_in.title, filename=fname)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_multi(db: Session):
    return db.query(PDFFile).order_by(PDFFile.uploaded_at.desc()).all()


def delete(db: Session, *, filename: str) -> PDFFile | None:
    """Remove a ``PDFFile`` entry and delete the file from disk."""
    db_obj = db.query(PDFFile).filter(PDFFile.filename == filename).first()
    if not db_obj:
        return None

    path = os.path.join(get_upload_root(), db_obj.filename)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass

    db.delete(db_obj)
    db.commit()
    return db_obj
