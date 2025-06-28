from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.todo import ToDoCreate, ToDoResponse
from app.crud import todo

router = APIRouter(prefix="/todo", tags=["ToDo"],trailing_slash=False)

@router.post("/", response_model=ToDoResponse)
def create_todo_route(data: ToDoCreate, db: Session = Depends(get_db)):
    """Create a todo item and return it."""
    return todo.create_todo(db, data)

@router.get("/", response_model=list[ToDoResponse])
def list_todos(db: Session = Depends(get_db)):
    """List all todo items."""
    return todo.get_todos(db)

@router.put("/{todo_id}", response_model=ToDoResponse)
def update_todo_route(todo_id: str, data: ToDoCreate, db: Session = Depends(get_db)):
    """Update a todo and return the updated model or 404."""
    db_todo = todo.update_todo(db, todo_id, data)
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    return db_todo

@router.delete("/{todo_id}")
def delete_todo_route(todo_id: str, db: Session = Depends(get_db)):
    """Remove a todo item if present and confirm deletion."""
    db_todo = todo.delete_todo(db, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    return {"ok": True}
