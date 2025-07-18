from pydantic import BaseModel


class SegnaleticaOrizzontaleCreate(BaseModel):
    azienda: str
    descrizione: str
    anno: int


class SegnaleticaOrizzontaleResponse(SegnaleticaOrizzontaleCreate):
    id: str

    model_config = {
        "from_attributes": True,
    }
