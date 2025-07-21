from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from app.schemas.todo import StatoToDo


class ToDo(Base):
    __tablename__ = "todos"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    descrizione = Column(String, nullable=False)
    scadenza = Column(DateTime, nullable=False)
    stato = Column(String(30), nullable=False, default=StatoToDo.ATTIVO.value)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="todos")
