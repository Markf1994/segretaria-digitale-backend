# Segretaria Digitale Backend

This repository contains a FastAPI backend used by Segretaria Digitale.

## Setup

1. Ensure you have **Python 3.10–3.11** installed.
2. Create a virtual environment and install dependencies (including `pandas`,
   `openpyxl`, `WeasyPrint==60.1` and `pydyf==0.8.0`):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt -r requirements-dev.txt
   ```
3. Install the system libraries required by **WeasyPrint** such as **Pango** and
   **Cairo**. On Debian-based distributions you can run:
   `apt-get update && apt-get install -y libpango-1.0-0 libcairo2 gdk-pixbuf2.0-0 libffi-dev`.
   PDF generation now relies on WeasyPrint, which references `Logo.png` and uses
   the **Aptos** font. Install the font from
   [Google Fonts](https://fonts.google.com/specimen/Aptos) or provide it
   locally. These libraries are required by
   `app/services/excel_import.py` and must be included in deployment build
   steps.
4. Place your `Logo.png` file at `static/Logo.png`. A placeholder file
   is included in that directory for version control and should be replaced
   with the actual image.
5. Copy `.env.example` to `.env` and adjust the values as needed. If you want to
   restrict cross-origin requests, set `CORS_ORIGINS` to a comma-separated list
   of allowed origins; leaving it unset defaults to `"*"` for development.

If asynchronous database access becomes necessary later on, add `asyncpg` to
`requirements.txt` and configure SQLAlchemy with its async engine.

## Required environment variables

- `DATABASE_URL` – connection string for the PostgreSQL database.
- `DATABASE_SSLMODE` – (optional) sslmode used for PostgreSQL connections. When
  set it overrides any `sslmode` parameter in `DATABASE_URL`. If neither is
  provided, the application defaults to `require`.
- `SECRET_KEY` – secret key used to sign JWT tokens.
- `ALGORITHM` – (optional) algorithm used for JWT; defaults to `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES` – (optional) lifetime of access tokens in minutes; defaults to `30`.
- `PDF_UPLOAD_ROOT` – directory where uploaded PDF files are stored.
- `GOOGLE_CREDENTIALS_JSON` – JSON credentials (or path) for Google APIs.
- `GOOGLE_CALENDAR_ID` – ID of the calendar to read events from.
- `G_SHIFT_CAL_ID` – ID of the Google Calendar used for shift syncs. Colors for
  shift events are assigned per agent using the `AGENT_COLORS` mapping defined
  in `app/services/gcal.py`. Agents not listed there fall back to a
  deterministic hash-based color.
- `GOOGLE_CLIENT_ID` – OAuth client ID for verifying Google sign-in tokens.
- `CORS_ORIGINS` – (optional) comma separated list of allowed origins for
  cross-origin requests. Defaults to `"*"`.
- `LOG_LEVEL` – (optional) Python log level for application logging. Defaults
  to `"INFO"`.

When `DATABASE_SSLMODE` is unset, the `sslmode` value from `DATABASE_URL` (if
any) is honored. If neither specifies a value, the application enforces secure
connections by setting `sslmode=require`.

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

### Google login

When using Google Identity Services, send the ID token returned by the client
to `/google-login`:

```javascript
fetch("http://localhost:8000/google-login", {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({token: googleToken}),
});
```

The response contains an `access_token` which should be stored (for example in
`localStorage`) and then included in the `Authorization` header of subsequent
requests:

```javascript
fetch("http://localhost:8000/google-login", { /* as above */ })
  .then((resp) => resp.json())
  .then(({access_token}) => {
    localStorage.setItem("token", access_token);
    return access_token;
  })
  .then((token) => {
    fetch("http://localhost:8000/protected-endpoint", {
      headers: {Authorization: `Bearer ${token}`},
    });
  });
