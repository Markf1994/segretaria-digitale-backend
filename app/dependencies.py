from typing import Generator

from sqlalchemy.orm import Session
from fastapi import Depends, Header, HTTPException, status
from jose import jwt, JWTError
from app.config import settings

from .database import SessionLocal
from .models.user import User


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(None, alias="Authorization"),
) -> User:
    """Return the authenticated ``User`` based on the JWT token."""
    if authorization is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
        )
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.split(" ", 1)[1]
    secret = settings.SECRET_KEY
    if not secret:
        raise HTTPException(status_code=500, detail="Secret key not configured")
    algorithm = settings.ALGORITHM

    try:
        payload = jwt.decode(token, secret, algorithms=[algorithm])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_optional_user(
    db: Session = Depends(get_db),
    authorization: str | None = Header(None, alias="Authorization"),
) -> User | None:
    """Return the authenticated ``User`` if credentials are provided."""
    if authorization is None:
        return None
    return get_current_user(db=db, authorization=authorization)
