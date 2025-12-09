#!/usr/bin/env bash
#
# Quick launcher for Kitenga Whiro (backend + frontend + MCP) with hot reload.
# - Kills anything already bound to ports 8000 (backend) and 5173 (frontend).
# - Starts uvicorn with --reload.
# - Starts Vite dev server on 0.0.0.0:5173.
# - Starts MCP server (te_hau/kitenga_mcp) and optional awa_tunnel when present.
#
# Usage (from repo root):
#   chmod +x run_dev.sh
#   ./run_dev.sh
#
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_BIN="${ROOT_DIR}/.venv/bin"
PYTHON_BIN="${VENV_BIN}/python"
BACKEND_PORT=8000
FRONTEND_PORT=5173
BACKEND_LOG=/tmp/uvicorn.log
FRONTEND_LOG=/tmp/vite.log
MCP_LOG=/tmp/kitenga_mcp.log
TUNNEL_LOG=/tmp/awa_tunnel.log
WORKER_LOG=/tmp/rq_worker.log
WORKER_URGENT_LOG=/tmp/rq_worker_urgent.log
WORKER_DEFAULT_LOG=/tmp/rq_worker_default.log
WORKER_SLOW_LOG=/tmp/rq_worker_slow.log
REDIS_PORT=6379
REDIS_CONTAINER="kitenga-redis"

# Ensure virtualenv binaries are first in PATH so uvicorn/rq use local deps
if [[ ! -x "${VENV_BIN}/uvicorn" ]]; then
  echo "Missing ${VENV_BIN}/uvicorn. Create venv and install deps: python -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi
export PATH="${VENV_BIN}:${PATH}"
if [[ -x "${PYTHON_BIN}" ]]; then
  PYTHON_BIN="${PYTHON_BIN}"
else
  PYTHON_BIN="$(command -v python3)"
fi

# Load .env if present so MCP/Supabase creds are available
if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  source "${ROOT_DIR}/.env"
  set +a
fi

kill_port() {
  local port="$1"
  pids=$(lsof -ti tcp:"$port" || true)
  if [[ -n "${pids}" ]]; then
    echo "Killing processes on port ${port}: ${pids}"
    kill ${pids} || true
  fi
}

start_redis() {
  if lsof -ti tcp:"${REDIS_PORT}" >/dev/null 2>&1; then
    echo "Redis already running on port ${REDIS_PORT}"
    return
  fi
  if command -v docker >/dev/null 2>&1; then
    echo "Starting Redis via Docker on :${REDIS_PORT}"
    docker run -d --name "${REDIS_CONTAINER}" -p "${REDIS_PORT}:${REDIS_PORT}" redis:latest >/dev/null 2>&1 || true
  else
    echo "Docker not available; please start Redis manually on port ${REDIS_PORT}"
  fi
}

start_worker() {
  echo "Starting RQ workers (urgent/default/slow)..."
  (
    cd "${ROOT_DIR}"
    nohup "${ROOT_DIR}/.venv/bin/rq" worker urgent --concurrency 2 >"${WORKER_URGENT_LOG}" 2>&1 &
    echo $! > /tmp/kitenga_worker_urgent.pid
    nohup "${ROOT_DIR}/.venv/bin/rq" worker default --concurrency 4 >"${WORKER_DEFAULT_LOG}" 2>&1 &
    echo $! > /tmp/kitenga_worker_default.pid
    nohup "${ROOT_DIR}/.venv/bin/rq" worker slow --concurrency 1 >"${WORKER_SLOW_LOG}" 2>&1 &
    echo $! > /tmp/kitenga_worker_slow.pid
  )
}

start_mcp() {
  local mcp_entry="${ROOT_DIR}/te_hau/kitenga_mcp/start_kitenga.py"
  if [[ ! -f "${mcp_entry}" ]]; then
    echo "MCP entrypoint not found at ${mcp_entry}; skipping MCP start."
    return
  fi
  echo "Starting MCP server (kitenga) -> ${MCP_LOG}"
  nohup "${PYTHON_BIN}" "${mcp_entry}" >"${MCP_LOG}" 2>&1 &
  echo $! > /tmp/kitenga_mcp.pid
}

start_tunnel() {
  if command -v awa_tunnel >/dev/null 2>&1; then
    echo "Starting awa_tunnel -> ${TUNNEL_LOG}"
    nohup awa_tunnel >"${TUNNEL_LOG}" 2>&1 &
    echo $! > /tmp/awa_tunnel.pid
  else
    echo "awa_tunnel not found; skipping tunnel start."
  fi
}

kill_port "${BACKEND_PORT}"
kill_port "${FRONTEND_PORT}"

start_redis
start_worker
start_mcp
start_tunnel

echo "Starting backend (uvicorn --reload on :${BACKEND_PORT}) -> ${BACKEND_LOG}"
(
  cd "${ROOT_DIR}"
  nohup "${VENV_BIN}/uvicorn" te_po.core.main:app --reload --host 0.0.0.0 --port "${BACKEND_PORT}" >"${BACKEND_LOG}" 2>&1 &
  echo $! > /tmp/kitenga_backend.pid
)
BACK_PID=$(cat /tmp/kitenga_backend.pid)

echo "Starting frontend (Vite dev server on :${FRONTEND_PORT}) -> ${FRONTEND_LOG}"
(
  cd "${ROOT_DIR}/te_ao"
  nohup npm run dev -- --host 0.0.0.0 --port "${FRONTEND_PORT}" >"${FRONTEND_LOG}" 2>&1 &
  echo $! > /tmp/kitenga_frontend.pid
)
FRONT_PID=$(cat /tmp/kitenga_frontend.pid)

MCP_PID=$(cat /tmp/kitenga_mcp.pid 2>/dev/null || true)
TUNNEL_PID=$(cat /tmp/awa_tunnel.pid 2>/dev/null || true)

echo "Backend PID: ${BACK_PID} | Frontend PID: ${FRONT_PID} | MCP PID: ${MCP_PID:-n/a} | Tunnel PID: ${TUNNEL_PID:-n/a}"
echo "Logs: tail -f ${BACKEND_LOG} ${FRONTEND_LOG} ${MCP_LOG} ${TUNNEL_LOG} ${WORKER_URGENT_LOG} ${WORKER_DEFAULT_LOG} ${WORKER_SLOW_LOG}"
echo "Stop: kill \$(cat /tmp/kitenga_backend.pid /tmp/kitenga_frontend.pid /tmp/kitenga_mcp.pid /tmp/awa_tunnel.pid /tmp/kitenga_worker_urgent.pid /tmp/kitenga_worker_default.pid /tmp/kitenga_worker_slow.pid 2>/dev/null)"
