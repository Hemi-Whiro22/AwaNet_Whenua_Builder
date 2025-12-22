#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(dirname "$0")"
cd "$ROOT_DIR"

print_step() {
  echo
  echo "=============================="
  echo "Running: $1"
  echo "=============================="
}

print_step "test_cors_auth.sh"
bash "$ROOT_DIR/test_cors_auth.sh"

print_step "test_state_sync.sh"
bash "$ROOT_DIR/test_state_sync.sh"

print_step "test_template.py"
python "$ROOT_DIR/test_template.py"
