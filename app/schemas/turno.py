from datetime import date, time
from pydantic import BaseModel

class Slot(BaseModel):
    inizio: time
    fine: time

class TurnoIn(BaseModel):
    user_id: str
    giorno: date
    slot1: Slot
    slot2: Slot | None = None
    slot3: Slot | None = None
    tipo: str = "NORMALE"
    note: str | None = None

class TurnoResponse(TurnoIn):
    id: str

    class Config:
        orm_mode = True
