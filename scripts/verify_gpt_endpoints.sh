#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BASE_URL="${KITENGA_MAIN_URL:-https://kitenga-main.onrender.com}"
PIPELINE_TOKEN="${PIPELINE_TOKEN:-}"

if [[ -z "$PIPELINE_TOKEN" ]]; then
  echo "✅ Please export PIPELINE_TOKEN before running this script." >&2
  echo "   export PIPELINE_TOKEN=\"your_real_token\"" >&2
  exit 1
fi

manifest_file=$(mktemp)
plugin_file=$(mktemp)
trap 'rm -f "$manifest_file" "$plugin_file"' EXIT

echo "1) Checking tools manifest ($BASE_URL/openai_tools.json)..."
curl --fail --show-error \
  -H "Authorization: Bearer $PIPELINE_TOKEN" \
  -o "$manifest_file" \
  "${BASE_URL}/openai_tools.json"
head -n 20 "$manifest_file"
echo "   => OK"

echo "2) Checking AI plugin descriptor ($BASE_URL/.well-known/ai-plugin.json)..."
curl --fail --show-error \
  -o "$plugin_file" \
  "${BASE_URL}/.well-known/ai-plugin.json"
head -n 20 "$plugin_file"
echo "   => OK"

echo "All good. GPT Builder can import the manifest and the GPT app can load the plugin descriptor."
