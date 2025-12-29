"""
Minimal smoke tests for Whakairo stack.
Run after env is set and servers are up.
"""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STACK_SCRIPT = ROOT / "te_hau" / "kitenga_whakairo" / "scripts" / "whakairo_stack.sh"


def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def main():
    print("[whakairo] status ->")
    print(run(f"{STACK_SCRIPT} status").stdout)

    # Basic check: call supabase_sql (read-only) and tehau_health via mcp servers would require an MCP client;
    # here we just ensure the stack script is present and env variables are set.
    missing = []
    for key in ["SUPABASE_URL", "SUPABASE_SERVICE_KEY", "PIPELINE_TOKEN"]:
        if not os.getenv(key):
            missing.append(key)
    if missing:
        print(f"[warn] missing env vars: {', '.join(missing)}")
else:
    print("[ok] core env vars present")


if __name__ == "__main__":
    main()
