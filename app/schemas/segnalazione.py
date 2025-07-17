from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class TipoSegnalazione(str, Enum):
    INCIDENTE = "incidente"
    VIOLAZIONE = "violazione"
    ALTRO = "altro"


class StatoSegnalazione(str, Enum):
    APERTA = "aperta"
    IN_LAVORAZIONE = "in lavorazione"
    CHIUSA = "chiusa"


class SegnalazioneCreate(BaseModel):
    tipo: TipoSegnalazione
    stato: StatoSegnalazione
    priorita: str | None = None
    data: datetime
    descrizione: str
    latitudine: float | None = None
    longitudine: float | None = None


class SegnalazioneUpdate(BaseModel):
    tipo: TipoSegnalazione | None = None
    stato: StatoSegnalazione | None = None
    priorita: str | None = None
    data: datetime | None = None
    descrizione: str | None = None
    latitudine: float | None = None
    longitudine: float | None = None


class SegnalazioneResponse(SegnalazioneCreate):
    id: str
    user_id: str

    model_config = {
        "from_attributes": True,
    }
