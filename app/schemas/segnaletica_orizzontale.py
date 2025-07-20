from pydantic import BaseModel


class SegnaleticaOrizzontaleCreate(BaseModel):
    azienda: str
    descrizione: str
    anno: int | None = None


class SegnaleticaOrizzontaleResponse(SegnaleticaOrizzontaleCreate):
    id: str

    model_config = {
        "from_attributes": True,
    }


class SignageInventoryItem(BaseModel):
    """Aggregated inventory entry used by inventory endpoints."""

    name: str
    count: int
