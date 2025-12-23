#!/usr/bin/env bash
# Author: awa developer (Kitenga Whiro [Adrian Hemi])
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo
echo "↺ Running live tool tester (openapi payload sweep + analysis GET)..."
cd "$REPO_ROOT"
python3 scripts/live_tool_tester.py --skip-sync
echo "✅ Live tool tester completed."
