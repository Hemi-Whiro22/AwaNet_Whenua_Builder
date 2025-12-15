#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[boot] Creating virtualenv..."
  python3 -m venv "${VENV_DIR}"
fi

echo "[boot] Installing dependencies..."
source "${VENV_DIR}/bin/activate"
pip install --upgrade pip >/dev/null
pip install -r "${ROOT_DIR}/requirements.txt" >/dev/null

echo "[boot] Starting run_dev.sh ..."
"${ROOT_DIR}/run_dev.sh"
