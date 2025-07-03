from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from datetime import date, timedelta
import os

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.turno import TurnoIn, TurnoOut
from app.crud import turno as crud_turno
from app.services.excel_import import df_to_pdf

router = APIRouter(prefix="/orari", tags=["Turni"])


@router.post("/", response_model=TurnoOut)
def save_turno(
    payload: TurnoIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update a turno."""
    return crud_turno.upsert_turno(db, payload)


@router.get("/", response_model=list[TurnoOut])
def list_turni(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return all turni without filtering by user."""
    return crud_turno.list_all(db)


@router.delete("/{turno_id}")
def delete_turno(
    turno_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a turno."""
    crud_turno.remove_turno(db, turno_id)
    return {"ok": True}


@router.get("/pdf")
def week_pdf(
    week: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return a PDF summary of turni for the given ISO week (YYYY-Www)."""
    try:
        year_str, week_str = week.split("-W")
        start = date.fromisocalendar(int(year_str), int(week_str), 1)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid week format")
    end = start + timedelta(days=6)

    turni = crud_turno.list_between(db, start, end)

    rows = [jsonable_encoder(TurnoOut.from_orm(t)) for t in turni]

    pdf_path, html_path = df_to_pdf(rows)
    background_tasks.add_task(os.remove, pdf_path)
    background_tasks.add_task(os.remove, html_path)
    filename = f"turni_{week}.pdf"
    return FileResponse(pdf_path, filename=filename)
