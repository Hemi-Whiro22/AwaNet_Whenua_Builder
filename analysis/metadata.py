from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from te_po.stealth_ocr import StealthOCR

AUTHOR_TAG = "awa developer (Kitenga Whiro [Adrian Hemi])"
_STEALTH = StealthOCR()


def build_metadata(resource: str) -> Dict[str, Any]:
    protection = _STEALTH._generate_protection_metadata(resource)
    return {
        "author": AUTHOR_TAG,
        "resource": resource,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "protection": protection,
    }


def write_metadata_file(path: Path, resource: str) -> Dict[str, Any]:
    metadata = build_metadata(resource)
    meta_path = path.with_name(f"{path.stem}.meta.json")
    meta_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    return metadata


def append_markdown_footer(path: Path, metadata: Dict[str, Any]) -> None:
    content = path.read_text(encoding="utf-8")
    body = content.split("\n---\n")[0]
    footer = "\n\n---\n"
    footer += f"Author: {metadata['author']}\n"
    footer += f"Protection: {json.dumps(metadata['protection'], ensure_ascii=False)}\n"
    path.write_text(body + footer, encoding="utf-8")
