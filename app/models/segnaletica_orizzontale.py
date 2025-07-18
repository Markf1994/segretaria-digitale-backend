from sqlalchemy import Column, String, Integer
from app.database import Base
import uuid


class SegnaleticaOrizzontale(Base):
    __tablename__ = "segnaletica_orizzontale"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    azienda = Column(String, nullable=False)
    anno = Column(Integer, nullable=False)
    descrizione = Column(String, nullable=False)
