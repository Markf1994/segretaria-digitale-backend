from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.schemas.user import UserCreate, UserResponse, UserOut
from app.crud import user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


# ───── nuovo endpoint GET /users/ ─────
@router.get("/", response_model=list[UserResponse])
def list_users_route(
    db: Session = Depends(get_db),
):
    """Restituisce la lista di tutti gli utenti."""
    return user.list_users(db)


# ───────────────────────────────────────


@router.post("/", response_model=UserResponse)
def create_user_route(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user and return it."""
    return user.create_user(db, user_data.email, user_data.password, user_data.nome)


# ───── nuovo endpoint GET /users/by-email ─────
@router.get("/by-email", response_model=UserResponse)
def get_user_by_email_route(email: str, db: Session = Depends(get_db)):
    """Return a user by email or raise 404 if not found."""
    result = user.get_user_by_email(db, email)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result


# ───────────────────────────────────────────────


@router.get("/me", response_model=UserOut)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Restituisce i dati dell'utente autenticato (dal token JWT)."""
    return current_user


# ───────────────────────────────────────────────
