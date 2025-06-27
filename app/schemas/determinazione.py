from pydantic import BaseModel
from datetime import datetime
class DeterminazioneCreate(BaseModel):
    capitolo: str
    numero: str
    descrizione: str | None = None
    somma: float
    scadenza: datetime
class DeterminazioneResponse(DeterminazioneCreate):
    id: str
    class Config:
        orm_mode = True
