from datetime import date, time
from pydantic import BaseModel
from typing import Optional

class Slot(BaseModel):
    inizio: time
    fine: time

class TurnoBase(BaseModel):
    giorno: date
    slot1: Slot
    slot2: Optional[Slot] = None
    slot3: Optional[Slot] = None
    tipo: str
    note: Optional[str] = None

class TurnoIn(TurnoBase):
    user_id: str

class TurnoOut(TurnoBase):
    id: str
    user_id: str

    class Config:
        orm_mode = True
