"""
Environment loader - simplified UTF-8 enforcement for Te Awa Network.
No encryption - just clean environment loading with mi_NZ.UTF-8 locale support.
"""
import locale
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root first
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def enforce_utf8_locale() -> str:
    """Set UTF-8 locale, preferring mi_NZ.UTF-8 for Māori language support."""
    locales_to_try = ["mi_NZ.UTF-8", "en_NZ.UTF-8", "en_US.UTF-8", "C.UTF-8"]

    for loc in locales_to_try:
        try:
            locale.setlocale(locale.LC_ALL, loc)
            os.environ["LANG"] = loc
            os.environ["LC_ALL"] = loc
            os.environ["LC_CTYPE"] = loc
            return loc
        except locale.Error:
            continue

    # Fallback - just set env vars
    os.environ["LANG"] = "C.UTF-8"
    os.environ["LC_ALL"] = "C.UTF-8"
    return "C.UTF-8"


def enforce_maori_locale() -> str:
    """Force Māori locale preferences, defaulting to mi_NZ.UTF-8."""
    os.environ["LANG"] = "mi_NZ.UTF-8"
    os.environ["LC_ALL"] = "mi_NZ.UTF-8"
    os.environ["LC_CTYPE"] = "mi_NZ.UTF-8"
    return "mi_NZ.UTF-8"


def get_queue_mode() -> str:
    """Get queue mode from environment."""
    mode = os.getenv("QUEUE_MODE", "inline").lower()
    if mode not in ("inline", "rq"):
        raise ValueError(f"QUEUE_MODE must be 'inline' or 'rq', got: {mode}")
    return mode


def get_env(soft: bool = False) -> dict:
    """Returns environment variables as dict. If soft=True, won't raise on missing keys."""
    from te_po.core.config import settings

    env = {}
    missing = []

    for key in settings.model_fields.keys():
        value = getattr(settings, key, None)
        env[key] = value
        if value is None and key in getattr(settings, 'required_keys', []):
            missing.append(key)

    if missing and not soft:
        log_missing(missing)
        raise EnvironmentError(f"Missing required environment keys: {missing}")

    return env


def log_missing(missing: list) -> None:
    """Log missing environment keys."""
    log_path = PROJECT_ROOT / "logs" / "env_validation.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        for key in missing:
            f.write(f"[ENV-ERROR] Missing: {key}\n")


# Enforce UTF-8 on module load
_active_locale = enforce_utf8_locale()
