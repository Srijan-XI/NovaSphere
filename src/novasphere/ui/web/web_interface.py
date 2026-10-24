"""Compatibility wrapper for the separated web application."""

from web.backend.app import WebInterface as _WebInterface


class WebInterface(_WebInterface):
    """Backward-compatible alias used by the existing package imports."""

    pass


__all__ = ["WebInterface"]
