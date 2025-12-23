#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
ENV_FILE="$REPO_ROOT/.env"
URL="https://kitenga-main.onrender.com/tools/call"
BODY_FILE=""

usage() {
  cat <<'EOF'
Usage: run_kitenga_tool_call.sh [-u URL] [-f JSON_FILE]

Reads PIPELINE_TOKEN from .env and POSTs the provided JSON to the kitenga-main /tools/call endpoint.
Send the body via STDIN when no file is specified:

cat <<'JSON' | scripts/run_kitenga_tool_call.sh
{
  "domain": "kitenga",
  "command": "vector_batch_status",
  "input": {
    "batch_id": "test"
  }
}
JSON
EOF
  exit 1
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -u|--url) URL="$2"; shift 2 ;;
    -f|--file) BODY_FILE="$2"; shift 2 ;;
    -h|--help) usage ;;
    *) usage ;;
  esac
done

if [[ ! -f "$ENV_FILE" ]]; then
  echo "⚠️  .env missing in repo root"
  exit 1
fi

PIPELINE_TOKEN=$(grep -E '^PIPELINE_TOKEN=' "$ENV_FILE" | cut -d= -f2-)
if [[ -z "$PIPELINE_TOKEN" ]]; then
  echo "⚠️  PIPELINE_TOKEN not set"
  exit 1
fi

if [[ -n "$BODY_FILE" ]]; then
  BODY=$(cat "$BODY_FILE")
else
  if [[ -t 0 ]]; then
    echo "Provide JSON payload via stdin or -f/--file."
    usage
  fi
  BODY=$(cat -)
fi

curl -sS -X POST "$URL" \
  -H "Authorization: Bearer $PIPELINE_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$BODY" | jq .
