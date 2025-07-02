from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import (
    users,
    auth,
    events,
    todo,
    determinazioni,
    pdfs,
    dashboard,
)
from app.routes.orari import router as orari_router
from app.routes import import_xlsx

# Enable automatic redirect so both `/path` and `/path/` work
# Tests continue to use the canonical routes defined in the routers
app = FastAPI()


@app.on_event("startup")
def on_startup() -> None:
    """Create database tables on startup."""
    Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(todo.router)
app.include_router(determinazioni.router)
app.include_router(pdfs.router)
app.include_router(dashboard.router)
app.include_router(orari_router)
app.include_router(import_xlsx.router)

from app.crud.pdffile import get_upload_root
from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory=get_upload_root()), name="uploads")
