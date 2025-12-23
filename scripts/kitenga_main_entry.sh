#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PORT="${PORT:-10000}"

"$ROOT/scripts/run_awa_stack.sh" start
trap "$ROOT/scripts/run_awa_stack.sh stop" EXIT

exec uvicorn kitenga_mcp.app_server:app --host 0.0.0.0 --port "$PORT"
