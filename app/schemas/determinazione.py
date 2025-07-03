from pydantic import BaseModel
from datetime import datetime


class DeterminazioneCreate(BaseModel):
    capitolo: str
    numero: str
    descrizione: str
    somma: float
    scadenza: datetime


class DeterminazioneResponse(DeterminazioneCreate):
    id: str

    model_config = {
        "from_attributes": True,
    }
