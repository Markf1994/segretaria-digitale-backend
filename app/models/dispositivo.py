from sqlalchemy import Column, String, Integer
from app.database import Base
import uuid


class Dispositivo(Base):
    __tablename__ = "dispositivi"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    nome = Column(String, nullable=False)
    descrizione = Column(String, nullable=True)
    anno = Column(Integer, nullable=True)
