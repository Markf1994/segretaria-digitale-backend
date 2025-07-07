from sqlalchemy import create_engine, event
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Recupera la URL del database dal modulo di configurazione
DATABASE_URL = settings.DATABASE_URL

# Determina gli argomenti di connessione in base allo schema della URL
url = make_url(DATABASE_URL)
if url.drivername.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
else:
    connect_args = {"sslmode": "require"}

# Crea il motore SQLAlchemy con gli argomenti appropriati
engine = create_engine(DATABASE_URL, connect_args=connect_args)

if url.drivername.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Esporta gli argomenti di connessione per i test
CONNECT_ARGS = connect_args

# Configura la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base per i modelli ORM
Base = declarative_base()
