# Kitenga Whiro Repo Review

**Scan time:** 2025-12-23T18:24:04.682258
**Branch:** main
**Commit:** 09c2f495984862db3fdc4e81873362ddbb863b50
**Performed by:** run_repo_review.py

## Route Catalog
### Mcp

- GET /mcp/health
- GET /mcp/health
- GET /mcp/tools/list
- GET /mcp/tools/describe
- POST /mcp/tools/call
- GET /mcp/memory/ping
- GET /mcp/health
- GET /mcp/tools/list
- GET /mcp/tools/describe
- POST /mcp/tools/call

### Other

- GET /
- GET /api/status
- POST /api/ocr
- GET /api/kaitiaki
- POST /api/kaitiaki
- GET /api/events
- POST /api/events
- GET /debug/routes
- POST /awa/loop/test
- POST /awa/protocol/event
- GET /awa/memory/debug
- POST /awa/memory/search
- POST /awa/memory/add
- GET /
- GET /
- GET /
- GET /heartbeat
- GET /gpt_connect.yaml
- GET /realm.json
- GET /openapi-core.json
- GET /.well-known/openapi-core.json
- POST /ocr
- POST /translate
- POST /speak
- POST /scribe
- POST /gpt-whisper
- GET /
- POST /api/generate
- GET /api/status
- GET /status
- GET /status
- GET /status
- GET /status
- GET /status
- GET /status

## External Context
- **Te Pō (`te_po/`)** handles FastAPI routes, assistant bridges, and vector + Supabase helpers—key envvars include `OPENAI_API_KEY`, `SUPABASE_SERVICE_ROLE_KEY`.
- **Kitenga MCP (`kitenga_mcp/`)** exposes `/mcp/*`, aggregates tool manifests, and front-ends Render/Supabase flows with `PIPELINE_TOKEN`/`RENDER_API_KEY` guardrails.
- **Vector + Logging**: `te_po/routes` + `kitenga_mcp/app_server.py` push embeddings, AwaNet events, and logs to Supabase buckets.

## MCP Tool Manifest Highlights
- Domains captured: cloudflare, commands, openai, supabase, tepo.
- Top loaded tools: deploy_pages, deploy_te_ao, create_project, list_projects, get_project.

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