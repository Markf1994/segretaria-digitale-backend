from typing import List
import logging
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from app.dependencies import get_db, get_optional_user
from app.models.user import User
from app.schemas.pdf_file import PDFFileCreate, PDFFileResponse
from app.crud import pdf_file as crud_pdf_file

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdf", tags=["PDF"])


@router.get("/", response_model=List[PDFFileResponse])
def list_pdfs(db: Session = Depends(get_db)):
    return crud_pdf_file.get_multi(db)


@router.post("/", response_model=PDFFileResponse, status_code=201)
async def upload_pdf(
    title: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Il file deve essere un PDF")
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Il file deve avere estensione .pdf")
    return await crud_pdf_file.create(db, obj_in=PDFFileCreate(title=title), file=file)


@router.get("/{filename}")
def get_pdf(
    filename: str,
    current_user: User | None = Depends(get_optional_user),
):
    """Return a previously uploaded PDF by filename."""
    from pathlib import Path
    from app.crud.pdf_file import get_upload_root

    # Prevent path traversal attacks by stripping directory components
    safe_name = Path(filename).name
    user_ctx = current_user.email if current_user else "anonymous"
    if safe_name != filename:
        # Invalid filename with path components
        logger.warning("Invalid filename '%s' requested by %s", filename, user_ctx)
        raise HTTPException(status_code=404)

    root = Path(get_upload_root())
    path = root / safe_name
    if not path.exists():
        logger.warning("PDF '%s' not found for user %s", filename, user_ctx)
        raise HTTPException(status_code=404)

    response = FileResponse(str(path), media_type="application/pdf", filename=safe_name)
    logger.info("PDF '%s' retrieved by %s", filename, user_ctx)
    return response


@router.delete("/{filename}")
def delete_pdf(
    filename: str,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_optional_user),
):
    """Delete a previously uploaded PDF by filename."""
    from pathlib import Path

    safe_name = Path(filename).name
    if safe_name != filename:
        raise HTTPException(status_code=404)

    db_obj = crud_pdf_file.delete(db, filename=safe_name)
    if not db_obj:
        raise HTTPException(status_code=404)

    user_ctx = current_user.email if current_user else "anonymous"
    logger.info("PDF '%s' deleted by %s", safe_name, user_ctx)
    return {"ok": True}
