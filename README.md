# Segretaria Digitale Backend

This repository contains a FastAPI backend used by Segretaria Digitale.

## Setup

1. Ensure you have **Python 3.10+** installed.
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and adjust the values as needed.

## Required environment variables

- `DATABASE_URL` – connection string for the PostgreSQL database.
- `SECRET_KEY` – secret key used to sign JWT tokens.
- `ALGORITHM` – (optional) algorithm used for JWT; defaults to `HS256`.

### Email configuration (optional)

The `app.utils.email` module can send basic emails using SMTP. Configure the
following variables if you wish to use this functionality:

- `SMTP_HOST` – address of the SMTP server.
- `SMTP_PORT` – (optional) port number, defaults to `587`.
- `SMTP_USER` – username for authentication (if required).
- `SMTP_PASSWORD` – password for authentication (if required).

## Running the server

After installing dependencies and setting the environment variables, start the
application with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000/` by default.

The application starts a small background scheduler defined in
`app/scheduler.py`. By default it runs a job every minute that prints a message
to the console. You can modify or add jobs in that module to suit your needs.

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

