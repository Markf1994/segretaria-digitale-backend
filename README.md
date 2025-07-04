# Segretaria Digitale Backend

This repository contains a FastAPI backend used by Segretaria Digitale.

## Setup

1. Ensure you have **Python 3.10–3.11** installed.
2. Create a virtual environment and install dependencies (including `httpx`,
   `pandas`, `openpyxl` and `pdfkit`):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt -r requirements-dev.txt
   ```
3. Install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) at the system
   level (e.g. `apt-get update && apt-get install -y wkhtmltopdf`). This is
   required for PDF generation in `app/services/excel_import.py` and must be
   included in deployment build steps.
4. Copy `.env.example` to `.env` and adjust the values as needed. If you want to
   restrict cross-origin requests, set `CORS_ORIGINS` to a comma-separated list
   of allowed origins; leaving it unset defaults to `"*"` for development.

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
- `CORS_ORIGINS` – (optional) comma separated list of allowed origins for
  cross-origin requests. Defaults to `"*"`.
- `LOG_LEVEL` – (optional) Python log level for application logging. Defaults
  to `"INFO"`.

## Database migrations

This project uses **Alembic** to manage database schema changes. With
`DATABASE_URL` configured, apply pending migrations using:

```bash
alembic upgrade head
```

After pulling the latest changes, run `alembic upgrade head` again to apply the new migration.

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

## Authentication

Obtain a JWT access token using `POST /login`. The endpoint only accepts a
`POST` request; `GET` requests are not supported.

Example:

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```


## Running tests

Tests are located in the `tests/` directory. After installing the
dependencies from both `requirements.txt` and `requirements-dev.txt`, make
sure system packages such as `wkhtmltopdf` are available and export the
environment variables required by the application (e.g. `DATABASE_URL`)
before running the tests:

```bash
export DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
pytest
```

The test suite uses a temporary SQLite database by default, but the
environment variables still need to be defined.

## Continuous Integration

All pushes and pull requests trigger a GitHub Actions workflow. It sets up
Python 3.11, installs the dependencies from `requirements.txt` and runs
`pytest`. The job fails if any tests fail.

## Deployment

When deploying on platforms like Render or Railway, ensure `wkhtmltopdf` is
installed before Python dependencies. A typical build command is:

```bash
apt-get update && apt-get install -y wkhtmltopdf && pip install -r requirements.txt
```

If deploying with Docker, the provided `Dockerfile` installs `wkhtmltopdf` prior
to installing packages.

### Troubleshooting CORS

Set the `CORS_ORIGINS` environment variable to a comma-separated list of allowed
origins, for example `https://example.com,https://app.example.com`. Two common
pitfalls are omitting the domain entirely and leaving trailing slashes after the
origin URL. When `CORS_ORIGINS` is not set, the API defaults to `"*"`, which is
appropriate only for local development.

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

## Users endpoint

Look up a user by email:

```bash
GET /users/by-email?email=<address>
```

Returns the matching user or `404` if none exists.

## Excel import endpoint

The `/import/xlsx` route accepts an Excel file containing shift data. It parses
each row, synchronizes the shifts with the database and Google Calendar, then
returns a PDF summary. The endpoint expects the file in a `multipart/form-data`
request under the `file` field. The same functionality is available via
`/import/excel`.

The Excel sheet **must** include the `Data`, `Inizio1` and `Fine1` columns and
either a `User ID` or an `Agente` column. Optional columns are
`Inizio2`/`Fine2`, `Inizio3`/`Fine3` (or `Straordinario inizio`/`Straordinario fine`), `Tipo` and `Note`.

Requests can fail with status `400` when required columns are missing, when a
user referenced by `User ID` or `Agente` does not exist, or when the identifier
cells are left empty.

Example:

```bash
curl -X POST -F "file=@shift.xlsx" http://localhost:8000/import/xlsx -o turni.pdf
```

When an import fails, the API returns a JSON response with a `detail` field
describing the issue. Front‑end code should display this message to the user
instead of logging a truncated line such as `ImportExcel error: L`.

## Shift PDF endpoint

The `GET /orari/pdf?week=YYYY-Www` route returns a PDF summary of the shifts
scheduled in the specified ISO week. The `week` parameter identifies the week
using the `YYYY-Www` format (for example, `2023-W42`). Authentication is
required.

## Health endpoint

Check that required configuration and the database connection are working:

```bash
GET /health
```

A successful call returns status `200` with `{ "status": "ok" }`.

## License

This project is licensed under the [MIT License](LICENSE).

