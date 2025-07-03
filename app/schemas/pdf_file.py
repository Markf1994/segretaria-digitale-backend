from datetime import datetime
from fastapi import UploadFile
from pydantic import BaseModel

class PdfFileIn(BaseModel):
    title: str
    file: UploadFile

class PdfFileOut(BaseModel):
    id: str
    title: str
    filename: str
    uploaded_at: datetime

    class Config:
        orm_mode = True
