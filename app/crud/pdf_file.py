import os
import uuid
import shutil
import logging
from typing import Optional

from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.models.pdf_file import PDFFile
from app.models.user import User
from app.schemas.pdf_file import PDFFileCreate

logger = logging.getLogger(__name__)


def get_upload_root() -> str:
    """Return the path where PDF files should be stored."""
    root = os.getenv("PDF_UPLOAD_ROOT", "uploads/pdfs")
    os.makedirs(root, exist_ok=True)
    return root


def create(
    db: Session,
    *,
    obj_in: PDFFileCreate,
    file: UploadFile,
    user: Optional[User] = None,
) -> PDFFile:
    """Store ``file`` on disk and persist metadata in the database."""
    ext = os.path.splitext(file.filename)[1]
    fname = f"{uuid.uuid4()}{ext}"
    path = os.path.join(get_upload_root(), fname)
    try:
        with open(path, "wb") as fp:
            shutil.copyfileobj(file.file, fp)
        logger.info(
            "Uploaded %s as %s for user=%s",
            file.filename,
            fname,
            getattr(user, "email", "anonymous"),
        )
    except Exception as exc:  # pragma: no cover - unexpected I/O failure
        logger.error(
            "Failed uploading %s for user=%s: %s",
            file.filename,
            getattr(user, "email", "anonymous"),
            exc,
        )
        raise
    finally:
        # Explicitly close the uploaded file to release resources
        file.file.close()

    db_obj = PDFFile(title=obj_in.title, filename=fname)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_multi(db: Session):
    return db.query(PDFFile).order_by(PDFFile.uploaded_at.desc()).all()


def get_file_path(filename: str, user: Optional[User] = None) -> str:
    """Return the full path for ``filename`` or raise ``FileNotFoundError``."""
    from pathlib import Path

    safe_name = Path(filename).name
    if safe_name != filename:
        logger.warning(
            "Invalid filename requested %s by user=%s",
            filename,
            getattr(user, "email", "anonymous"),
        )
        raise FileNotFoundError(filename)

    root = Path(get_upload_root())
    path = root / safe_name
    if not path.exists():
        logger.warning(
            "Requested file not found %s by user=%s",
            safe_name,
            getattr(user, "email", "anonymous"),
        )
        raise FileNotFoundError(filename)

    logger.info(
        "Retrieving file %s for user=%s",
        safe_name,
        getattr(user, "email", "anonymous"),
    )
    return str(path)
