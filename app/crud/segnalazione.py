from sqlalchemy.orm import Session
from app.models.segnalazione import Segnalazione
from app.models.user import User


def create_segnalazione(db: Session, data, user: User):
    data_dict = data.dict()
    data_dict["data"] = data_dict.pop("data_segnalazione")
    db_obj = Segnalazione(**data_dict, user_id=user.id)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_segnalazioni(db: Session, user: User):
    return db.query(Segnalazione).filter(Segnalazione.user_id == user.id).all()


def update_segnalazione(db: Session, segnalazione_id: str, data, user: User):
    db_obj = (
        db.query(Segnalazione)
        .filter(Segnalazione.id == segnalazione_id, Segnalazione.user_id == user.id)
        .first()
    )
    if not db_obj:
        return None
    update_data = data.dict(exclude_unset=True)
    if "data_segnalazione" in update_data:
        update_data["data"] = update_data.pop("data_segnalazione")
    for key, value in update_data.items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def delete_segnalazione(db: Session, segnalazione_id: str, user: User):
    db_obj = (
        db.query(Segnalazione)
        .filter(Segnalazione.id == segnalazione_id, Segnalazione.user_id == user.id)
        .first()
    )
    if db_obj:
        db.delete(db_obj)
        db.commit()
    return db_obj
