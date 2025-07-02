from pydantic import BaseModel
class UserCreate(BaseModel):
    email: str
    password: str
class UserResponse(BaseModel):
    id: str
    email: str
    nome: str
    class Config:
        orm_mode = True
