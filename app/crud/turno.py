from app.services.gcal import sync_shift_event

def upsert_turno(db: Session, payload: TurnoIn) -> Turno:
    # ...  (logica esistente)
    db.commit(); db.refresh(turno)

    # ★ aggiungi questa riga
    sync_shift_event(turno)

    return turno
