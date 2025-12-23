#!/usr/bin/env bash
# Author: awa developer (Kitenga Whiro [Adrian Hemi])
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
TESTRUNNER="$SCRIPT_DIR/run_all_tests.sh"
cd "$REPO_ROOT"

TARGET="${1:-local}"
PORT="${PORT:-8000}"
HOST="${HOST:-127.0.0.1}"
APP_MODULE="${APP_MODULE:-te_po.core.main:app}"
WAIT_TIMEOUT="${WAIT_TIMEOUT:-30}"

start_local_backend() {
  echo "Starting local backend ($APP_MODULE) on http://$HOST:$PORT ..."
  python -m uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT" &
  SERVER_PID=$!
  trap 'kill "${SERVER_PID}" >/dev/null 2>&1 || true' EXIT

  local api_url="http://$HOST:$PORT"
  for i in $(seq 1 "$WAIT_TIMEOUT"); do
    if curl -sSf "$api_url/heartbeat" >/dev/null 2>&1; then
      echo "Backend responded on attempt $i."
      break
    fi
    echo "Waiting for backend to start ($i/$WAIT_TIMEOUT)..."
    sleep 1
  done

  if ! curl -sSf "$api_url/heartbeat" >/dev/null 2>&1; then
    echo "Backend failed to respond after $WAIT_TIMEOUT seconds."
    kill "${SERVER_PID}" >/dev/null 2>&1 || true
    exit 1
  fi

  export API_URL="$api_url"
  export STATE_BASE_URL="$api_url"
  export TARGET

  echo "Running test suite against $API_URL ..."
  bash "$TESTRUNNER" "$TARGET"
}

start_remote_tests() {
  API_URL="${TARGET_API_URL:-https://tiwhanawhana-backend.onrender.com}"
  STATE_BASE_URL="${STATE_BASE_URL:-$API_URL}"
  export API_URL STATE_BASE_URL TARGET

  echo "Running tests against remote backend ($API_URL) ..."
  bash "$TESTRUNNER" "$TARGET"
}

if [ "$TARGET" = "local" ]; then
  start_local_backend
else
  start_remote_tests
fi
