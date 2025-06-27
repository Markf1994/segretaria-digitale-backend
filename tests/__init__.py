import os

# Ensure a default secret key is available for tests
os.environ.setdefault("SECRET_KEY", "test-secret-key")
