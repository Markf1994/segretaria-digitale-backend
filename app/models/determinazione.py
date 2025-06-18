from sqlalchemy import Column, String, DateTime, Float
from app.database import Base
import uuid
class Determinazione(Base):
    __tablename__ = "determinazioni"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    capitolo = Column(String, nullable=False)
    numero = Column(String, nullable=False)
    somma = Column(Float, nullable=False)
    scadenza = Column(DateTime, nullable=False)