import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Recupera la URL del database da variabile d'ambiente
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable not set")

# Crea il motore SQLAlchemy con SSL richiesto
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)

# Configura la session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base per i modelli ORM
Base = declarative_base()
