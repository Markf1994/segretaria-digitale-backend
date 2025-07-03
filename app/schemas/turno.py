from datetime import date, time
from pydantic import BaseModel, Field
from typing import Optional

class Slot(BaseModel):
    inizio: time
    fine: time

class TurnoBase(BaseModel):
    giorno: date
    slot1: Slot = Field(..., alias="inizio_1_fine_1")
    slot2: Optional[Slot] = Field(None, alias="inizio_2_fine_2")
    slot3: Optional[Slot] = Field(None, alias="inizio_3_fine_3")
    tipo: str
    note: Optional[str] = None

    class Config:
        allow_population_by_field_name = True

class TurnoIn(TurnoBase):
    user_id: str

class TurnoOut(TurnoBase):
    id: str
    user_id: str

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
