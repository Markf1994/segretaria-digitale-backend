import uuid
from sqlalchemy import Column, String, DateTime, func
from app.database import Base

class PdfFile(Base):
    __tablename__ = "pdf_files"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    filename = Column(String, unique=True, nullable=False)
    uploaded_at = Column(DateTime, server_default=func.now())
