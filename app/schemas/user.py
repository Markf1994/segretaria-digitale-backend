from pydantic import BaseModel, EmailStr, SecretStr
class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr
class UserResponse(BaseModel):
    id: str
    email: str
    class Config:
        orm_mode = True
