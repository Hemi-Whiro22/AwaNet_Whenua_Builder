#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m pip install --upgrade pip
python3 -m pip install -r "${ROOT_DIR}/requirements.txt"
python3 -m pip install -e "${ROOT_DIR}/te_hau"

if [[ -f "${ROOT_DIR}/te_hau/requirements.txt" ]]; then
  python3 -m pip install -r "${ROOT_DIR}/te_hau/requirements.txt"
fi

if command -v npm >/dev/null 2>&1; then
  npm install --prefix "${ROOT_DIR}/te_ao"
fi
