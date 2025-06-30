from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.schemas.todo import ToDoCreate, ToDoResponse
from app.crud import todo

router = APIRouter(prefix="/todo", tags=["ToDo"],trailing_slash=False)

@router.post("/", response_model=ToDoResponse)
def create_todo_route(
    data: ToDoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a todo item for the authenticated user."""
    return todo.create_todo(db, data, current_user)

@router.get("/", response_model=list[ToDoResponse])
def list_todos(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """List todo items for the authenticated user."""
    return todo.get_todos(db, current_user)

@router.put("/{todo_id}", response_model=ToDoResponse)
def update_todo_route(
    todo_id: str,
    data: ToDoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a todo owned by the authenticated user."""
    db_todo = todo.update_todo(db, todo_id, data, current_user)
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    return db_todo

@router.delete("/{todo_id}")
def delete_todo_route(
    todo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Remove a todo item owned by the authenticated user."""
    db_todo = todo.delete_todo(db, todo_id, current_user)
    if not db_todo:
        raise HTTPException(status_code=404, detail="ToDo not found")
    return {"ok": True}

