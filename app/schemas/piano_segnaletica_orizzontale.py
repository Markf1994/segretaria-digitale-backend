from pydantic import BaseModel
from typing import List


class SegnaleticaOrizzontaleItemCreate(BaseModel):
    descrizione: str
    quantita: int = 1


class SegnaleticaOrizzontaleItemUpdate(BaseModel):
    descrizione: str | None = None
    quantita: int | None = None


class SegnaleticaOrizzontaleItemResponse(SegnaleticaOrizzontaleItemCreate):
    id: str
    piano_id: str

    model_config = {
        "from_attributes": True,
    }


class PianoSegnaleticaOrizzontaleCreate(BaseModel):
    descrizione: str
    anno: int | None = None


class PianoSegnaleticaOrizzontaleResponse(PianoSegnaleticaOrizzontaleCreate):
    id: str
    items: List[SegnaleticaOrizzontaleItemResponse] = []

    model_config = {
        "from_attributes": True,
    }
