#!/usr/bin/env bash
set -u

# NovaSphere web server launcher.
# The FastAPI backend serves the frontend assets and exposes the API.
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
    exit 1;
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "ERROR: python3 was not found on PATH." >&2
    echo "Install Python 3.8 or newer and try again." >&2
    exit 1
fi

if ! python3 -c 'import sys; assert sys.version_info >= (3, 8)' >/dev/null 2>&1; then
    echo "ERROR: Python 3.8 or newer is required." >&2
    exit 1
fi

echo "Checking web requirements..."
PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT" python3 -c 'import fastapi, uvicorn, psutil, sqlite3' >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "Web requirements are missing. Installing from web/requirements.txt..."
    if ! python3 -m pip install -r "$WEB_DIR/requirements.txt"; then
        echo "ERROR: Failed to install web requirements." >&2
        exit 1
    fi
fi

echo "Checking NovaSphere core connection..."
if ! PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT" python3 -c 'from novasphere.core.battery.battery_monitor import create_battery_monitor; from novasphere.core.diagnostics.hardware_tests import create_diagnostics; from novasphere.core.monitoring.system_monitor import create_system_monitor' >/dev/null 2>&1; then
    echo "ERROR: Web backend cannot import the core services from src/novasphere/core." >&2
    echo "Confirm that the project is started from the repository and that src is present." >&2
    exit 1
fi

echo "Requirements OK."
echo "Core services connected."
echo "Frontend: $FRONTEND_DIR"
echo "Backend:  http://$BACKEND_HOST:$BACKEND_PORT"
echo "Press Ctrl+C to stop NovaSphere."
echo

cd "$PROJECT_ROOT"
PYTHONPATH="$PROJECT_ROOT/src:$PROJECT_ROOT" \
    python3 -m web.backend.app --host "$BACKEND_HOST" --port "$BACKEND_PORT"
