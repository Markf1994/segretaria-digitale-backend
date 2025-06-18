from sqlalchemy.orm import Session
from app.models import user
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(db: Session, email: str, password: str):
    hashed_password = pwd_context.hash(password)
    db_user = user.User(id=str(uuid.uuid4()), email=email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(user.User).filter(user.User.email == email).first()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)