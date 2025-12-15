#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${HUMAN_BEARER_KEY:-}" ]]; then
  source "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.env"
fi

API_URL="${VITE_API_URL:-http://localhost:8000}"
curl -sf -H "Authorization: Bearer ${HUMAN_BEARER_KEY}" "${API_URL}/status/full"
echo
