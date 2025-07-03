from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.models.user import User
from passlib.context import CryptContext
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, email: str, password: str, nome: str):
    """Create and return a new user with a hashed password."""
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=409, detail="Email already registered")

    hashed_password = pwd_context.hash(password)
    db_user = User(
        id=str(uuid.uuid4()),
        email=email,
        nome=nome,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str):
    """Return a user instance matching ``email`` or ``None``."""
    return db.query(User).filter(User.email == email).first()


def verify_password(plain_password, hashed_password):
    """Return ``True`` if the plaintext password matches the hashed one."""
    return pwd_context.verify(plain_password, hashed_password)


def list_users(db: Session):
    """Restituisce tutti gli utenti ordinati per nome con i turni caricati."""
    return (
        db.query(User)
        .options(joinedload(User.turni))
        .order_by(User.nome.asc())
        .all()
    )
