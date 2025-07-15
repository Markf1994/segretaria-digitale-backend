from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import FileResponse
import os

from app.services.inventory_pdf import build_inventory_pdf

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("/pdf")
def inventory_pdf(year: int, background_tasks: BackgroundTasks):
    """Return a PDF inventory report for the specified year."""
    # In a real application this would fetch data from the database.
    items = []  # placeholder for inventory entries
    pdf_path, html_path = build_inventory_pdf(items, year)
    background_tasks.add_task(os.remove, pdf_path)
    background_tasks.add_task(os.remove, html_path)
    filename = f"inventory_{year}.pdf"
    return FileResponse(pdf_path, filename=filename)
