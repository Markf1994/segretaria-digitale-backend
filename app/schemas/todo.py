from pydantic import BaseModel
from datetime import datetime


class ToDoCreate(BaseModel):
    descrizione: str
    scadenza: datetime


class ToDoResponse(ToDoCreate):
    id: str
    user_id: str

    model_config = {
        "from_attributes": True,
    }
