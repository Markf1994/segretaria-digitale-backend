from sqlalchemy import Column, String
from app.database import Base
class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# app/schemas/user.py
from pydantic import BaseModel
class UserCreate(BaseModel):
    email: str
    password: str
class UserResponse(BaseModel):
    id: str
    email: str
    class Config:
        orm_mode = True
