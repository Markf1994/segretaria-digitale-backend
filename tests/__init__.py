import os

# Ensure a default secret key is available for tests
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("GOOGLE_CLIENT_ID", "test-client")
os.environ.setdefault("G_SHIFT_CAL_ID", "test-shift-cal")
