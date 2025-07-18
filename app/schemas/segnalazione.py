from datetime import datetime
from enum import Enum
from pydantic import BaseModel


class TipoSegnalazione(str, Enum):
    PIANTE = "Piante"
    DANNEGGIAMENTI = "Danneggiamenti"
    REATI = "Reati"
    ANIMALI = "Animali"
    ALTRO = "Altro"


class StatoSegnalazione(str, Enum):
    APERTA = "aperta"
    IN_LAVORAZIONE = "in lavorazione"
    CHIUSA = "chiusa"


class SegnalazioneCreate(BaseModel):
    tipo: TipoSegnalazione
    stato: StatoSegnalazione
    priorita: int
    data_segnalazione: datetime
    descrizione: str
    latitudine: float | None = None
    longitudine: float | None = None


class SegnalazioneUpdate(BaseModel):
    stato: StatoSegnalazione | None = None
    priorita: int | None = None


class SegnalazionePatch(SegnalazioneUpdate):
    pass


class SegnalazioneResponse(SegnalazioneCreate):
    id: str
    user_id: str

    model_config = {
        "from_attributes": True,
    }
