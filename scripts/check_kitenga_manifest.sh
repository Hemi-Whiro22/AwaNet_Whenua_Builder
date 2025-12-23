#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
ENV_FILE="$REPO_ROOT/.env"
MANIFEST_URL=${1:-"https://kitenga-main.onrender.com/tools/list"}

if [[ ! -f "$ENV_FILE" ]]; then
  echo "⚠️  .env file missing in repo root."
  exit 1
fi

PIPELINE_TOKEN=$(grep -E '^PIPELINE_TOKEN=' "$ENV_FILE" | cut -d= -f2-)
if [[ -z "$PIPELINE_TOKEN" ]]; then
  echo "⚠️  PIPELINE_TOKEN is empty; please configure it in .env."
  exit 1
fi

echo "🙌  Curling ${MANIFEST_URL}"
curl -sS -H "Authorization: Bearer $PIPELINE_TOKEN" "$MANIFEST_URL" | jq .
