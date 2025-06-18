from sqlalchemy import Column, String, DateTime
from app.database import Base
import uuid
class ToDo(Base):
    __tablename__ = "todos"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    descrizione = Column(String, nullable=False)
    scadenza = Column(DateTime, nullable=False)