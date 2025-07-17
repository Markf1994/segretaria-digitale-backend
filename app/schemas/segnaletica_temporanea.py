from pydantic import BaseModel
from datetime import date


class SegnaleticaTemporaneaCreate(BaseModel):
    descrizione: str
    anno: int | None = None
    luogo: str | None = None
    fine_validita: date | None = None
    quantita: int | None = None


class SegnaleticaTemporaneaResponse(SegnaleticaTemporaneaCreate):
    id: str

    model_config = {
        "from_attributes": True,
    }
