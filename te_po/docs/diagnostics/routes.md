# Kitenga Whiro Repo Review

**Scan time:** 2026-01-03T22:16:04.112298
**Branch:** main
**Commit:** cda6778fbee3929cfb8334a297a75cd53526bc04
**Performed by:** run_repo_review.py

## Route Catalog
### Other

- GET /
- GET /.well-known/openapi-core.json
- GET /analysis/documents/latest
- GET /analysis/sync-status
- GET /gpt_connect.yaml
- GET /heartbeat
- GET /openai_tools.json
- GET /openapi-core.json
- GET /realm.json
- POST /gpt-whisper
- POST /ocr
- POST /scribe
- POST /speak
- POST /translate

## External Context
- **Te Pō (`te_po/`)** handles FastAPI routes, assistant bridges, and vector + Supabase helpers—key envvars include none detected from .env.
- **Kitenga MCP (`kitenga_mcp/`)** exposes `/mcp/*`, aggregates tool manifests, and front-ends Render/Supabase flows with `PIPELINE_TOKEN`/`RENDER_API_KEY` guardrails.
- **Vector + Logging**: `te_po/routes` + `kitenga_mcp/app_server.py` push embeddings, AwaNet events, and logs to Supabase buckets.

## MCP Tool Manifest Highlights
- Domains captured: none yet.
- No tool manifests yet.

## Script Tool Scan
- Script scan captured 6 file(s) matching keywords: real_time, loop, event, awa, mcp, orchestrate.
- `core/awa_event_loop.py` → FastAPI: False, event-loop/async: True, functions: awa_event_loop, start_awa_event_loop
- `core/awa_gpt.py` → FastAPI: True, event-loop/async: True, functions: call_awa_bridge, gpt_reason, awa_gpt_invoke
- `core/awa_realtime.py` → FastAPI: True, event-loop/async: True, functions: awa_realtime_listener, handle_awa_event, toggle_realtime, ...
- `diagnostics/awa_mana.py` → FastAPI: False, event-loop/async: True, functions: run_diagnose, main
- `routes/awa.py` → FastAPI: True, event-loop/async: True, functions: bridge_test, awa_orchestrate, gpt_bridge
- (1 more script tool files recorded.)

## Key Environment Variables
- (none detected from .env)

## Mauri Summary
Flows stay connected: base routes + tool manifests are present, MCP/middleware checks guard bearer auth. Mauri score is 3/10 and growing.

## Notes for Agents
- `/analysis/` now holds JSON + Markdown review artifacts—MCP tool manifests should guide GPT Builder tooling.
- Follow the karakia cadence: start + finish, log to `/analysis/review_log_*.md`.

## Metadata
- Script: `analysis/run_repo_review.py`
- Versioned scan: yes

---
Author: kitenga (fallback)
