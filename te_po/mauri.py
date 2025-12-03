import json
from pathlib import Path

MAURI_PATH = Path(__file__).resolve().parent.parent / "mauri" / "global_env.json"


def load_mauri() -> dict:
    """Load sanitized Mauri metadata if available."""
    try:
        with MAURI_PATH.open(encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


MAURI = load_mauri()
