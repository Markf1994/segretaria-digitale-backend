from datetime import date, time
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator

class TipoTurno(str, Enum):
    NORMALE = "NORMALE"
    STRAORD = "STRAORD"
    FERIE = "FERIE"
    RIPOSO = "RIPOSO"
    FESTIVO = "FESTIVO"
    RECUPERO = "RECUPERO"


DAY_OFF_TYPES = {
    TipoTurno.FERIE,
    TipoTurno.RIPOSO,
    TipoTurno.FESTIVO,
    TipoTurno.RECUPERO,
}


class TurnoBase(BaseModel):
    giorno: date
    inizio_1: Optional[time] = None
    fine_1: Optional[time] = None
    inizio_2: Optional[time] = None
    fine_2: Optional[time] = None
    inizio_3: Optional[time] = None
    fine_3: Optional[time] = None
    tipo: TipoTurno
    note: Optional[str] = None

    @model_validator(mode="after")
    def check_required_times(cls, data):
        if data.tipo not in DAY_OFF_TYPES:
            if data.inizio_1 is None or data.fine_1 is None:
                raise ValueError("inizio_1 and fine_1 are required")
        return data


class TurnoIn(TurnoBase):
    user_id: str


class TurnoOut(TurnoBase):
    id: UUID
    user_id: UUID

    model_config = {
        "from_attributes": True,
    }
