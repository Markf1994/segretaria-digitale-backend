from pydantic import BaseModel
class UserCreate(BaseModel):
    email: str
    password: str
class UserResponse(BaseModel):
    id: str
    email: str
    class Config:
        from_attributes = True