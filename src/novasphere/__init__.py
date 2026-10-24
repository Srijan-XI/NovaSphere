"""
NovaSphere - All-in-One System Diagnostic & Monitoring Suite
==========================================================

A comprehensive system monitoring and diagnostic tool for Windows and Linux.

Features:
- Battery monitoring and analysis
- Hardware diagnostics
- System performance monitoring
- Web, GUI, and CLI interfaces
- Performance graphs and metrics
- Desktop notifications
- Dark/Light themes
"""

__version__ = "2.0.0"
__author__ = "Srijan-XI"
__license__ = "MIT"

from novasphere.utils.config import Config
from novasphere.utils.logger import Logger

# Create global instances
config = Config()
logger = Logger()

__all__ = [
    "__version__",
    "config",
    "logger",
]
