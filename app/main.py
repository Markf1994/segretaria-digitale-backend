from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.routes import users, auth, events, todo, determinazioni

Base.metadata.create_all(bind=engine)

app = FastAPI()

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


@app.get("/")
async def read_root():
    """Health check endpoint to confirm the service is running."""
    return {"message": "Service is running"}
