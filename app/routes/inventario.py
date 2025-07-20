from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os

from app.dependencies import get_db
from app.services.signage_horizontal import (
    build_signage_horizontal_pdf,
    get_years,
    aggregate_items,
)
from app.schemas.segnaletica_orizzontale import SignageInventoryItem

router = APIRouter(prefix="/inventario", tags=["Inventario"])


@router.get("/signage-horizontal/years", response_model=list[int])
def signage_horizontal_years(db: Session = Depends(get_db)):
    """List distinct years for which horizontal signage plans exist."""
    return get_years(db)


@router.get("/signage-horizontal/pdf")
def signage_horizontal_pdf(
    year: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    pdf_path, html_path = build_signage_horizontal_pdf(db, year)
    background_tasks.add_task(os.remove, pdf_path)
    background_tasks.add_task(os.remove, html_path)
    filename = f"signage_horizontal_{year}.pdf"
    return FileResponse(pdf_path, filename=filename)


@router.get(
    "/signage-horizontal/",
    response_model=list[SignageInventoryItem],
)
def signage_horizontal_items(year: int, db: Session = Depends(get_db)):
    """Return aggregated signage items for the given year."""
    return aggregate_items(db, year)
