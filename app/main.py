from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import users, auth, events, todo, determinazioni, pdfs
from app import scheduler

app = FastAPI(redirect_slashes=False)


@app.on_event("startup")
def on_startup() -> None:
    """Create database tables and start the scheduler on startup."""
    Base.metadata.create_all(bind=engine)
    scheduler.start()

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

from app.crud.pdffile import UPLOAD_ROOT
from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory=UPLOAD_ROOT), name="uploads")


@app.on_event("shutdown")
def on_shutdown() -> None:
    """Shutdown background services when the application stops."""
    scheduler.shutdown()
