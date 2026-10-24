#!/usr/bin/env python3
"""Compatibility entry point for the FastAPI-powered NovaSphere web UI."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT))

from web.backend.app import WebInterface


def main() -> None:
    WebInterface().run(host="127.0.0.1", port=5000)


if __name__ == "__main__":
    main()
