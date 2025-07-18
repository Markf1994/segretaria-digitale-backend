from sqlalchemy.orm import Session
from app.models.segnalazione import Segnalazione
from app.models.user import User


def create_segnalazione(db: Session, data, user: User):
    payload = data.model_dump(mode="json")
    payload["stato"] = payload["stato"].lower()
    tipo_map = {
        "piante": "Piante",
        "danneggiamenti": "Danneggiamenti",
        "reati": "Reati",
        "animali": "Animali",
        "altro": "Altro",
    }
    payload["tipo"] = tipo_map.get(payload["tipo"].lower(), payload["tipo"])

    db_obj = Segnalazione(**payload, user_id=user.id)

    print("DEBUG PRE-COMMIT:", db_obj.tipo, db_obj.stato)

    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


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
    payload = data.model_dump(mode="json", exclude_unset=True)
    if "stato" in payload:
        payload["stato"] = payload["stato"].lower()
    if "tipo" in payload:
        tipo_map = {
            "piante": "Piante",
            "danneggiamenti": "Danneggiamenti",
            "reati": "Reati",
            "animali": "Animali",
            "altro": "Altro",
        }
        payload["tipo"] = tipo_map.get(payload["tipo"].lower(), payload["tipo"])
    for key, value in payload.items():
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
    payload = data.model_dump(mode="json", exclude_unset=True)
    if "stato" in payload:
        payload["stato"] = payload["stato"].lower()
    if "tipo" in payload:
        tipo_map = {
            "piante": "Piante",
            "danneggiamenti": "Danneggiamenti",
            "reati": "Reati",
            "animali": "Animali",
            "altro": "Altro",
        }
        payload["tipo"] = tipo_map.get(payload["tipo"].lower(), payload["tipo"])
    for key, value in payload.items():
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
