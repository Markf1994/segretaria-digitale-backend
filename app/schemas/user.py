from pydantic import BaseModel
from app.schemas.turno import TurnoOut
class UserCreate(BaseModel):
    email: str
    password: str
    nome: str


class UserCredentials(BaseModel):
    email: str
    password: str
class UserResponse(BaseModel):
    id: str
    email: str
    nome: str
    turni: list[TurnoOut] = []
    class Config:
        orm_mode = True
