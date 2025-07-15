from sqlalchemy import Column, String, Integer
from app.database import Base
import uuid


class SegnaleticaTemporanea(Base):
    __tablename__ = "segnaletica_temporanea"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    descrizione = Column(String, nullable=False)
    anno = Column(Integer, nullable=True)
