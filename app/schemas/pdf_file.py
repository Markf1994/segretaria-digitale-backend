from datetime import datetime
from pydantic import BaseModel

class PDFFileBase(BaseModel):
    title: str

class PDFFileCreate(PDFFileBase):
    pass

class PDFFileResponse(PDFFileBase):
    id: str
    filename: str
    uploaded_at: datetime

    class Config:
        orm_mode = True
