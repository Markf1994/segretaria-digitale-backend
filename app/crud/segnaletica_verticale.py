from sqlalchemy.orm import Session
from app.models.segnaletica_verticale import SegnaleticaVerticale


def create_segnaletica_verticale(db: Session, data):
    db_obj = SegnaleticaVerticale(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_segnaletica_verticale(db: Session, search: str | None = None, anno: int | None = None):
    query = db.query(SegnaleticaVerticale)
    if search:
        query = query.filter(SegnaleticaVerticale.descrizione.ilike(f"%{search}%"))
    if anno is not None:
        query = query.filter(SegnaleticaVerticale.anno == anno)
    return query.all()


def update_segnaletica_verticale(db: Session, sv_id: str, data):
    db_obj = db.query(SegnaleticaVerticale).filter(SegnaleticaVerticale.id == sv_id).first()
    if not db_obj:
        return None
    for key, value in data.dict().items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_segnaletica_verticale(db: Session, sv_id: str):
    db_obj = db.query(SegnaleticaVerticale).filter(SegnaleticaVerticale.id == sv_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
