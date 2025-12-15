"""
Bootstrap script for te_po_proxy

Ensures environment is ready and performs startup checks.
Does NOT call te_po modules (standalone).
"""

import os
import sys
import json
from pathlib import Path


def bootstrap():
    """Bootstrap the proxy."""
    print("[te_po_proxy] Bootstrapping...")

    # Load .env
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        import dotenv
        dotenv.load_dotenv(env_file)

    # Check required env vars
    required = ["REALM_ID", "TE_PO_URL", "BEARER_KEY"]
    missing = [k for k in required if not os.getenv(k)]

    if missing:
        print(f"[te_po_proxy] WARNING: Missing env vars: {', '.join(missing)}")
        print(f"[te_po_proxy] Check .env file and ensure it has all required fields")

    # Load realm manifest
    manifest_file = Path(__file__).parent.parent / \
        "mauri" / "realm_manifest.json"
    if manifest_file.exists():
        with open(manifest_file) as f:
            manifest = json.load(f)
            print(f"[te_po_proxy] Realm: {manifest.get('realm_id', '?')}")
            print(f"[te_po_proxy] Upstream: {manifest.get('te_po_url', '?')}")
    else:
        print(f"[te_po_proxy] No realm manifest found at {manifest_file}")

    print("[te_po_proxy] Bootstrap complete")


if __name__ == "__main__":
    bootstrap()
