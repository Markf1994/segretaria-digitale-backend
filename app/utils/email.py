"""Utility functions for sending email via SMTP.

`send_email` provides a very small wrapper around :class:`smtplib.SMTP` that
loads connection details from environment variables.  It is intentionally simple
so that it can be reused in background jobs or request handlers.
"""

import os
import smtplib
from email.message import EmailMessage


def send_email(to_email: str, subject: str, body: str, from_email: str | None = None) -> None:
    """Send a plain text email using credentials from environment variables.

    Environment variables used:
        ``SMTP_HOST`` - hostname of the SMTP server (required)
        ``SMTP_PORT`` - port of the SMTP server, defaults to ``587``
        ``SMTP_USER`` - username used for authentication (optional)
        ``SMTP_PASSWORD`` - password used for authentication (optional)
    """

    host = os.getenv("SMTP_HOST")
    if host is None:
        raise ValueError("SMTP_HOST environment variable not set")

    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_addr = from_email or username

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP(host, port) as server:
        server.starttls()
        if username and password:
            server.login(username, password)
        server.send_message(msg)

