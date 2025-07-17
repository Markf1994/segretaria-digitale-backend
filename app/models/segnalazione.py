from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer, Enum
from sqlalchemy.orm import relationship
import sqlalchemy as sa
from app.database import Base
from app.schemas.segnalazione import TipoSegnalazione, StatoSegnalazione
import uuid


class Segnalazione(Base):
    __tablename__ = "segnalazioni"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    tipo = Column(sa.Enum(TipoSegnalazione), nullable=False)
    stato = Column(sa.Enum(StatoSegnalazione), nullable=False)
    priorita = Column(Integer, nullable=True)
    data_segnalazione = Column(DateTime, nullable=False)
    descrizione = Column(String, nullable=False)
    latitudine = Column(Float, nullable=True)
    longitudine = Column(Float, nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="segnalazioni")
