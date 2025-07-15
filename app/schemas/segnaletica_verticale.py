from pydantic import BaseModel


class SegnaleticaVerticaleCreate(BaseModel):
    descrizione: str
    anno: int | None = None


class SegnaleticaVerticaleResponse(SegnaleticaVerticaleCreate):
    id: str

    model_config = {
        "from_attributes": True,
    }
