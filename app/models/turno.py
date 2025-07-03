from sqlalchemy import Column, String, Date, Time, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Turno(Base):
    __tablename__ = "turni"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    giorno = Column(Date, nullable=False)

    inizio_1 = Column(Time, nullable=False)
    fine_1 = Column(Time, nullable=False)
    inizio_2 = Column(Time, nullable=True)
    fine_2 = Column(Time, nullable=True)
    inizio_3 = Column(Time, nullable=True)
    fine_3 = Column(Time, nullable=True)

    tipo = Column(String, nullable=True)
    note = Column(String, nullable=True)

    user = relationship("User", back_populates="turni")

    # Properties used by Pydantic alias mapping ------------------------------
    @property
    def inizio_1_fine_1(self) -> dict[str, Time]:
        """Return slot1 as a dictionary for Pydantic alias mapping."""
        return {"inizio": self.inizio_1, "fine": self.fine_1}

    @property
    def inizio_2_fine_2(self) -> dict[str, Time] | None:
        """Return slot2 or ``None`` if not fully specified."""
        if self.inizio_2 and self.fine_2:
            return {"inizio": self.inizio_2, "fine": self.fine_2}
        return None

    @property
    def inizio_3_fine_3(self) -> dict[str, Time] | None:
        """Return slot3 or ``None`` if not fully specified."""
        if self.inizio_3 and self.fine_3:
            return {"inizio": self.inizio_3, "fine": self.fine_3}
        return None
