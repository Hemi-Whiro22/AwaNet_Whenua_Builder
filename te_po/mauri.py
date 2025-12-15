import json
from pathlib import Path
from typing import Dict


CANDIDATES = [
    Path('/mauri/global_env.json'),
    Path(__file__).resolve().parents[1] / 'mauri' / 'global_env.json',
]


def load_mauri() -> Dict:
    """Load mauri metadata from mounted or repo path."""
    for path in CANDIDATES:
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                return {}
    return {}


MAURI = load_mauri()

__all__ = ['MAURI', 'load_mauri']
