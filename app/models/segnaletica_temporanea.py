from sqlalchemy import Column, String, Integer, Date
from app.database import Base
import uuid


class SegnaleticaTemporanea(Base):
    __tablename__ = "segnaletica_temporanea"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    descrizione = Column(String, nullable=False)
    anno = Column(Integer, nullable=True)
    luogo = Column(String, nullable=True)
    fine_validita = Column(Date, nullable=True)
    quantita = Column(Integer, nullable=True)
