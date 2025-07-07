from fastapi.testclient import TestClient
from pathlib import Path
from unittest.mock import patch
from app import config

from app.main import app

client = TestClient(app)


def test_upload_pdf_and_list(setup_db, tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 test")
    with open(pdf_path, "rb") as fh:
        res = client.post(
            "/pdf/",
            data={"title": "Doc"},
            files={"file": ("sample.pdf", fh, "application/pdf")},
        )
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "Doc"
    assert "filename" in body
    # ensure id is a valid UUID string
    from uuid import UUID

    UUID(body["id"])

    list_res = client.get("/pdf/")
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    get_res = client.get(f"/pdf/{body['filename']}")
    assert get_res.status_code == 200
    assert get_res.headers["content-type"] == "application/pdf"


def test_upload_invalid_content_type(setup_db, tmp_path):
    txt_path = tmp_path / "sample.txt"
    txt_path.write_text("hello")
    with open(txt_path, "rb") as fh:
        res = client.post(
            "/pdf/",
            data={"title": "Bad"},
            files={"file": ("sample.txt", fh, "text/plain")},
        )
    assert res.status_code == 400


def test_upload_invalid_extension(setup_db, tmp_path):
    malicious = tmp_path / "malicious.txt"
    malicious.write_bytes(b"%PDF-1.4 test")
    with open(malicious, "rb") as fh:
        res = client.post(
            "/pdf/",
            data={"title": "Bad"},
            files={"file": ("malicious.txt", fh, "application/pdf")},
        )
    assert res.status_code == 400


def test_get_pdf_not_found(setup_db):
    res = client.get("/pdf/missing.pdf")
    assert res.status_code == 404


def test_get_pdf_invalid_filename(setup_db):
    res = client.get("/pdf/../secret.pdf")
    assert res.status_code in (400, 404)


def test_delete_pdf_removes_file_and_record(setup_db, tmp_path):
    pdf_path = tmp_path / "del.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 test")
    with open(pdf_path, "rb") as fh:
        res = client.post(
            "/pdf/",
            data={"title": "Doc"},
            files={"file": ("del.pdf", fh, "application/pdf")},
        )
    fname = res.json()["filename"]

    upload_root = config.settings.PDF_UPLOAD_ROOT
    stored = Path(upload_root) / fname
    assert stored.exists()

    del_res = client.delete(f"/pdf/{fname}")
    assert del_res.status_code == 200
    assert del_res.json()["ok"] is True
    assert client.get("/pdf/").json() == []
    assert not stored.exists()


def test_delete_pdf_not_found(setup_db):
    res = client.delete("/pdf/missing.pdf")
    assert res.status_code == 404


def test_delete_pdf_invalid_filename(setup_db):
    res = client.delete("/pdf/../hack.pdf")
    assert res.status_code in (400, 404)


def test_upload_write_error_returns_500(setup_db, tmp_path):
    pdf_path = tmp_path / "err.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 test")

    with patch("app.crud.pdf_file.aiofiles.open", side_effect=OSError("disk full")):
        with open(pdf_path, "rb") as fh:
            res = client.post(
                "/pdf/",
                data={"title": "Bad"},
                files={"file": ("err.pdf", fh, "application/pdf")},
            )

    assert res.status_code == 500
    assert client.get("/pdf/").json() == []
    upload_root = config.settings.PDF_UPLOAD_ROOT
    assert list(Path(upload_root).iterdir()) == []
