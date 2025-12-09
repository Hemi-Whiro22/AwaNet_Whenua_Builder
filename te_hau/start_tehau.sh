#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$SCRIPT_DIR/kitenga_mcp/logs"
mkdir -p "$LOG_DIR"

# Activate virtualenv if present so python/uvicorn use project deps
if [[ -f "$ROOT_DIR/.venv/bin/activate" ]]; then
  source "$ROOT_DIR/.venv/bin/activate"
fi

# Load environment variables (root .env, then fallback to te_po/core/.env)
if [[ -f "$ROOT_DIR/.env" ]]; then
  set -a
  source "$ROOT_DIR/.env"
  set +a
elif [[ -f "$ROOT_DIR/te_po/core/.env" ]]; then
  set -a
  source "$ROOT_DIR/te_po/core/.env"
  set +a
fi

export PYTHONPATH="$ROOT_DIR:${PYTHONPATH:-}"

MCP_LOG="$LOG_DIR/kitenga_mcp.log"
BACKEND_LOG="$LOG_DIR/te_po.log"
TUNNEL_LOG="$LOG_DIR/awa_tunnel.log"
touch "$MCP_LOG" "$BACKEND_LOG" "$TUNNEL_LOG"

pids=()
cleanup() {
  for pid in "${pids[@]:-}"; do
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT

echo "[kitenga] starting MCP server..."
python "$SCRIPT_DIR/kitenga_mcp/start_kitenga.py" >>"$MCP_LOG" 2>&1 &
pids+=($!)

echo "[te_po] starting FastAPI backend..."
uvicorn te_po.main:app --reload --host 0.0.0.0 --port 8000 >>"$BACKEND_LOG" 2>&1 &
pids+=($!)

# Optional tunnel start after services
if command -v awa_tunnel >/dev/null 2>&1; then
  echo "[tunnel] starting awa_tunnel..."
  awa_tunnel >>"$TUNNEL_LOG" 2>&1 &
  pids+=($!)
else
  echo "[tunnel] awa_tunnel not found; skipping."
fi

echo "[logs] tailing $MCP_LOG and $BACKEND_LOG (Ctrl+C to stop)…"
tail -F "$MCP_LOG" "$BACKEND_LOG" "$TUNNEL_LOG"
