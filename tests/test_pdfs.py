from fastapi.testclient import TestClient


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


def test_upload_pdf_respects_max_size(monkeypatch, setup_db, tmp_path):
    monkeypatch.setenv("MAX_PDF_SIZE", "20")
    pdf_path = tmp_path / "ok.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 small")
    with open(pdf_path, "rb") as fh:
        res = client.post(
            "/pdf/",
            data={"title": "Doc"},
            files={"file": ("ok.pdf", fh, "application/pdf")},
        )
    assert res.status_code == 201


def test_upload_pdf_too_large(monkeypatch, setup_db, tmp_path):
    monkeypatch.setenv("MAX_PDF_SIZE", "10")
    pdf_path = tmp_path / "big.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 big file")
    with open(pdf_path, "rb") as fh:
        res = client.post(
            "/pdf/",
            data={"title": "Big"},
            files={"file": ("big.pdf", fh, "application/pdf")},
        )
    assert res.status_code == 413


def test_get_pdf_not_found(setup_db):
    res = client.get("/pdf/missing.pdf")
    assert res.status_code == 404


def test_get_pdf_invalid_filename(setup_db):
    res = client.get("/pdf/../secret.pdf")
    assert res.status_code in (400, 404)
