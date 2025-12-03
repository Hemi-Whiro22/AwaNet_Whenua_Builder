import os
import locale
from dotenv import load_dotenv
from pathlib import Path

ENV_CANDIDATES = [
    Path(__file__).resolve().parent / ".env",
    Path(__file__).resolve().parents[1] / ".env",
    Path(__file__).resolve().parents[2] / ".env",
]

_env_loaded = False
for candidate in ENV_CANDIDATES:
    if candidate.exists():
        load_dotenv(candidate)
        _env_loaded = True
        break

if not _env_loaded:
    load_dotenv()

REQUIRED_KEYS = [
    "OPENAI_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_ROLE_KEY",
    "DATABASE_URL",
    "TESSERACT_PATH",
]


def load_env(env_path: str | None = None) -> None:
    """Load environment variables from .env if provided."""
    target = env_path
    if not target:
        for candidate in ENV_CANDIDATES:
            if candidate.exists():
                target = str(candidate)
                break
    load_dotenv(target)


def enforce_utf8_locale() -> None:
    """Set UTF-8 locale using LANG/LC_ALL or fallback to en_US.UTF-8."""
    lang = os.getenv("LANG", "en_US.UTF-8")
    lc_all = os.getenv("LC_ALL", lang)
    try:
        locale.setlocale(locale.LC_ALL, lc_all)
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
        except locale.Error:
            pass
    os.environ["LANG"] = lang
    os.environ["LC_ALL"] = lc_all


def enforce_maori_locale() -> str:
    """Force Māori locale preferences, falling back to mi_NZ.UTF-8."""
    preferred = ["mi_NZ.UTF-8", "mi_NZ.utf8", "mi_NZ"]
    current = os.environ.get("LANG", "")
    if current not in preferred:
        os.environ["LANG"] = "mi_NZ.UTF-8"
        os.environ["LC_ALL"] = "mi_NZ.UTF-8"
        os.environ["LC_CTYPE"] = "mi_NZ.UTF-8"
    return os.environ.get("LANG", "mi_NZ.UTF-8")


def current_locale() -> str:
    """Return current locale string."""
    try:
        return locale.setlocale(locale.LC_ALL, None)
    except Exception:
        return os.getenv("LANG", "unknown")


def get_env(soft: bool = False):
    """Returns a validated environment dict. soft=True returns partial without raising."""
    missing = []
    env = {}

    for key in REQUIRED_KEYS:
        value = os.getenv(key)
        if not value:
            missing.append(key)
        env[key] = value

    if missing and not soft:
        log_missing(missing)
        raise EnvironmentError(f"Missing required environment keys: {missing}")

    return env


def log_missing(missing):
    log_path = Path(__file__).resolve().parents[3] / "logs/env_validation.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        for key in missing:
            f.write(f"[ENV-ERROR] Missing: {key}\n")
