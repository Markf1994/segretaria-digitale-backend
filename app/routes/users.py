from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.schemas import user as user_schema
from app.crud import user as user_crud

router = APIRouter(prefix="/users", tags=["Users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=user_schema.UserResponse)
def create_user_route(user: user_schema.UserCreate, db: Session = Depends(get_db)):
    db_user = user_crud.create_user(db, user.email, user.password)
    return db_user