from datetime import date, time
from pydantic import BaseModel


class ShiftSlot(BaseModel):
    inizio: time
    fine: time


class TurnoBase(BaseModel):
    user_id: str
    giorno: date
    slot1: ShiftSlot
    slot2: ShiftSlot | None = None
    slot3: ShiftSlot | None = None
    tipo: str = "NORMALE"
    note: str | None = None


class TurnoIn(TurnoBase):
    pass


class TurnoOut(TurnoBase):
    id: str

    class Config:
        orm_mode = True
