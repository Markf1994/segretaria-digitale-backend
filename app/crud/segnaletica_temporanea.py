from sqlalchemy.orm import Session
from app.models.segnaletica_temporanea import SegnaleticaTemporanea


def create_segnaletica_temporanea(db: Session, data):
    db_obj = SegnaleticaTemporanea(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_segnaletica_temporanea(db: Session, search: str | None = None, anno: int | None = None):
    query = db.query(SegnaleticaTemporanea)
    if search:
        query = query.filter(SegnaleticaTemporanea.descrizione.ilike(f"%{search}%"))
    if anno is not None:
        query = query.filter(SegnaleticaTemporanea.anno == anno)
    return query.all()


def update_segnaletica_temporanea(db: Session, st_id: str, data):
    db_obj = db.query(SegnaleticaTemporanea).filter(SegnaleticaTemporanea.id == st_id).first()
    if not db_obj:
        return None
    for key, value in data.dict().items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_segnaletica_temporanea(db: Session, st_id: str):
    db_obj = db.query(SegnaleticaTemporanea).filter(SegnaleticaTemporanea.id == st_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
