from sqlalchemy.orm import Session
from app.models.determinazione import Determinazione


def create_determinazione(db: Session, data):
    """Persist a new :class:`Determinazione` using the provided schema."""
    db_det = Determinazione(**data.dict())
    db.add(db_det)
    db.commit()
    db.refresh(db_det)
    return db_det


def get_determinazioni(db: Session):
    """Return a list of all ``Determinazione`` entries."""
    return db.query(Determinazione).all()


def update_determinazione(db: Session, determinazione_id: str, data):
    """Update an existing ``Determinazione`` or return ``None`` if absent."""
    db_det = db.query(Determinazione).filter(Determinazione.id == determinazione_id).first()
    if not db_det:
        return None
    for key, value in data.dict().items():
        setattr(db_det, key, value)
    db.commit()
    return db_det


def delete_determinazione(db: Session, determinazione_id: str):
    """Delete a ``Determinazione`` by id if present and return it."""
    db_det = db.query(Determinazione).filter(Determinazione.id == determinazione_id).first()
    if db_det:
        db.delete(db_det)
        db.commit()
    return db_det
