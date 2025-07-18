from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.config import settings
from app.routes import (
    users,
    auth,
    events,
    todo,
    determinazioni,
    pdf_files,
    dashboard,
    health,
    dispositivi,
    segnaletica_temporanea,
    segnaletica_verticale,
    piani_orizzontali,
    segnaletica_orizzontale,
    segnalazioni,
)
from app.routes.orari import router as orari_router
from app.routes import inventory
from app.routes import imports
from app.routes import inventario

# Enable automatic redirect so both `/path` and `/path/` work
# Tests continue to use the canonical routes defined in the routers
log_level = settings.LOG_LEVEL.upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))

app = FastAPI()

# Database tables are managed with Alembic migrations.
# Tests create tables manually using `Base.metadata.create_all()`.

origins = settings.CORS_ORIGINS
if origins == "*":
    allow_origins = ["*"]
else:
    allow_origins = [o.strip() for o in origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(todo.router)
app.include_router(determinazioni.router)
app.include_router(pdf_files.router)
app.include_router(dispositivi.router)
app.include_router(segnalazioni.router)
app.include_router(segnaletica_temporanea.router)
app.include_router(segnaletica_verticale.router)
app.include_router(piani_orizzontali.router)
app.include_router(segnaletica_orizzontale.router)
app.include_router(dashboard.router)
app.include_router(health.router)
app.include_router(orari_router)
app.include_router(inventory.router)
app.include_router(imports.router)
app.include_router(inventario.router)

from app.crud.pdf_file import get_upload_root
from fastapi.staticfiles import StaticFiles

app.mount("/uploads", StaticFiles(directory=get_upload_root()), name="uploads")
