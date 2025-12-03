import requests
from rich import print
import json
import os

BASE_URL = os.getenv("TE_PO_URL") or os.getenv("TE_PŌ_URL") or "http://localhost:8010"


def api_get(path):
    try:
        r = requests.get(f"{BASE_URL}{path}")
        r.raise_for_status()
        return r.json()
    except Exception as e:  # noqa: BLE001
        print(f"[red]API error (GET {path}): {e}[/red]")
        return None


def api_post(path, payload):
    try:
        r = requests.post(f"{BASE_URL}{path}", json=payload)
        r.raise_for_status()
        return r.json()
    except Exception as e:  # noqa: BLE001
        print(f"[red]API error (POST {path}): {e}[/red]")
        return None


def pretty(data):
    print(json.dumps(data, indent=2, ensure_ascii=False))
