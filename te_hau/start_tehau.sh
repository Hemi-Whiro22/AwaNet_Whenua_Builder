#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$ROOT_DIR/te_po/kitenga/logs"
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

KITENGA_PORT="${KITENGA_PORT:-8000}"
CF_TUNNEL_ID="${CF_TUNNEL_ID:-}"
CF_TUNNEL_NAME="${CF_TUNNEL_NAME:-}"
CF_TUNNEL_HOSTNAME="${CF_TUNNEL_HOSTNAME:-kitenga-whiro.den-of-the-pack.com}"
CLOUDFLARED_DIR="${HOME}/.cloudflared"
CLOUDFLARED_CONFIG="$CLOUDFLARED_DIR/config.yml"
CLOUDFLARED_CREDS="$CLOUDFLARED_DIR/${CF_TUNNEL_ID}.json"

MCP_LOG="$LOG_DIR/kitenga_mcp.log"
BACKEND_LOG="$LOG_DIR/te_po.log"
TUNNEL_LOG="$LOG_DIR/cloudflared.log"
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

wait_for_backend() {
  local health_url="http://127.0.0.1:${KITENGA_PORT}/docs"
  echo "[health] waiting for backend at $health_url ..."
  for attempt in {1..120}; do
    if curl -fsS "$health_url" >/dev/null 2>&1; then
      echo "[health] backend is responding."
      return 0
    fi
    sleep 1
  done
  echo "[health] backend did not become ready after 120s" >&2
}

start_cloudflare_tunnel() {
  if [[ -z "$CF_TUNNEL_ID" || -z "$CF_TUNNEL_NAME" ]]; then
    echo "[cloudflared] CF_TUNNEL_ID or CF_TUNNEL_NAME not provided; skipping tunnel."
    return
  fi
  if ! command -v cloudflared >/dev/null 2>&1; then
    echo "[cloudflared] cloudflared binary not found; skipping tunnel."
    return
  fi

  mkdir -p "$CLOUDFLARED_DIR"

  if [[ ! -f "$CLOUDFLARED_CONFIG" ]]; then
    echo "[cloudflared] creating $CLOUDFLARED_CONFIG for tunnel $CF_TUNNEL_NAME..."
    cat <<EOF >"$CLOUDFLARED_CONFIG"
tunnel: $CF_TUNNEL_ID
credentials-file: $CLOUDFLARED_CREDS

ingress:
  - hostname: $CF_TUNNEL_HOSTNAME
    service: http://localhost:$KITENGA_PORT
  - service: http_status:404
EOF
  fi

  echo "[cloudflared] starting tunnel $CF_TUNNEL_NAME ($CF_TUNNEL_ID)"
  cloudflared tunnel run "$CF_TUNNEL_NAME" >>"$TUNNEL_LOG" 2>&1 &
  pids+=($!)
}

echo "[env] Launching Kitenga Whiro on port $KITENGA_PORT"
if [[ -n "$CF_TUNNEL_ID" && -n "$CF_TUNNEL_NAME" ]]; then
  echo "[env] Cloudflare tunnel: $CF_TUNNEL_NAME ($CF_TUNNEL_ID)"
  echo "[env] Tunnel credentials: $CLOUDFLARED_CREDS"
fi

echo "[kitenga] starting MCP server..."
python "$ROOT_DIR/te_po/kitenga/start_kitenga.py" >>"$MCP_LOG" 2>&1 &
pids+=($!)

echo "[te_po] starting FastAPI backend..."
uvicorn te_po.main:app --reload --host 0.0.0.0 --port "$KITENGA_PORT" >>"$BACKEND_LOG" 2>&1 &
pids+=($!)

start_cloudflare_tunnel
wait_for_backend || true

echo "[logs] tailing $MCP_LOG and $BACKEND_LOG (Ctrl+C to stop)…"
tail -F "$MCP_LOG" "$BACKEND_LOG" "$TUNNEL_LOG"
