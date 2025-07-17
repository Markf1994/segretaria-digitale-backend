from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Segnalazione(Base):
    __tablename__ = "segnalazioni"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    tipo = Column(String, nullable=False)
    stato = Column(String, nullable=False)
    priorita = Column(Integer, nullable=True)
    data_segnalazione = Column(DateTime, nullable=False)
    descrizione = Column(String, nullable=False)
    latitudine = Column(Float, nullable=True)
    longitudine = Column(Float, nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="segnalazioni")
