from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_upload_and_list_and_download(setup_db, tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 test")
    with open(pdf_path, "rb") as fh:
        res = client.post(
            "/pdf-files/",
            data={"title": "Doc"},
            files={"file": ("sample.pdf", fh, "application/pdf")},
        )
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "Doc"
    assert "id" in body

    list_res = client.get("/pdf-files/")
    assert list_res.status_code == 200
    items = list_res.json()
    assert len(items) == 1
    assert items[0]["id"] == body["id"]

    get_res = client.get(f"/pdf-files/{body['id']}")
    assert get_res.status_code == 200
    assert get_res.headers["content-type"] == "application/pdf"


def test_upload_invalid_content_type(setup_db, tmp_path):
    txt_path = tmp_path / "sample.txt"
    txt_path.write_text("hello")
    with open(txt_path, "rb") as fh:
        res = client.post(
            "/pdf-files/",
            data={"title": "Bad"},
            files={"file": ("sample.txt", fh, "text/plain")},
        )
    assert res.status_code == 400


def test_download_not_found(setup_db):
    res = client.get("/pdf-files/missing")
    assert res.status_code == 404
