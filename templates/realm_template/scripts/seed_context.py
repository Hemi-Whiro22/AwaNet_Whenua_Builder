#!/usr/bin/env python3
"""Seed Supabase context for a new realm."""

import json
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
SEED_PATH = ROOT / "context" / "context_seed.json"


def load_seed():
    if not SEED_PATH.exists():
        raise SystemExit(f"Seed file not found: {SEED_PATH}")
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def write_seed(data):
    SEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    SEED_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def upsert_supabase(data):
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    table = os.environ.get("SUPABASE_CONTEXT_TABLE", "kitenga_context")
    if not url or not key:
        print("[seed_context] SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY missing; skipping API call.")
        return
    endpoint = f"{url.rstrip('/')}/rest/v1/{table}"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }
    resp = requests.post(endpoint, headers=headers, json=data, timeout=10)
    if resp.status_code not in (200, 201):
        raise SystemExit(f"Supabase insert failed: {resp.status_code} {resp.text}")
    print("[seed_context] Supabase row created:", resp.json())


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--write":
        text = input("Enter default context summary: ").strip()
        data = {
            "summary": text,
            "notes": "Generated via seed_context.py",
        }
        write_seed(data)
        print(f"[seed_context] Wrote {SEED_PATH}")
        return

    data = load_seed()
    upsert_supabase(data)


if __name__ == "__main__":
    main()
