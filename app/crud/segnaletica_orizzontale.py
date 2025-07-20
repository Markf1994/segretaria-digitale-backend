from datetime import date
from sqlalchemy.orm import Session
from app.models.segnaletica_orizzontale import SegnaleticaOrizzontale


def create_segnaletica_orizzontale(db: Session, data):
    payload = data.dict()
    payload["anno"] = date.today().year
    db_obj = SegnaleticaOrizzontale(**payload)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_segnaletica_orizzontale(
    db: Session, search: str | None = None, year: int | None = None
):
    query = db.query(SegnaleticaOrizzontale)
    if search:
        query = query.filter(
            SegnaleticaOrizzontale.descrizione.ilike(f"%{search}%")
        )
    if year is not None:
        query = query.filter(SegnaleticaOrizzontale.anno == year)
    return query.all()


def get_years(db: Session) -> list[int]:
    rows = (
        db.query(SegnaleticaOrizzontale.anno)
        .filter(SegnaleticaOrizzontale.anno.isnot(None))
        .distinct()
        .order_by(SegnaleticaOrizzontale.anno)
        .all()
    )
    return [int(row[0]) for row in rows]


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
