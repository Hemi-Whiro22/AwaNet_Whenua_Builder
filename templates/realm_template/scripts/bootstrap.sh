#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ ! -f "${ROOT_DIR}/.env" ]]; then
  cp "${ROOT_DIR}/.env.template" "${ROOT_DIR}/.env"
fi

read -rp "Enter bearer token for this realm: " BEARER
if [[ -n "${BEARER}" ]]; then
  sed -i "s|^HUMAN_BEARER_KEY=.*|HUMAN_BEARER_KEY=${BEARER}|" "${ROOT_DIR}/.env"
fi

if [[ -n "${BOOTSTRAP_SKIP_INSTALL:-}" ]]; then
  echo "BOOTSTRAP_SKIP_INSTALL is enabled, skipping dependency installation."
else
  python -m venv "${ROOT_DIR}/.venv"
  if [[ -f "${ROOT_DIR}/requirements.txt" ]]; then
    "${ROOT_DIR}/.venv/bin/pip" install -r "${ROOT_DIR}/requirements.txt"
  fi
  "${ROOT_DIR}/.venv/bin/pip" install -r "${ROOT_DIR}/mini_te_po/requirements.txt"

  if [[ -d "${ROOT_DIR}/te_ao" ]]; then
    pushd "${ROOT_DIR}/te_ao" >/dev/null
    npm install
    popd >/dev/null
  fi

  "${ROOT_DIR}/.venv/bin/python" "${ROOT_DIR}/mini_te_po/bootstrap.py"
fi
