#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo
echo "↺ Running live tool tester (openapi payload sweep + analysis GET)..."
cd "$SCRIPT_DIR"
python3 live_tool_tester.py --skip-sync
echo "✅ Live tool tester completed."
