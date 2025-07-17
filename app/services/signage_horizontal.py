from typing import Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.piano_segnaletica_orizzontale import (
    PianoSegnaleticaOrizzontale,
    SegnaleticaOrizzontaleItem,
)
from .inventory_pdf import build_inventory_pdf


def aggregate_items(db: Session, year: int) -> List[Dict[str, Any]]:
    """Return SegnaleticaOrizzontaleItem counts grouped by description for ``year``."""
    rows = (
        db.query(
            SegnaleticaOrizzontaleItem.descrizione,
            func.sum(SegnaleticaOrizzontaleItem.quantita).label("count"),
        )
        .join(
            PianoSegnaleticaOrizzontale,
            SegnaleticaOrizzontaleItem.piano_id == PianoSegnaleticaOrizzontale.id,
        )
        .filter(PianoSegnaleticaOrizzontale.anno == year)
        .group_by(SegnaleticaOrizzontaleItem.descrizione)
        .order_by(SegnaleticaOrizzontaleItem.descrizione)
        .all()
    )

    return [
        {"name": descrizione, "count": int(count)}
        for descrizione, count in rows
    ]


def build_signage_horizontal_pdf(db: Session, year: int) -> Tuple[str, str]:
    """Build a PDF inventory report for SegnaleticaOrizzontaleItem entries."""
    items = aggregate_items(db, year)
    return build_inventory_pdf(items, year)
