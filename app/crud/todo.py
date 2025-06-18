from sqlalchemy.orm import Session
from app.models.todo import ToDo
def create_todo(db: Session, data):
    db_todo = ToDo(**data.dict())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo
def get_todos(db: Session):
    return db.query(ToDo).all()
def update_todo(db: Session, todo_id: str, data):
    db_todo = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if not db_todo:
        return None
    for key, value in data.dict().items():
        setattr(db_todo, key, value)
    db.commit()
    return db_todo
def delete_todo(db: Session, todo_id: str):
    db_todo = db.query(ToDo).filter(ToDo.id == todo_id).first()
    if db_todo:
        db.delete(db_todo)
        db.commit()
    return db_todo
