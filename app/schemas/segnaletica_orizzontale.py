from pydantic import BaseModel


class SegnaleticaOrizzontaleCreate(BaseModel):
    azienda: str
    descrizione: str


class SegnaleticaOrizzontaleResponse(SegnaleticaOrizzontaleCreate):
    id: str
    anno: int

    model_config = {
        "from_attributes": True,
    }


class SegnaleticaOrizzontaleUpdate(BaseModel):
    azienda: str | None = None
    descrizione: str | None = None


class SignageInventoryItem(BaseModel):
    """Aggregated inventory entry used by inventory endpoints."""

    name: str
    count: int
