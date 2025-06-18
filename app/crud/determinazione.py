from sqlalchemy.orm import Session
from app.models.determinazione import Determinazione
def create_determinazione(db: Session, data):
    db_det = Determinazione(**data.dict())
    db.add(db_det)
    db.commit()
    db.refresh(db_det)
    return db_det
def get_determinazioni(db: Session):
    return db.query(Determinazione).all()
def update_determinazione(db: Session, determinazione_id: str, data):
    db_det = db.query(Determinazione).filter(Determinazione.id == determinazione_id).first()
    if not db_det:
        return None
    for key, value in data.dict().items():
        setattr(db_det, key, value)
    db.commit()
    return db_det
def delete_determinazione(db: Session, determinazione_id: str):
    db_det = db.query(Determinazione).filter(Determinazione.id == determinazione_id).first()
    if db_det:
        db.delete(db_det)
        db.commit()
    return db_det
