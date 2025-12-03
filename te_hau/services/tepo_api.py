import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import requests

MAURI_PATH = Path("/mauri/global_env.json")


def _load_mauri() -> Dict[str, Any]:
    if MAURI_PATH.exists():
        try:
            return json.loads(MAURI_PATH.read_text())
        except Exception:
            return {}
    return {}


MAURI = _load_mauri()
TEPO_URL = os.getenv("TE_PO_URL", MAURI.get("TE_PO_URL", "http://te_po:8010")).rstrip("/")


def _normalize_path(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"


def te_po_get(path: str, **kwargs):
    path = _normalize_path(path)
    url = f"{TEPO_URL}{path}"
    resp = requests.get(url, **kwargs)
    resp.raise_for_status()
    return resp.json()


def te_po_post(path: str, data: Optional[dict] = None, files=None, **kwargs):
    path = _normalize_path(path)
    url = f"{TEPO_URL}{path}"
    resp = requests.post(url, json=data, files=files, **kwargs)
    resp.raise_for_status()
    return resp.json()


def te_po_request(method: str, path: str, **kwargs):
    """Low-level passthrough to Te Pō for arbitrary methods."""
    path = _normalize_path(path)
    url = f"{TEPO_URL}{path}"
    resp = requests.request(method=method, url=url, **kwargs)
    resp.raise_for_status()
    return resp
