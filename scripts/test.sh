#!/usr/bin/env bash
set -euo pipefail

VENV=".venv"

if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment in $VENV"
    python3 -m venv "$VENV"
    echo "Installing dependencies"
    "$VENV"/bin/pip install -r requirements.txt -r requirements-dev.txt
fi

. "$VENV"/bin/activate
pytest "$@"

