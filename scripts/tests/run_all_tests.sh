#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(dirname "$0")"
cd "$ROOT_DIR"

TARGET="${1:-local}"
API_URL="${API_URL:-}"

case "$TARGET" in
  render)
    API_URL="${API_URL:-https://tiwhanawhana-backend.onrender.com}"
    ;;
  *)
    API_URL="${API_URL:-http://localhost:10000}"
    ;;
esac

STATE_BASE_URL="${STATE_BASE_URL:-$API_URL}"

export TARGET API_URL STATE_BASE_URL

print_step() {
  echo
  echo "=============================="
  echo "Running: $1"
  echo "=============================="
}

print_step "test_cors_auth.sh"
bash "./test_cors_auth.sh" "$TARGET" "$API_URL"

print_step "test_state_sync.sh"
bash "./test_state_sync.sh"

print_step "test_template.py"
python "./test_template.py"

print_step "test_live_tools.sh"
bash "./test_live_tools.sh"

print_step "test_pipeline_samples.sh"
bash "./test_pipeline_samples.sh"
