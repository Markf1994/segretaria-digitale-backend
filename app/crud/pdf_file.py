import os
import uuid
import logging
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import aiofiles
from app.models.pdf_file import PDFFile
from app.schemas.pdf_file import PDFFileCreate

logger = logging.getLogger(__name__)


def get_upload_root() -> str:
    """Return the path where PDF files should be stored."""
    root = os.getenv("PDF_UPLOAD_ROOT", "uploads/pdfs")
    os.makedirs(root, exist_ok=True)
    return root


async def create(db: Session, *, obj_in: PDFFileCreate, file: UploadFile) -> PDFFile:
    ext = os.path.splitext(file.filename)[1]
    fname = f"{uuid.uuid4()}{ext}"
    path = os.path.join(get_upload_root(), fname)

    try:
        async with aiofiles.open(path, "wb") as fp:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                await fp.write(chunk)
    except Exception as exc:  # pragma: no cover - unexpected errors
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        logger.error("Failed to write PDF %s: %s", path, exc)
        await file.close()
        raise HTTPException(status_code=500, detail="Failed to store PDF")
    else:
        await file.close()
        logger.info("Stored PDF at %s", path)

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
