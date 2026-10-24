#!/usr/bin/env bash
set -u

# NovaSphere web server launcher.
# The Flask backend serves the frontend assets and exposes the API.
WEB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$WEB_DIR/.." && pwd)"
FRONTEND_DIR="$WEB_DIR/frontend"
BACKEND_HOST="${NOVASPHERE_WEB_HOST:-127.0.0.1}"
BACKEND_PORT="${NOVASPHERE_WEB_PORT:-8080}"

echo
echo "NovaSphere web server"
echo "===================="

if [[ ! -f "$FRONTEND_DIR/index.html" ]]; then
    echo "ERROR: Frontend files are missing: $FRONTEND_DIR" >&2
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 was not found on PATH." >&2
    echo "Install Python 3.7 or newer and try again." >&2
    exit 1
fi

if ! python3 -c 'import sys; assert sys.version_info >= (3, 7)' >/dev/null 2>&1; then
    echo "ERROR: Python 3.7 or newer is required." >&2
    exit 1
fi

echo "Checking web requirements..."
if ! PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT" python3 -c 'import flask, flask_cors, psutil, sqlite3' >/dev/null 2>&1; then
    echo "Web requirements are missing. Installing from web/requirements.txt..."
    python3 -m pip install -r "$WEB_DIR/requirements.txt" || {
        echo "ERROR: Failed to install web requirements." >&2
        exit 1
    }
fi

echo "Requirements OK."
echo "Frontend: $FRONTEND_DIR"
echo "Backend:  http://$BACKEND_HOST:$BACKEND_PORT"
echo "Press Ctrl+C to stop NovaSphere."
echo

cd "$PROJECT_ROOT"
PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT" \
    python3 -m web.backend.app --host "$BACKEND_HOST" --port "$BACKEND_PORT"
