"""
CRUD per i turni di servizio
────────────────────────────
• upsert_turno  → crea o aggiorna (1–3 intervalli) e sincronizza G-Calendar
• remove_turno → elimina dal DB e dal calendario turni
"""

from __future__ import annotations
from uuid import UUID

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import date
import logging

logger = logging.getLogger(__name__)

from app.models.turno import Turno  # modello ORM
from app.models.user import User
from app.schemas.turno import TurnoIn, TipoTurno  # Pydantic (input)
from app.services import gcal


# ------------------------------------------------------------------------------
def upsert_turno(db: Session, payload: TurnoIn) -> Turno:
    """
    Crea un nuovo turno o aggiorna quello esistente per lo stesso user+giorno.
    Dopo il commit sincronizza l’evento nel calendario “Turni di Servizio”.
    """
    # 1. verifica esistenza utente
    user = db.query(User).filter_by(id=payload.user_id).first()
    if not user:
        raise HTTPException(status_code=400, detail="Unknown user")

    # 2. recupera (o crea) il record
    rec: Turno | None = (
        db.query(Turno)
        .filter_by(user_id=payload.user_id, giorno=payload.giorno)
        .first()
    )
    if rec is None:
        rec = Turno(user_id=payload.user_id, giorno=payload.giorno)

    # 3. riempie i tre intervalli orari
    rec.inizio_1 = payload.inizio_1
    rec.fine_1 = payload.fine_1
    rec.inizio_2 = payload.inizio_2
    rec.fine_2 = payload.fine_2
    rec.inizio_3 = payload.inizio_3
    rec.fine_3 = payload.fine_3

    rec.tipo = payload.tipo.value  # NORMALE | STRAORD | FERIE
    rec.note = payload.note

    # 4. salva su database
    db.add(rec)
    db.commit()
    db.refresh(rec)  # ottieni id definitivo

    # 5. sincronizza l’evento Google Calendar (salta per i RECUPERO)
    if payload.tipo is not TipoTurno.RECUPERO:
        try:
            gcal.sync_shift_event(rec)
        except Exception as exc:
            # non bloccare l’operazione DB se G-Cal fallisce, ma loggare
            logger.error("Errore sync calendario: %s", exc)

    return rec


# ------------------------------------------------------------------------------
def remove_turno(db: Session, turno_id: UUID) -> None:
    """Elimina turno dal DB e dal calendario."""

    # 1. verifica che il turno esista
    rec = db.query(Turno).filter_by(id=turno_id).first()
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Turno non trovato"
        )

    # 2. cancella evento su Google (ignora eventuali errori)
    try:
        gcal.delete_shift_event(turno_id)
    except Exception as exc:  # pragma: no cover - unexpected errors
        # non bloccare l'operazione DB se G-Cal fallisce, ma loggare
        logger.error("Errore sync calendario: %s", exc)

    # 3. cancella record dal DB
    db.delete(rec)
    db.commit()


# ------------------------------------------------------------------------------
def get_turni(db: Session, user: User) -> list[Turno]:
    """Return all ``Turno`` records for ``user`` ordered by date."""
    return (
        db.query(Turno)
        .filter(Turno.user_id == user.id)
        .order_by(Turno.giorno.asc())
        .all()
    )


# ------------------------------------------------------------------------------
def list_all(db: Session) -> list[Turno]:
    """Return all ``Turno`` records in the database ordered by date."""
    return db.query(Turno).order_by(Turno.giorno.asc()).all()


# ------------------------------------------------------------------------------
def list_between(db: Session, start: date, end: date) -> list[Turno]:
    """Return ``Turno`` records between ``start`` and ``end`` dates."""
    return (
        db.query(Turno)
        .filter(Turno.giorno >= start, Turno.giorno <= end)
        .order_by(Turno.giorno.asc())
        .all()
    )
