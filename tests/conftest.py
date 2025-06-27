import os
import pytest

# Ensure DATABASE_URL is set for tests
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from app.database import Base, engine

@pytest.fixture(autouse=True)
def setup_db():
    """Create a fresh database for each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
