#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="$ROOT/.env"
LOG_DIR="$ROOT/logs/awa"
PID_DIR="$ROOT/logs/awa_pids"

mkdir -p "$LOG_DIR" "$PID_DIR"

declare -A SERVICES=(
  ["awa_loop"]="python $ROOT/awa_loop.py"
  ["awa_realtime"]="python $ROOT/awa_realtime.py"
  ["awa_gpt"]="python $ROOT/awa_gpt.py"
)

function load_env() {
  if [[ -f "$ENV_FILE" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
  fi
}

function stop_service() {
  local name=$1
  local pidfile="$PID_DIR/$name.pid"
  if [[ -f "$pidfile" ]]; then
    local pid
    pid=$(<"$pidfile")
    if kill -0 "$pid" 2>/dev/null; then
      echo "🛑 Stopping $name (pid $pid)"
      kill "$pid"
      sleep 1
    fi
    rm -f "$pidfile"
  fi
}

function start_service() {
  local name=$1
  local cmd=$2
  local logfile="$LOG_DIR/$name.log"
  local pidfile="$PID_DIR/$name.pid"

  stop_service "$name"

  echo "▶️ Starting $name → logs/$name.log"
  nohup bash -c "$cmd" >"$logfile" 2>&1 &
  echo "$!" >"$pidfile"
}

case "${1:-}" in
  start)
    load_env
    for name in "${!SERVICES[@]}"; do
      start_service "$name" "${SERVICES[$name]}"
    done
    ;;
  stop)
    for name in "${!SERVICES[@]}"; do
      stop_service "$name"
    done
    ;;
  restart)
    "$0" stop
    "$0" start
    ;;
  status)
    for name in "${!SERVICES[@]}"; do
      pidfile="$PID_DIR/$name.pid"
      if [[ -f "$pidfile" ]]; then
        pid=$(<"$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
          echo "✅ $name (pid $pid) running"
        else
          echo "⚠️ $name pid $pid not running, removing stale file"
          rm -f "$pidfile"
        fi
      else
        echo "⚪️ $name stopped"
      fi
    done
    ;;
  *)
    cat <<'EOF'
Usage: scripts/run_awa_stack.sh [start|stop|restart|status]

Runs the Awa bridge helpers (loop, realtime, GPT) under one supervisor.
It loads .env, writes logs to logs/awa/, and keeps pid files for easy restarts.
EOF
    exit 1
    ;;
esac
