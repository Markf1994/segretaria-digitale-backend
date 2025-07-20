from typing import Tuple, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.segnaletica_orizzontale import SegnaleticaOrizzontale
from .inventory_pdf import build_inventory_pdf


def aggregate_items(db: Session, year: int) -> List[Dict[str, Any]]:
    """Return ``SegnaleticaOrizzontale`` counts grouped by description for ``year``."""

    rows = (
        db.query(
            SegnaleticaOrizzontale.descrizione,
            func.count(SegnaleticaOrizzontale.id).label("count"),
        )
        .filter(SegnaleticaOrizzontale.anno == year)
        .group_by(SegnaleticaOrizzontale.descrizione)
        .order_by(SegnaleticaOrizzontale.descrizione)
        .all()
    )

    return [
        {"name": descrizione, "count": int(count)}
        for descrizione, count in rows
    ]


def build_signage_horizontal_pdf(db: Session, year: int) -> Tuple[str, str]:
    """Build a PDF inventory report for ``SegnaleticaOrizzontale`` entries."""
    items = aggregate_items(db, year)
    return build_inventory_pdf(items, year)


def get_years(db: Session) -> List[int]:
    """Return all distinct ``anno`` values from ``SegnaleticaOrizzontale``."""
    rows = (
        db.query(SegnaleticaOrizzontale.anno)
        .filter(SegnaleticaOrizzontale.anno.isnot(None))
        .distinct()
        .order_by(SegnaleticaOrizzontale.anno)
        .all()
    )
    return [int(row[0]) for row in rows]
