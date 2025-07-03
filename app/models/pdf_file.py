from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class PDFFile(Base):
    __tablename__ = "pdf_files"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    filename = Column(String, unique=True, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
