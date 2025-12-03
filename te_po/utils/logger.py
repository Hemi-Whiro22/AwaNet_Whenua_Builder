"""
Unified logger for Tiwhanawhana / Awa Network.
Provides:
    log_info()
    log_warn()
    log_error()
    log_event()
    get_logger()

All logs are compatible with FastAPI boot, mana_trace, and Supabase JSON.
"""

import logging
import time
import json
from typing import Any, Dict, Optional


# ============================================================
# 1. BASE LOGGER
# ============================================================

_LOGGER_NAME = "kitenga"


def _ts() -> str:
    """Human readable timestamp."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def _fmt_meta(meta: Optional[Dict[str, Any]]) -> str:
    """Normalize meta field into a nice JSON string."""
    if not meta:
        return "{}"
    try:
        return json.dumps(meta, ensure_ascii=False)
    except Exception:
        return str(meta)


# ============================================================
# 2. SIMPLE EVENT PRINT LOGS (FASTAPI SAFE)
# ============================================================

def log_info(message: str, meta: Dict[str, Any] | None = None) -> None:
    print(f"[INFO]  [{_ts()}] {message} | {_fmt_meta(meta)}")


def log_warn(message: str, meta: Dict[str, Any] | None = None) -> None:
    print(f"[WARN]  [{_ts()}] {message} | {_fmt_meta(meta)}")


def log_error(message: str, meta: Dict[str, Any] | None = None) -> None:
    print(f"[ERROR] [{_ts()}] {message} | {_fmt_meta(meta)}")


def log_event(event: str, meta: Dict[str, Any] | None = None) -> None:
    """Pretty event suitable for mana.trace + ingestion."""
    print(f"[EVENT] [{_ts()}] {event} | {_fmt_meta(meta)}")


# ============================================================
# 3. PYTHON LOGGING BACKEND (FOR FILES + FUTURE)
# ============================================================

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Returns a configured python logger.
    Safe to call multiple times (won't double-add handlers).
    """
    logger = logging.getLogger(name or _LOGGER_NAME)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s — %(levelname)s — %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.INFO)
    return logger
