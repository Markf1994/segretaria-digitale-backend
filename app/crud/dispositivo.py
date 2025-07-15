from sqlalchemy.orm import Session
from app.models.dispositivo import Dispositivo


def create_dispositivo(db: Session, data):
    db_obj = Dispositivo(**data.dict())
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_dispositivi(db: Session, search: str | None = None, anno: int | None = None):
    query = db.query(Dispositivo)
    if search:
        query = query.filter(Dispositivo.nome.ilike(f"%{search}%"))
    if anno is not None:
        query = query.filter(Dispositivo.anno == anno)
    return query.all()


def update_dispositivo(db: Session, dispositivo_id: str, data):
    db_obj = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if not db_obj:
        return None
    for key, value in data.dict().items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_dispositivo(db: Session, dispositivo_id: str):
    db_obj = db.query(Dispositivo).filter(Dispositivo.id == dispositivo_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
