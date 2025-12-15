# Te Hau Utilities Module
"""Utility functions and helpers."""

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Get timezone-aware UTC datetime (replaces deprecated utcnow())."""
    return datetime.now(timezone.utc)


def utc_now_iso() -> str:
    """Get ISO formatted UTC datetime string with Z suffix."""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
