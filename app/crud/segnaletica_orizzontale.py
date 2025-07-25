from datetime import date
from sqlalchemy.orm import Session
from app.models.segnaletica_orizzontale import SegnaleticaOrizzontale


def create_segnaletica_orizzontale(db: Session, data):
    payload = data.model_dump(mode="json")
    payload.setdefault("anno", date.today().year)
    db_obj = SegnaleticaOrizzontale(**payload)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_segnaletica_orizzontale(db: Session, search: str | None = None, anno: int | None = None):
    query = db.query(SegnaleticaOrizzontale)
    if search:
        query = query.filter(SegnaleticaOrizzontale.descrizione.ilike(f"%{search}%"))
    if anno is not None:
        query = query.filter(SegnaleticaOrizzontale.anno == anno)
    return query.all()


def update_segnaletica_orizzontale(db: Session, so_id: str, data):
    db_obj = db.query(SegnaleticaOrizzontale).filter(SegnaleticaOrizzontale.id == so_id).first()
    if not db_obj:
        return None
    payload = data.model_dump(mode="json", exclude_unset=True)
    for key, value in payload.items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_segnaletica_orizzontale(db: Session, so_id: str):
    db_obj = db.query(SegnaleticaOrizzontale).filter(SegnaleticaOrizzontale.id == so_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


def get_years(db: Session) -> list[int]:
    """Return all distinct ``anno`` values."""
    rows = (
        db.query(SegnaleticaOrizzontale.anno)
        .filter(SegnaleticaOrizzontale.anno.isnot(None))
        .distinct()
        .order_by(SegnaleticaOrizzontale.anno)
        .all()
    )
    return [int(row[0]) for row in rows]

