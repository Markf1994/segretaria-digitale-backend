from sqlalchemy.orm import Session
from app.models.piano_segnaletica_orizzontale import (
    PianoSegnaleticaOrizzontale,
    SegnaleticaOrizzontaleItem,
)


def create_piano(db: Session, data):
    db_obj = PianoSegnaleticaOrizzontale(**data.dict(exclude={"items"}))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_piani(db: Session, search: str | None = None, anno: int | None = None):
    query = db.query(PianoSegnaleticaOrizzontale)
    if search:
        query = query.filter(PianoSegnaleticaOrizzontale.descrizione.ilike(f"%{search}%"))
    if anno is not None:
        query = query.filter(PianoSegnaleticaOrizzontale.anno == anno)
    return query.all()


def update_piano(db: Session, piano_id: str, data):
    db_obj = db.query(PianoSegnaleticaOrizzontale).filter(PianoSegnaleticaOrizzontale.id == piano_id).first()
    if not db_obj:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_piano(db: Session, piano_id: str):
    db_obj = db.query(PianoSegnaleticaOrizzontale).filter(PianoSegnaleticaOrizzontale.id == piano_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj


def add_item(db: Session, piano_id: str, data):
    db_piano = db.query(PianoSegnaleticaOrizzontale).filter(PianoSegnaleticaOrizzontale.id == piano_id).first()
    if not db_piano:
        return None
    item = SegnaleticaOrizzontaleItem(**data.dict(), piano_id=piano_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: str):
    db_obj = db.query(SegnaleticaOrizzontaleItem).filter(SegnaleticaOrizzontaleItem.id == item_id).first()
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
