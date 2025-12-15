
import json
import re
from pathlib import Path
from typing import Dict, List


CANDIDATES = [
    Path('/mauri/kaitiaki'),
    Path(__file__).resolve().parents[2] / 'mauri' / 'kaitiaki',
]


def _base_dir() -> Path:
    for path in CANDIDATES:
        if path.exists():
            return path
    # default to mounted path
    default = CANDIDATES[0]
    default.mkdir(parents=True, exist_ok=True)
    return default


def list_kaitiaki() -> List[Dict]:
    base = _base_dir()
    entries: List[Dict] = []
    for file in base.glob('*.json'):
        try:
            data = json.loads(file.read_text())
            data.setdefault('id', file.stem)
            entries.append(data)
        except Exception:
            continue
    return entries


def save_kaitiaki(payload: Dict) -> Dict:
    base = _base_dir()
    name = payload.get('name') or 'kaitiaki'
    slug = re.sub(r'[^a-z0-9_-]+', '-', name.lower()).strip('-') or 'kaitiaki'
    file_path = base / f"{slug}.json"
    file_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    return {"ok": True, "slug": slug, "path": str(file_path)}
