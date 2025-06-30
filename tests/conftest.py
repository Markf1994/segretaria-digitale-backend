import os
import pytest
import shutil
import importlib

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


@pytest.fixture(autouse=True)
def setup_upload_dir(tmp_path):
    upload_dir = tmp_path / "pdfs"
    os.environ["PDF_UPLOAD_ROOT"] = str(upload_dir)

    # Reload pdffile module so it picks up the new environment variable
    import app.crud.pdffile as pdffile
    pdffile = importlib.reload(pdffile)

    # Update the reference used by the PDF routes
    import app.routes.pdfs as pdf_routes
    pdf_routes.crud_pdffile = pdffile

    yield
    shutil.rmtree(str(upload_dir), ignore_errors=True)
