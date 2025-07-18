from sqlalchemy.orm import Session
from app.models.segnalazione import Segnalazione
from app.models.user import User


def create_segnalazione(db: Session, data, user: User):
    tipo_val = getattr(data.tipo, "value", data.tipo)
    stato_val = getattr(data.stato, "value", data.stato)
    stato_val = stato_val.lower()

    mapping_tipo = {
        "piante": "Piante",
        "danneggiamenti": "Danneggiamenti",
        "reati": "Reati",
        "animali": "Animali",
        "altro": "Altro",
    }

    tipo_val = mapping_tipo.get(tipo_val.lower(), tipo_val)

    obj = Segnalazione(
        tipo=tipo_val,
        stato=stato_val,
        priorita=data.priorita,
        data_segnalazione=data.data_segnalazione,
        descrizione=data.descrizione,
        latitudine=data.latitudine,
        longitudine=data.longitudine,
        user_id=user.id,
    )

    print("DEBUG INSERT:", obj.tipo, obj.stato)

    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get_segnalazioni(db: Session, user: User):
    return db.query(Segnalazione).filter(Segnalazione.user_id == user.id).all()


def get_segnalazioni_by_stato(db: Session, user: User, stati: list[str]):
    """Return segnalazioni owned by ``user`` whose ``stato`` is in ``stati``."""
    if not stati:
        return []
    return (
        db.query(Segnalazione)
        .filter(
            Segnalazione.user_id == user.id,
            Segnalazione.stato.in_(stati),
        )
        .all()
    )


def get_segnalazione(db: Session, segnalazione_id: str, user: User):
    return (
        db.query(Segnalazione)
        .filter(Segnalazione.id == segnalazione_id, Segnalazione.user_id == user.id)
        .first()
    )


def update_segnalazione(db: Session, segnalazione_id: str, data, user: User):
    db_obj = (
        db.query(Segnalazione)
        .filter(Segnalazione.id == segnalazione_id, Segnalazione.user_id == user.id)
        .first()
    )
    if not db_obj:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(db_obj, key, value)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def patch_segnalazione(db: Session, segnalazione_id: str, data, user: User):
    db_obj = (
        db.query(Segnalazione)
        .filter(Segnalazione.id == segnalazione_id, Segnalazione.user_id == user.id)
        .first()
    )
    if not db_obj:
        return None
    for key, value in data.dict(exclude_unset=True).items():
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
