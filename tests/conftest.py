import os
import shutil
import importlib
from unittest.mock import MagicMock, patch

import pytest

# Ensure DATABASE_URL is set for tests
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from app.database import Base, engine
from app import config

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
    original = config.settings.PDF_UPLOAD_ROOT
    config.settings.PDF_UPLOAD_ROOT = str(upload_dir)

    # Reload pdf_file module so it picks up the new setting
    import app.crud.pdf_file as pdf_file
    pdf_file = importlib.reload(pdf_file)

    # Update the reference used by the PDF routes
    import app.routes.pdf_files as pdf_routes
    pdf_routes.crud_pdf_file = pdf_file

    yield
    shutil.rmtree(str(upload_dir), ignore_errors=True)
    config.settings.PDF_UPLOAD_ROOT = original


@pytest.fixture(autouse=True)
def patch_google_clients():
    """Mock Google API clients so tests run without network access."""
    with patch(
        "google.oauth2.service_account.Credentials.from_service_account_file",
        return_value=MagicMock(),
    ):
        with patch("googleapiclient.discovery.build", return_value=MagicMock()):
            yield
