# Kitenga Whiro Repo Review

**Scan time:** 2025-12-24T01:03:47.987840
**Branch:** main
**Commit:** 57f85af51dc70162b2c81fd2fa8e138e0a1c19a9
**Performed by:** run_repo_review.py

## Route Catalog
### Other

- GET /
- GET /.well-known/openapi-core.json
- GET /analysis/documents/latest
- GET /analysis/sync-status
- GET /api/events
- GET /api/kaitiaki
- GET /api/status
- GET /awa/memory/debug
- GET /debug/routes
- GET /gpt_connect.yaml
- GET /health
- GET /heartbeat
- GET /memory/ping
- GET /openai_tools.json
- GET /openapi-core.json
- GET /realm.json
- GET /status
- GET /tools/describe
- GET /tools/list
- POST /api/events
- POST /api/generate
- POST /api/kaitiaki
- POST /api/ocr
- POST /awa/loop/test
- POST /awa/memory/add
- POST /awa/memory/search
- POST /awa/protocol/event
- POST /gpt-whisper
- POST /ocr
- POST /scribe
- POST /speak
- POST /tools/call
- POST /translate

## External Context
- **Te Pō (`te_po/`)** handles FastAPI routes, assistant bridges, and vector + Supabase helpers—key envvars include `OPENAI_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`.
- **Kitenga MCP (`kitenga_mcp/`)** exposes `/mcp/*`, aggregates tool manifests, and front-ends Render/Supabase flows with `PIPELINE_TOKEN`/`RENDER_API_KEY` guardrails.
- **Vector + Logging**: `te_po/routes` + `kitenga_mcp/app_server.py` push embeddings, AwaNet events, and logs to Supabase buckets.

## MCP Tool Manifest Highlights
- Domains captured: cloudflare, commands, openai, supabase, tepo.
- Top loaded tools: deploy_pages, deploy_te_ao, create_project, list_projects, get_project.

## Script Tool Scan
- Script scan captured 13 file(s) matching keywords: real_time, loop, event, awa, mcp, orchestrate.
- `kitenga_mcp/fastmcp_config.py` → FastAPI: False, event-loop/async: False, functions: get_service_config, get_all_services, get_server_config
- `mauri/archived/shared/awa_bus/awa_events.py` → FastAPI: False, event-loop/async: False, functions: n/a
- `scripts/tests/test_mcp_import.py` → FastAPI: False, event-loop/async: False, functions: n/a
- `te_hau/cli/awanui.py` → FastAPI: False, event-loop/async: False, functions: cli, main
- `te_hau/services/awa_bus.py` → FastAPI: False, event-loop/async: False, functions: emit, latest
- (8 more script tool files recorded.)

## Key Environment Variables
- `OPENAI_API_KEY`
- `KITENGA_ASSISTANT_ID`
- `KITENGA_VECTOR_STORE_ID`
- `PIPELINE_TOKEN`
- `HUMAN_BEARER_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`

## Mauri Summary
Flows stay connected: base routes + tool manifests are present, MCP/middleware checks guard bearer auth. Mauri score is 9/10 and growing.

## Notes for Agents
- `/analysis/` now holds JSON + Markdown review artifacts—MCP tool manifests should guide GPT Builder tooling.
- Follow the karakia cadence: start + finish, log to `/analysis/review_log_*.md`.

## Metadata
- Script: `analysis/run_repo_review.py`
- Versioned scan: yes