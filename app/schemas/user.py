from pydantic import BaseModel, constr
from uuid import UUID
from app.schemas.turno import TurnoOut


class UserCreate(BaseModel):
    email: str
    password: str
    nome: constr(strip_whitespace=True, min_length=1)


class UserCredentials(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    id: UUID
    email: str
    nome: str

    model_config = {
        "from_attributes": True,
    }


class UserResponse(BaseModel):
    id: str
    email: str
    nome: str
    turni: list[TurnoOut] = []

    model_config = {
        "from_attributes": True,
    }
