from pydantic import BaseModel
from datetime import datetime
class DeterminazioneCreate(BaseModel):
    capitolo: str
    numero: str
    somma: float
    scadenza: datetime
class DeterminazioneResponse(DeterminazioneCreate):
    id: str
    class Config:
        orm_mode = True
