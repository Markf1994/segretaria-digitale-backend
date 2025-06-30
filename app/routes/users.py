from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse
from app.crud import user
router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserResponse)
def create_user_route(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return it."""
    return user.create_user(db, user_data.email, user_data.password)
