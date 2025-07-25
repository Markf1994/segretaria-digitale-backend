from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.user import UserCredentials
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests
from app.crud import user
from jose import jwt
from app.config import settings
import datetime

SECRET_KEY = settings.SECRET_KEY
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable not set")

ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
router = APIRouter(tags=["Auth"])


class GoogleToken(BaseModel):
    token: str


@router.post("/login")
def login(form_data: UserCredentials, db: Session = Depends(get_db)):
    """Authenticate a user and issue a JWT access token.

    The provided credentials are validated against the stored user data.
    On success the generated token and token type are returned, otherwise a
    400 HTTP error is raised.
    """
    db_user = user.get_user_by_email(db, form_data.email)
    if not db_user or not user.verify_password(
        form_data.password, db_user.hashed_password
    ):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": db_user.email, "exp": int(expire.timestamp())}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/google-login")
def google_login(data: GoogleToken, db: Session = Depends(get_db)):
    """Validate a Google ID token and issue a JWT access token."""
    client_id = settings.GOOGLE_CLIENT_ID
    if not client_id:
        raise HTTPException(status_code=500, detail="GOOGLE_CLIENT_ID not configured")

    try:
        info = id_token.verify_oauth2_token(data.token, requests.Request(), client_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Google token")

    email = info.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Token missing email")

    db_user = user.get_user_by_email(db, email)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    expire = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    payload = {"sub": db_user.email, "exp": int(expire.timestamp())}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}
