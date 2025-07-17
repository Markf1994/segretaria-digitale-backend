from pydantic import BaseModel


class SegnaleticaVerticaleCreate(BaseModel):
    descrizione: str
    tipo: str | None = None
    quantita: int = 1
    luogo: str | None = None
    anno: int | None = None


class SegnaleticaVerticaleResponse(SegnaleticaVerticaleCreate):
    id: str

    model_config = {
        "from_attributes": True,
    }
