#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo
echo "↺ Generating pipeline samples and running orchestrator suite..."
cd "$SCRIPT_DIR"
python3 pipeline_sample_runner.py
echo "✅ Pipeline samples executed."
