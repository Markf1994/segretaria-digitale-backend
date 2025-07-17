from sqlalchemy import Column, String, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class PianoSegnaleticaOrizzontale(Base):
    __tablename__ = "piani_segnaletica_orizzontale"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    descrizione = Column(String, nullable=False)
    anno = Column(Integer, nullable=True)

    items = relationship(
        "SegnaleticaOrizzontaleItem",
        back_populates="piano",
        cascade="all, delete-orphan",
    )


class SegnaleticaOrizzontaleItem(Base):
    __tablename__ = "segnaletica_orizzontale_items"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    piano_id = Column(String, ForeignKey("piani_segnaletica_orizzontale.id"), nullable=False)
    descrizione = Column(String, nullable=False)
    quantita = Column(Integer, nullable=False, default=1)
    luogo = Column(String, nullable=True)
    data = Column(Date, nullable=True)

    piano = relationship("PianoSegnaleticaOrizzontale", back_populates="items")
