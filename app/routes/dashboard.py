from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.dependencies import get_db, get_current_user
import re
from app.models.user import User
from app.schemas.event import EventResponse
from app.schemas.todo import ToDoResponse
from app.crud import event, todo
from app.services.google_calendar import list_upcoming_events

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/upcoming")
def upcoming_events(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    now = datetime.utcnow()
    limit = now + timedelta(days=days)

    ev_items = [
        {
            **EventResponse.model_validate(ev, from_attributes=True).dict(),
            "kind": "event",
        }
        for ev in event.get_events(db, current_user)
        if now <= ev.data_ora <= limit
    ]

    todo_items = []
    for td in todo.get_todos(db, current_user):
        if now <= td.scadenza <= limit:
            data = ToDoResponse.model_validate(td, from_attributes=True).dict()
            data.pop("user_id", None)
            data["data_ora"] = data.pop("scadenza")
            data["kind"] = "todo"
            todo_items.append(data)

    gcal_raw = list_upcoming_events(days)

    me_name = (current_user.nome or current_user.email.split("@")[0]).strip().lower()
    other_names = {
        n.strip().lower()
        for (n,) in db.query(User.nome).filter(User.id != current_user.id).all()
        if n
    }

    def include_event(item: dict) -> bool:
        title = (item.get("titolo") or "").strip().lower()
        m = re.match(r"^(\d{1,2}:\d{2})\s+(.+)$", title)
        if m:
            who = m.group(2).strip().lower()
            return who == me_name
        if title in other_names:
            return False
        return True

    gcal_items = [
        {**g, "kind": "google"}
        for g in gcal_raw
        if now <= g.get("data_ora") <= limit and include_event(g)
    ]

    combined = ev_items + todo_items + gcal_items
    combined.sort(key=lambda x: x["data_ora"])
    # Convert datetimes to ISO strings for JSON response
    for item in combined:
        if isinstance(item.get("data_ora"), datetime):
            item["data_ora"] = item["data_ora"].isoformat()
    return combined
