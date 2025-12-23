#!/usr/bin/env python3
"""
Git commit + push helper for the Kitenga Whiro kaitiaki.
Runs the context sync + repo review checklist before committing so the mauri artifacts stay fresh.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECK_SCRIPTS = [
    ["python", "analysis/generate_repo_tree.py"],
    ["python", "analysis/kaitiaki_context_sync.py"],
    ["python", "scripts/kaitiaki_sanity.py"],
    ["python", "-m", "analysis.run_repo_review"],
]


def get_env():
    env = os.environ.copy()
    prev = env.get("PYTHONPATH", "")
    root = str(REPO_ROOT)
    env["PYTHONPATH"] = f"{root}:{prev}" if prev else root
    return env


def run_checklist():
    env = get_env()
    for cmd in CHECK_SCRIPTS:
        result = subprocess.run(cmd, env=env)
        if result.returncode != 0:
            raise SystemExit(f"Checklist step failed: {' '.join(cmd)}")


def git_commit_push(message: str):
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", message], check=True)
    subprocess.run(["git", "push"], check=True)


def main():
    parser = argparse.ArgumentParser(description="Run AwaNet pre-commit checklist then push.")
    parser.add_argument("-m", "--message", required=True, help="Git commit message")
    args = parser.parse_args()

    print("⚙️  Running kaitiaki checklist")
    run_checklist()
    print("✅ Checklist complete; committing")
    git_commit_push(args.message)
    print("🚀 Push complete")


if __name__ == "__main__":
    main()
