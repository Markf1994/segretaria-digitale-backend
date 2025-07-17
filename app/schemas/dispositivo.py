from pydantic import BaseModel


class DispositivoCreate(BaseModel):
    nome: str
    descrizione: str | None = None
    anno: int | None = None
    note: str | None = None


class DispositivoResponse(DispositivoCreate):
    id: str

    model_config = {
        "from_attributes": True,
    }
