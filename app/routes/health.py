from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import os

from app.dependencies import get_db

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Check environment and database connectivity."""
    if not os.getenv("DATABASE_URL"):
        raise HTTPException(status_code=500, detail="DATABASE_URL not configured")
    if not os.getenv("SECRET_KEY"):
        raise HTTPException(status_code=500, detail="SECRET_KEY not configured")
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
