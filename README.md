# Segretaria Digitale Backend

This repository contains a FastAPI backend used by Segretaria Digitale.

## Setup

1. Ensure you have **Python 3.10+** installed.
2. Create a virtual environment and install dependencies (including `httpx`,
   `pandas`, `openpyxl` and `pdfkit`):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Install `wkhtmltopdf` at the system level (e.g. `apt-get install wkhtmltopdf`
   when deploying to Docker or Render).
4. Copy `.env.example` to `.env` and adjust the values as needed.

4. Install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) to enable
   PDF generation in `app/services/excel_import.py`.

If asynchronous database access becomes necessary later on, add `asyncpg` to
`requirements.txt` and configure SQLAlchemy with its async engine.

## Required environment variables

- `DATABASE_URL` – connection string for the PostgreSQL database.
- `SECRET_KEY` – secret key used to sign JWT tokens.
- `ALGORITHM` – (optional) algorithm used for JWT; defaults to `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES` – (optional) lifetime of access tokens in minutes; defaults to `30`.
- `PDF_UPLOAD_ROOT` – directory where uploaded PDF files are stored.
- `GOOGLE_CREDENTIALS_JSON` – JSON credentials (or path) for Google APIs.
- `GOOGLE_CALENDAR_ID` – ID of the calendar to read events from.
- `G_EVENT_CAL_ID` – ID of the Google Calendar used for event syncs.
- `G_SHIFT_CAL_ID` – ID of the Google Calendar used for shift syncs.

## Database migrations

This project uses **Alembic** to manage database schema changes. With
`DATABASE_URL` configured, apply pending migrations using:

```bash
alembic upgrade head
```

After modifying the models, create a new revision and upgrade:

```bash
alembic revision --autogenerate -m "<message>"
alembic upgrade head
```

## Running the server

After installing dependencies and setting the environment variables, start the
application with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000/` by default.


## Running tests

Tests are located in the `tests/` directory. After installing the
dependencies simply run:

```bash
pytest
```

The test suite uses a temporary SQLite database, so no additional
configuration is required.

## Dashboard endpoint

The `/dashboard/upcoming` route aggregates local events, personal todos and
Google Calendar items. The optional query parameter `days` limits the lookup
window (default `7`). Authentication is required.

Example:

```bash
GET /dashboard/upcoming?days=5
```

The response is a chronologically ordered list where each item contains a
`kind` field (`event`, `todo` or `google`) and a `data_ora` timestamp.

## Events endpoint

Creating an event via `POST /events/` now returns HTTP status code `201` along
with the created event.

## Excel import endpoint

The `/import/xlsx` route accepts an Excel file containing shift data. It parses
each row, synchronizes the shifts with the database and Google Calendar, then
returns a PDF summary. The endpoint expects the file in a `multipart/form-data`
request under the `file` field.

Example:

```bash
curl -X POST -F "file=@shift.xlsx" http://localhost:8000/import/xlsx -o turni.pdf
```

## License

This project is licensed under the [MIT License](LICENSE).

