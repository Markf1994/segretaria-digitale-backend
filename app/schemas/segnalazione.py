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


class SegnalazioneBase(BaseModel):
    tipo: TipoSegnalazione | None = None
    stato: StatoSegnalazione | None = None
    priorita: str | None = None
    data: datetime | None = None
    descrizione: str | None = None
    latitudine: float | None = None
    longitudine: float | None = None


class SegnalazioneCreate(SegnalazioneBase):
    tipo: TipoSegnalazione
    stato: StatoSegnalazione
    data: datetime
    descrizione: str


class SegnalazioneResponse(SegnalazioneCreate):
    id: str
    user_id: str

    model_config = {
        "from_attributes": True,
    }


class SegnalazioneUpdate(SegnalazioneBase):
    """Schema for partial update of a segnalazione."""

    pass
