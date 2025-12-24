#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "[whakairo] starting nightly pipeline run"

cd "$ROOT"

echo "[whakairo] updating analysis artifacts"
python analysis/run_repo_review.py
python analysis/kaitiaki_context_sync.py

echo "[whakairo] recording carve summary"
python te_hau/kitenga_whakairo/record_carve.py \
  --title "Nightly carve" \
  --summary "Automated nightly sync of analysis/docs for Supabase + OpenAI recall." \
  --files "analysis/routes.json,analysis/routes_summary.json,analysis/mcp_tools_manifest.json" \
  --tags "automation,whakairo" \
  --mode research \
  --text "Nightly carving pipeline refreshed the analysis artifacts and latched them into Supabase/OpenAI vectors." \
  --save-vector

echo "[whakairo] syncing Supabase carver context"
python te_hau/kitenga_whakairo/sync_carver_context.py

echo "[whakairo] ingesting docs via pipeline"
python scripts/kitenga_whakairo_ingest.py --mode research

echo "[whakairo] pipeline complete"
