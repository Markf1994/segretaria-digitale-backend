from datetime import datetime
import uuid
from sqlalchemy import Column, String, DateTime
from app.database import Base

class PDFFile(Base):
    __tablename__ = "pdf_files"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    filename = Column(String, unique=True, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
