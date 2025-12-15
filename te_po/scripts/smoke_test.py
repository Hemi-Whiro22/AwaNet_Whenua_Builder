"""
Lightweight smoke test for Te Pō API.

Usage:
    python te_po/scripts/smoke_test.py --base http://localhost:10000
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib import request, error

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from te_po.core.env_loader import load_env  # noqa: E402

TEST_FILE = ROOT / "te_po" / "storage" / "test_files" / "test_document.txt"


def heartbeat(base):
    url = f"{base}/heartbeat"
    try:
        with request.urlopen(url, timeout=10) as resp:
            body = resp.read()
            print(f"[heartbeat] {resp.status}: {body.decode('utf-8')[:120]}")
    except error.URLError as exc:
        print(f"[heartbeat] failed: {exc}")


def whisper(base):
    try:
        import requests  # type: ignore
    except Exception:
        print("[whisper] skipping: requests not installed. pip install requests to run this step.")
        return

    if not TEST_FILE.exists():
        print(f"[whisper] test file missing: {TEST_FILE}")
        return

    files = {"file": ("test_document.txt", TEST_FILE.read_bytes(), "text/plain")}
    data = {
        "whisper": TEST_FILE.read_text(encoding="utf-8"),
        "use_retrieval": "false",
        "run_pipeline": "true",
        "save_vector": "true",
        "source": "smoke_test",
    }
    try:
        resp = requests.post(f"{base}/kitenga/gpt-whisper", data=data, files=files, timeout=30)
        print(f"[whisper] {resp.status_code}")
        try:
            parsed = resp.json()
            print(json.dumps(parsed, indent=2)[:400])
        except Exception:
            print(resp.text[:400])
    except Exception as exc:
        print(f"[whisper] failed: {exc}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="http://localhost:10000", help="Base URL of the running API")
    args = parser.parse_args()

    load_env(str(ROOT / "te_po" / "core" / ".env"))
    heartbeat(args.base)
    whisper(args.base)


if __name__ == "__main__":
    main()
