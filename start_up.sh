#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_REPO_NAME="${AWA_REPO_NAME:-The_Awa_Network}"

resolve_repo_root() {
  local base_dir="$1"
  local candidate

  # 1. Current directory
  if [[ -d "${base_dir}/te_po" ]]; then
    printf '%s\n' "${base_dir}"
    return 0
  fi

  # 2. Named subdirectory (e.g. ./The_Awa_Network)
  candidate="${base_dir}/${DEFAULT_REPO_NAME}"
  if [[ -d "${candidate}/te_po" ]]; then
    printf '%s\n' "$(cd "${candidate}" && pwd)"
    return 0
  fi

  # 3. Parent/child combination (../The_Awa_Network)
  candidate="$(cd "${base_dir}/.." && pwd)/${DEFAULT_REPO_NAME}"
  if [[ -d "${candidate}/te_po" ]]; then
    printf '%s\n' "$(cd "${candidate}" && pwd)"
    return 0
  fi

  # 4. First directory under base_dir containing te_po (depth 2 to stay quick)
  candidate="$(find "${base_dir}" -maxdepth 2 -type d -name te_po -print -quit 2>/dev/null || true)"
  if [[ -n "${candidate}" ]]; then
    printf '%s\n' "$(cd "$(dirname "${candidate}")" && pwd)"
    return 0
  fi

  return 1
}

ROOT_DIR="${SCRIPT_DIR}"
if [[ -n "${AWA_REPO_ROOT:-}" ]]; then
  if [[ -d "${AWA_REPO_ROOT}/te_po" ]]; then
    ROOT_DIR="$(cd "${AWA_REPO_ROOT}" && pwd)"
  else
    echo "AWA_REPO_ROOT=${AWA_REPO_ROOT} does not look like The Awa Network repo (missing te_po directory)."
    exit 1
  fi
elif [[ ! -d "${ROOT_DIR}/te_po" ]]; then
  ROOT_DIR="$(resolve_repo_root "${SCRIPT_DIR}")" || {
    echo "Unable to locate The Awa Network repo. Set AWA_REPO_ROOT=/path/to/The_Awa_Network and retry."
    exit 1
  }
fi

BACKEND_APP="${BACKEND_APP:-te_po.core.main:app}"
BACKEND_HOST="${BACKEND_HOST:-0.0.0.0}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

PROXY_APP="${PROXY_APP:-realms.tohu_mana_trading_cards.te_po_proxy.main:app}"
PROXY_HOST="${PROXY_HOST:-0.0.0.0}"
PROXY_PORT="${PROXY_PORT:-5000}"

FRONTEND_DIR="${FRONTEND_DIR:-${ROOT_DIR}/realms/tohu_mana_trading_cards/te_ao}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"
FRONTEND_HOST="${FRONTEND_HOST:-0.0.0.0}"

LOG_DIR="${LOG_DIR:-/tmp/awa_startup}"
mkdir -p "${LOG_DIR}"
BACKEND_LOG="${LOG_DIR}/backend.log"
PROXY_LOG="${LOG_DIR}/proxy.log"
FRONTEND_LOG="${LOG_DIR}/frontend.log"

pid_file() {
  local name="$1"
  printf '%s/%s.pid' "${LOG_DIR}" "${name}"
}

kill_port() {
  local port="$1"
  local pids
  pids="$(lsof -ti tcp:"${port}" 2>/dev/null || true)"
  if [[ -n "${pids}" ]]; then
    echo "Killing processes on port ${port}: ${pids}"
    kill ${pids} || true
  fi
}

kill_existing() {
  local name="$1"
  local port="$2"
  local pid_path
  pid_path="$(pid_file "${name}")"
  if [[ -f "${pid_path}" ]]; then
    local pid
    pid="$(cat "${pid_path}")"
    if ps -p "${pid}" >/dev/null 2>&1; then
      echo "Stopping ${name} (pid ${pid})"
      kill "${pid}" || true
    fi
    rm -f "${pid_path}"
  fi
  kill_port "${port}"
}

require_bin() {
  local bin_name="$1"
  local var_name="$2"
  local default_bin
  default_bin="$(command -v "${bin_name}" || true)"
  if [[ -n "${default_bin}" ]]; then
    printf -v "${var_name}" '%s' "${default_bin}"
    return 0
  fi
  echo "Missing ${bin_name}. Please install it and retry."
  exit 1
}

load_env() {
  local env_file="${ROOT_DIR}/.env"
  if [[ -f "${env_file}" ]]; then
    set -a
    # shellcheck disable=SC1090
    source "${env_file}"
    set +a
  fi
}

start_backend() {
  local bin
  require_bin uvicorn bin
  echo "Starting backend (${BACKEND_APP}) on ${BACKEND_HOST}:${BACKEND_PORT}"
  (
    cd "${ROOT_DIR}"
    nohup "${bin}" "${BACKEND_APP}" \
      --host "${BACKEND_HOST}" \
      --port "${BACKEND_PORT}" \
      --reload >"${BACKEND_LOG}" 2>&1 &
    echo $! >"$(pid_file backend)"
  )
}

start_proxy() {
  local bin
  require_bin uvicorn bin
  echo "Starting proxy (${PROXY_APP}) on ${PROXY_HOST}:${PROXY_PORT}"
  (
    cd "${ROOT_DIR}"
    nohup "${bin}" "${PROXY_APP}" \
      --host "${PROXY_HOST}" \
      --port "${PROXY_PORT}" \
      --reload >"${PROXY_LOG}" 2>&1 &
    echo $! >"$(pid_file proxy)"
  )
}

start_frontend() {
  local npm_bin
  require_bin npm npm_bin
  if [[ ! -d "${FRONTEND_DIR}" ]]; then
    echo "Frontend directory ${FRONTEND_DIR} not found."
    exit 1
  fi
  echo "Starting frontend (npm run dev) on ${FRONTEND_HOST}:${FRONTEND_PORT}"
  (
    cd "${FRONTEND_DIR}"
    nohup "${npm_bin}" run dev -- \
      --host "${FRONTEND_HOST}" \
      --port "${FRONTEND_PORT}" >"${FRONTEND_LOG}" 2>&1 &
    echo $! >"$(pid_file frontend)"
  )
}

status_line() {
  local name="$1"
  local pid_path
  pid_path="$(pid_file "${name}")"
  if [[ -f "${pid_path}" ]]; then
    local pid
    pid="$(cat "${pid_path}")"
    if ps -p "${pid}" >/dev/null 2>&1; then
      echo "${name}: running (pid ${pid})"
      return
    fi
  fi
  echo "${name}: not running"
}

main() {
  load_env

  kill_existing backend "${BACKEND_PORT}"
  kill_existing proxy "${PROXY_PORT}"
  kill_existing frontend "${FRONTEND_PORT}"

  start_backend
  sleep 1
  start_proxy
  sleep 1
  start_frontend

  echo "--- process status ---"
  status_line backend
  status_line proxy
  status_line frontend

  echo
  echo "Logs:"
  echo "  tail -f \"${BACKEND_LOG}\""
  echo "  tail -f \"${PROXY_LOG}\""
  echo "  tail -f \"${FRONTEND_LOG}\""
}

main "$@"
