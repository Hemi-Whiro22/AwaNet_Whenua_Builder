#!/usr/bin/env bash
set -euo pipefail

# Helper to start/stop/status Whakairo Codex and shared MCP realms.
# Usage:
#   scripts/whakairo_stack.sh start   # load env, start servers
#   scripts/whakairo_stack.sh stop    # stop servers
#   scripts/whakairo_stack.sh status  # show PIDs
#   scripts/whakairo_stack.sh sync    # pull carver context from Supabase

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
WHAKAIRO_DIR="${ROOT}/te_hau/kitenga_whakairo"
LOG_DIR="${WHAKAIRO_DIR}/logs"
PID_DIR="${WHAKAIRO_DIR}/state/pids"
mkdir -p "${LOG_DIR}" "${PID_DIR}"

ENV_CANDIDATES=(
  "${WHAKAIRO_DIR}/.env.whakairo"
  "${ROOT}/.env.whakairo"
  "${ROOT}/.env"
)

load_env() {
  for f in "${ENV_CANDIDATES[@]}"; do
    if [[ -f "$f" ]]; then
      set -a
      # shellcheck disable=SC1090
      source "$f"
      set +a
      echo "💠 Loaded env from $f"
      return 0
    fi
  done
  echo "⚠️  No env file found; relying on current environment."
}

declare -a SERVERS=(
  "whakairo:python3 -m te_hau.cli.start_whakairo"
  "tepo:python3 ${ROOT}/.mcp/tepo/server.py"
  "tehau:python3 ${ROOT}/.mcp/tehau/server.py"
  "git:python3 ${ROOT}/.mcp/git/server.py"
  "render:python3 ${ROOT}/.mcp/render/server.py"
  "supabase:python3 ${ROOT}/.mcp/supabase/server.py"
  "openai:python3 ${ROOT}/.mcp/openai/server.py"
  "cloudflare:python3 ${ROOT}/.mcp/cloudflare/server.py"
)

start_server() {
  local name cmd
  name="$1"
  cmd="$2"
  local pid_file="${PID_DIR}/${name}.pid"

  if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
    echo "▶️  ${name} already running (pid $(cat "$pid_file"))."
    return
  fi

  echo "▶️  Starting ${name}..."
  nohup bash -lc "$cmd" >"${LOG_DIR}/${name}.log" 2>&1 &
  echo $! >"$pid_file"
  echo "✅ ${name} pid $(cat "$pid_file"), log ${LOG_DIR}/${name}.log"
}

stop_server() {
  local name="$1"
  local pid_file="${PID_DIR}/${name}.pid"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" 2>/dev/null; then
      echo "⏹  Stopping ${name} (pid ${pid})"
      kill "$pid" 2>/dev/null || true
    else
      echo "ℹ️  ${name} not running; cleaning stale pid."
    fi
    rm -f "$pid_file"
  else
    echo "ℹ️  No pid file for ${name}"
  fi
}

status_server() {
  local name="$1"
  local pid_file="${PID_DIR}/${name}.pid"
  if [[ -f "$pid_file" ]] && kill -0 "$(cat "$pid_file")" 2>/dev/null; then
    echo "✅ ${name}: running (pid $(cat "$pid_file"))"
  else
    echo "❌ ${name}: not running"
  fi
}

start_all() {
  load_env
  for entry in "${SERVERS[@]}"; do
    IFS=":" read -r name cmd <<<"$entry"
    start_server "$name" "$cmd"
  done
  echo "🔄 Running optional sync_carver_context..."
  python3 "${WHAKAIRO_DIR}/sync_carver_context.py" || echo "⚠️  sync_carver_context failed (check Supabase env)"
}

stop_all() {
  for entry in "${SERVERS[@]}"; do
    IFS=":" read -r name cmd <<<"$entry"
    stop_server "$name"
  done
}

status_all() {
  for entry in "${SERVERS[@]}"; do
    IFS=":" read -r name cmd <<<"$entry"
    status_server "$name"
  done
}

sync_only() {
  load_env
  python3 "${WHAKAIRO_DIR}/sync_carver_context.py"
}

case "${1:-}" in
  start) start_all ;;
  stop) stop_all ;;
  status) status_all ;;
  sync) sync_only ;;
  *)
    echo "Usage: $0 {start|stop|status|sync}"
    exit 1
    ;;
esac
