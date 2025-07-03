from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse
from app.crud import user
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
