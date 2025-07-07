from sqlalchemy import Column, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class Turno(Base):
    __tablename__ = "turni"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    giorno = Column(Date, nullable=False)

    inizio_1 = Column(Time, nullable=True)
    fine_1 = Column(Time, nullable=True)
    inizio_2 = Column(Time, nullable=True)
    fine_2 = Column(Time, nullable=True)
    inizio_3 = Column(Time, nullable=True)
    fine_3 = Column(Time, nullable=True)

    tipo = Column(String, nullable=True)
    note = Column(String, nullable=True)

    user = relationship("User", back_populates="turni")
