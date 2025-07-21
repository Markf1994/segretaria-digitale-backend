from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class StatoToDo(str, Enum):
    ATTIVO = "ATTIVO"
    ARCHIVIATO = "ARCHIVIATO"


class ToDoCreate(BaseModel):
    descrizione: str
    scadenza: datetime
    stato: StatoToDo = StatoToDo.ATTIVO


class ToDoResponse(ToDoCreate):
    id: str
    user_id: str

    model_config = {
        "from_attributes": True,
    }
