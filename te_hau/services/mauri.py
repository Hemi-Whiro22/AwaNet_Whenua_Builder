import json
from pathlib import Path


def load_mauri() -> dict:
    """Load mauri config from mounted /mauri or repo fallback."""
    candidates = [
        Path('/mauri/global_env.json'),
        Path(__file__).resolve().parents[2] / 'mauri' / 'global_env.json',
    ]
    for path in candidates:
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                return {}
    return {}


MAURI = load_mauri()
