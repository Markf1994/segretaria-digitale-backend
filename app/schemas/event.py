from pydantic import BaseModel
from datetime import datetime


class EventCreate(BaseModel):
    titolo: str
    descrizione: str | None = None
    data_ora: datetime
    is_public: bool = False


class EventResponse(EventCreate):
    id: str
    user_id: str

    model_config = {
        "from_attributes": True,
    }
