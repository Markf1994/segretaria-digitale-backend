from sqlalchemy.orm import Session
from app.models.todo import ToDo
from app.models.user import User


def create_todo(db: Session, data, user: User):
    """Create a ``ToDo`` entry from the supplied schema for ``user``."""
    db_todo = ToDo(**data.dict(), user_id=user.id)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def get_todos(db: Session, user: User):
    """Return all ``ToDo`` objects owned by ``user``."""
    return db.query(ToDo).filter(ToDo.user_id == user.id).all()


def update_todo(db: Session, todo_id: str, data, user: User):
    """Update a ``ToDo`` owned by ``user`` or return ``None`` if it does not exist."""
    db_todo = db.query(ToDo).filter(ToDo.id == todo_id, ToDo.user_id == user.id).first()
    if not db_todo:
        return None
    for key, value in data.dict().items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, todo_id: str, user: User):
    """Remove a todo entry owned by ``user`` and return it if found."""
    db_todo = db.query(ToDo).filter(ToDo.id == todo_id, ToDo.user_id == user.id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
    return db_todo
