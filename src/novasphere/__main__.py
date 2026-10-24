"""
Main entry point for NovaSphere when run as a module.

Usage:
    python -m novasphere [options]
    python -m novasphere --gui
    python -m novasphere --cli battery
    python -m novasphere --web --port 8080
"""

import sys
from novasphere.cli import main

if __name__ == "__main__":
    sys.exit(main())
