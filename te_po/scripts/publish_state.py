import argparse
import datetime
import json
import os
import subprocess
from pathlib import Path

import yaml
from supabase import create_client
from te_po.core.config import settings

# Remove redundant dotenv calls
SUPABASE_URL = settings.supabase_url
SUPABASE_KEY = settings.supabase_service_role_key

if not SUPABASE_URL or not SUPABASE_KEY:
    raise EnvironmentError("SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY is not set.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

STATE_FILE = Path(__file__).resolve().parents[1] / "state.yaml"


def get_git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip()
    except Exception:
        return "unknown"


def load_state() -> dict:
    if not STATE_FILE.exists():
        raise FileNotFoundError(f"state.yaml not found at: {STATE_FILE}")
    return yaml.safe_load(STATE_FILE.read_text(encoding="utf-8")) or {}


def utc_now_iso() -> str:
    # Render-friendly + consistent
    return datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def publish_state(dry_run: bool) -> None:
    state = load_state()
    meta = state.setdefault("meta", {})
    meta["commit"] = get_git_commit()
    meta["last_updated"] = utc_now_iso()

    repo = meta.get("repo", "unknown")
    env = meta.get("environment", "unknown")
    branch = meta.get("branch", "main")
    commit = meta.get("commit", "unknown")
    version = meta.get("version", 1)

    payload = {
        "id": f"{repo}:{env}",
        "repo": repo,
        "branch": branch,
        "commit": commit,
        "version": version,
        "last_updated": meta["last_updated"],
        "state_yaml": yaml.safe_dump(state, sort_keys=False, allow_unicode=True),
    }

    # Debug: Log the payload before sending
    print("Debug: Payload to be sent:")
    print(json.dumps(payload, indent=2))

    if dry_run:
        print("[DRY RUN] Payload to be upserted:")
        print(yaml.safe_dump(payload, sort_keys=False, allow_unicode=True))
        return

    res = supabase.table("project_state_public").upsert(payload).execute()
    if getattr(res, "error", None):
        raise RuntimeError(f"Failed to publish state: {res.error}")

    print("State published successfully.")


def main():
    parser = argparse.ArgumentParser(description="Publish state to Supabase.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()

    if args.dry_run:
        publish_state(dry_run=True)
    elif args.live:
        publish_state(dry_run=False)
    else:
        raise SystemExit("Use --dry-run or --live")


if __name__ == "__main__":
    main()

# Ensure this script is standalone and not executed on FastAPI app startup.