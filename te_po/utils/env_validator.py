"""
Environment validator for Tiwhanawhana / Awa Network.

Checks:
    - Required environment variables exist
    - Values are not empty
    - Keys are masked before logging

Compatible with: main.py, logger.py, mana_trace
"""

import os
from typing import Dict, List

from te_po.utils.logger import log_info, log_warn, log_error


# Set REQUIRED .env vars here (canonical)
REQUIRED_VARS: List[str] = [
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "OPENAI_API_KEY",
    "DATABASE_URL",
    "TESSERACT_PATH",
]


def _mask(value: str) -> str:
    """Mask secrets safely for logs."""
    if not value:
        return "None"
    if len(value) <= 6:
        return "***"
    return value[:3] + "***" + value[-3:]


def validate_environment() -> Dict[str, Dict[str, str]]:
    """
    Validates required environment variables from .env.

    Returns a dictionary of:
        - present keys (masked)
        - missing keys
    """

    log_info("🔧 Initializing Tiwhanawhana environment validation...")

    missing = []
    present = {}

    for key in REQUIRED_VARS:
        value = os.getenv(key)

        if not value:
            missing.append(key)
        else:
            present[key] = _mask(value)

    # ─────────────────────────────────────
    # Logging
    # ─────────────────────────────────────

    if missing:
        log_warn("⚠️  Missing required environment variables: " +
                 ", ".join(missing))
        log_warn("⚠️  Application may not function correctly without these variables")
        log_warn(
            f"⚠️  Environment partially configured ({len(present)}/{len(REQUIRED_VARS)})")
    else:
        log_info("✅ All required environment variables are present")

    return {
        "present": present,
        "missing": missing,
        "count": f"{len(present)}/{len(REQUIRED_VARS)}",
    }
