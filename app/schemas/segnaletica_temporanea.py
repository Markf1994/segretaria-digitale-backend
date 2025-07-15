from pydantic import BaseModel


class SegnaleticaTemporaneaCreate(BaseModel):
    descrizione: str
    anno: int | None = None


class SegnaleticaTemporaneaResponse(SegnaleticaTemporaneaCreate):
    id: str

    model_config = {
        "from_attributes": True,
    }
