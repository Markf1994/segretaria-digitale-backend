from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import FileResponse
import os
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.dependencies import get_db
from app.models.piano_segnaletica_orizzontale import (
    PianoSegnaleticaOrizzontale,
    SegnaleticaOrizzontaleItem,
)

from app.services.inventory_pdf import build_inventory_pdf

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/pdf")
def inventory_pdf(
    year: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Return a PDF inventory report for the specified year."""

    query = (
        db.query(
            SegnaleticaOrizzontaleItem.descrizione.label("name"),
            func.sum(SegnaleticaOrizzontaleItem.quantita).label("count"),
        )
        .join(
            PianoSegnaleticaOrizzontale,
            SegnaleticaOrizzontaleItem.piano_id == PianoSegnaleticaOrizzontale.id,
        )
        .filter(PianoSegnaleticaOrizzontale.anno == year)
        .group_by(SegnaleticaOrizzontaleItem.descrizione)
    )
    items = [
        {"name": row.name, "count": int(row.count)}
        for row in query.all()
    ]

    pdf_path, html_path = build_inventory_pdf(items, year)
    background_tasks.add_task(os.remove, pdf_path)
    background_tasks.add_task(os.remove, html_path)
    filename = f"inventory_{year}.pdf"
    return FileResponse(pdf_path, filename=filename)