```


## Running tests

Tests are located in the `tests/` directory. The suite requires all
packages listed in both `requirements.txt` and `requirements-dev.txt`.
System packages required by **WeasyPrint** (for example **Pango** and **Cairo**) must also be installed and the
necessary environment variables (for example `DATABASE_URL`) exported.
You can run the helper script `scripts/test.sh` which sets up a local
virtual environment, installs these dependencies and executes `pytest`:

```bash
export DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
./scripts/test.sh
```

The test suite uses a temporary SQLite database by default, but the
environment variables still need to be defined.

## Continuous Integration

All pushes and pull requests trigger a GitHub Actions workflow. It sets up
Python 3.11, installs the dependencies from `requirements.txt` and runs
`pytest`. The job fails if any tests fail.

## Deployment

When deploying on platforms like Render or Railway, ensure the libraries
required by **WeasyPrint** (such as **Pango** and **Cairo**) are installed before
Python dependencies. A typical build command is:

```bash
apt-get update && apt-get install -y libpango-1.0-0 libcairo2 gdk-pixbuf2.0-0 libffi-dev && pip install -r requirements.txt
```

If deploying with Docker, the provided `Dockerfile` installs these libraries
prior to installing packages.

A `render.yaml` file is also provided for deployments on **Render**. The web
service uses Docker and runs on port `10000`, which Render expects the
application to bind to. Install the [Render CLI](https://render.com/docs/cli)
and run

```bash
render blueprint deploy render.yaml
```

to create or update the service. Set the required environment variables
(for example `DATABASE_URL` and `SECRET_KEY`) in the Render dashboard.

## Troubleshooting

### CORS

Set the `CORS_ORIGINS` environment variable to a comma-separated list of allowed
origins, for example `https://example.com,https://app.example.com`. Two common
pitfalls are omitting the domain entirely and leaving trailing slashes after the
origin URL. When `CORS_ORIGINS` is not set, the API defaults to `"*"`, which is
appropriate only for local development.

### PDF generation

If `WeasyPrint` or its system libraries (for example **Pango** and **Cairo**) are
missing, PDF generation can fail with an error similar to:

```
PDF.__init__() takes 1 positional argument but 3 were given
```

Install the required packages using the apt-get command shown in the **Setup**
section:

```bash
apt-get update && apt-get install -y libpango-1.0-0 libcairo2 gdk-pixbuf2.0-0 libffi-dev
```

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
returns a PDF summary. This PDF now uses a formatted layout rendered by
WeasyPrint which embeds `Logo.png` and relies on the **Aptos** font. The
endpoint expects the file in a `multipart/form-data` request under the `file`
field. The same functionality is available via `/import/excel`.

The Excel sheet **must** include the `Giorno`, `Inizio1` and `Fine1` columns and
either a `User ID` or an `Agente` column. The `Giorno` column may also be
labeled `Data`. Optional columns are
`Inizio2`/`Fine2`, `Inizio3`/`Fine3` (or `Straordinario inizio`/`Straordinario fine`), `Tipo` and `Note`.
Valid values for `Tipo` are `NORMALE`, `STRAORD`, `FERIE`, `RIPOSO`, `FESTIVO` and `RECUPERO`.
Rows marked as day off (with `Tipo` set to `FERIE`, `RIPOSO`, `FESTIVO` or `RECUPERO`) may leave the `Inizio1` and `Fine1` cells empty. The columns must still be present in the sheet.
Leading and trailing spaces in time cells are ignored during parsing, but empty cells will raise a `400` error unless the row is a day off.
Invalid time formats (for example the string `nan`) also trigger a `400` response indicating the offending row.

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

## Orari endpoints

These routes manage turni records and require authentication.

- `POST /orari/` – create or update a turno and return the saved record.
- `GET /orari/` – list all turni without filtering by user.
- `DELETE /orari/{turno_id}` – remove the specified turno. When the
  `G_SHIFT_CAL_ID` environment variable is configured, the corresponding event
  is also deleted from Google Calendar.

## Shift PDF endpoint

The `GET /orari/pdf?week=YYYY-Www` route returns a PDF summary of the shifts
scheduled in the specified ISO week. The resulting document uses the same
formatted layout generated by WeasyPrint, embedding `Logo.png` and requiring
the **Aptos** font. The `week` parameter identifies the week using the
`YYYY-Www` format (for example, `2023-W42`). Authentication is required.

## Health endpoint

Check that required configuration and the database connection are working:

```bash
GET /health
```

A successful call returns status `200` with `{ "status": "ok" }`.

## License

This project is licensed under the [MIT License](LICENSE).

