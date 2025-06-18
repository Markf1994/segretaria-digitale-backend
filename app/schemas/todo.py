from pydantic import BaseModel
from datetime import datetime
class ToDoCreate(BaseModel):
    descrizione: str
    scadenza: datetime
class ToDoResponse(ToDoCreate):
    id: str
    class Config:
        from_attributes = True
