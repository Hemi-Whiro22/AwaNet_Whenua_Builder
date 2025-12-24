# Whakairo (Carving Context)

This folder holds Codex/Kaitiaki carving context and helpers. Content here is **non-taonga** by default; keep taonga/private details out of these files.

Files:
- `whakairo_manifest.json` – quick pointers to env, tables, endpoints, modes.
- `record_carve.py` – helper to append a carve summary to `mauri/state/carver_log.jsonl` and, if configured, to Supabase `carver_context_memory` (mode defaults to `research`).
- `mcp/manifest.yaml` – MCP manifest for the Whakairo Codex agent (Supabase schema/SQL inspection); served by `te_hau/cli/start_whakairo.py`.

Usage (record a carve):
```bash
python te_hau/whakairo/record_carve.py --title "Short title" --summary "What changed" --files "file1,file2" --tags "carve,api" --mode research
```

Notes:
- Keep taonga content out of this log; if you must note taonga work, set `--mode taonga` and keep summary high-level.
- Supabase insert is best-effort and uses the existing env keys in `te_po/core/.env`.

Nightly pipeline
--------------

The helper script `scripts/run_whakairo_pipeline.sh` runs the analysis export, records a carve, syncs Supabase state, and ingests the latest docs into the carving pipeline (Supabase + OpenAI vectors). Run it manually as needed or schedule it nightly:

```bash
scripts/run_whakairo_pipeline.sh

# or run via crontab
0 1 * * * cd /home/hemi-whiro/Titiraukawa/The_Awa_Network && ./scripts/run_whakairo_pipeline.sh >> /tmp/whakairo_pipeline.log 2>&1
```

The ingestion step targets `analysis`, `docs`, and `te_hau` directories by default; update `scripts/kitenga_whakairo_ingest.py` if you want additional sources (web search outputs, custom docs, etc.).

MCP usage:
```bash
python -m te_hau.cli.start_whakairo
# or
mcp serve --manifest te_hau/whakairo_codex/mcp/manifest.yaml
```
