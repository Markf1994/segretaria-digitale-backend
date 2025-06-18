from sqlalchemy import Column, String, DateTime, Boolean
from app.database import Base
import uuid
class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    titolo = Column(String, nullable=False)
    descrizione = Column(String, nullable=True)
    data_ora = Column(DateTime, nullable=False)
    is_public = Column(Boolean, default=False)