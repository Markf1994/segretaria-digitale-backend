from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas.user import UserCreate, UserResponse
from app.crud import user
router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
@router.post("/", response_model=UserResponse)
def create_user_route(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = user.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    db_user = user.create_user(db, user_data.email, user_data.password)
    return db_user