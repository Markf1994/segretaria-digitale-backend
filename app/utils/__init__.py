"""Utility helpers for the application."""

# Re-export the :func:`send_email` helper so modules can simply do:
# ``from app.utils import send_email``.

from .email import send_email
