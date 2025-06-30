# Segretaria Digitale Backend

This repository contains a FastAPI backend used by Segretaria Digitale.

## Setup

1. Ensure you have **Python 3.10+** installed.
2. Create a virtual environment and install dependencies (including `httpx`):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and adjust the values as needed.

If asynchronous database access becomes necessary later on, add `asyncpg` to
`requirements.txt` and configure SQLAlchemy with its async engine.

## Required environment variables

- `DATABASE_URL` – connection string for the PostgreSQL database.
- `SECRET_KEY` – secret key used to sign JWT tokens.
- `ALGORITHM` – (optional) algorithm used for JWT; defaults to `HS256`.
- `ACCESS_TOKEN_EXPIRE_MINUTES` – (optional) lifetime of access tokens in minutes; defaults to `30`.
- `PDF_UPLOAD_ROOT` – directory where uploaded PDF files are stored.

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

The application starts a small background scheduler defined in
`app/scheduler.py`. By default it runs a job every minute that logs a message.
You can edit `sample_job` or remove the `scheduler.add_job` line in that file
to disable the task. Alternatively comment out the call to `scheduler.start()`
in `app/main.py` to disable the scheduler entirely.

## Running tests

Tests are located in the `tests/` directory. After installing the
dependencies simply run:

```bash
pytest
```

The test suite uses a temporary SQLite database, so no additional
configuration is required.

## License

This project is licensed under the [MIT License](LICENSE).

