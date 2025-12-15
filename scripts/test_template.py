#!/usr/bin/env python3
"""Lightweight regression test for te_hau/project_template."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "te_hau" / "project_template"


def run(cmd, cwd, input_text: str | None = None):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        check=True,
        text=True,
        input=input_text,
        capture_output=True,
    )
    return result.stdout.strip()


def assert_contains(path: Path, needle: str):
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        raise AssertionError(f"{needle!r} not found in {path}")


def main() -> None:
    if not TEMPLATE_DIR.exists():
        raise SystemExit(f"Template directory missing: {TEMPLATE_DIR}")

    with tempfile.TemporaryDirectory() as tmp_dir:
        dest = Path(tmp_dir) / "template_test"
        shutil.copytree(TEMPLATE_DIR, dest)

        # Run new_realm.sh with canned values
        cmd = [
            "./scripts/new_realm.sh",
            "--hostname",
            "kitenga-test.example.com",
            "--tunnel-id",
            "tunnel-123",
            "--tunnel-name",
            "kitenga-test",
            "--pages-project",
            "te-ao-test",
            "--backend-url",
            "https://test.example.com",
            "TestRealm",
        ]
        run(cmd, dest)

        # Ensure placeholders replaced
        assert_contains(dest / ".env", "CF_TUNNEL_ID=tunnel-123")
        assert_contains(dest / "config" / "realm.json", "\"realm\": \"TestRealm\"")
        assert_contains(dest / "config" / "realm.json", "\"default_backend_url\": \"https://test.example.com\"")
        assert_contains(dest / "config" / "proxy.toml", "hostname = \"kitenga-test.example.com\"")
        assert_contains(dest / ".github" / "workflows" / "cloudflare-pages.yml", "projectName: te-ao-test")

        # Run bootstrap.sh (respond with bearer token)
        run(["./scripts/bootstrap.sh"], dest, input_text="token123\n")

        # Inspect bootstrap log output
        env_text = (dest / ".env").read_text(encoding="utf-8")
        if "HUMAN_BEARER_KEY=token123" not in env_text:
            raise AssertionError("bootstrap did not set HUMAN_BEARER_KEY")

        summary = {
            "status": "ok",
            "dest": str(dest),
        }
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
