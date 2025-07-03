from datetime import date, time
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class TurnoBase(BaseModel):
    giorno: date
    inizio_1: time
    fine_1: time
    inizio_2: Optional[time] = None
    fine_2: Optional[time] = None
    inizio_3: Optional[time] = None
    fine_3: Optional[time] = None
    tipo: str
    note: Optional[str] = None


class TurnoIn(TurnoBase):
    user_id: str


class TurnoOut(TurnoBase):
    id: UUID
    user_id: UUID

    model_config = {
        "from_attributes": True,
    }
