Whiro MCP Toolplane (Te Pō Only)
================================

Scope
- Whiro is a dev-only carver for Te Pō. It must not reach into Te Hau or other realms.
- Tools target existing Te Pō HTTP endpoints; no imports from `te_po.core.main` are required.
- Cultural/domain semantics are preserved (taonga, pipeline, Kitenga).

Run commands
- MCP stdio (for Continue/CLI): `./scripts/run_whiro_stdio.sh`
- Optional HTTP bridge on :6000: `./scripts/run_whiro_http.sh` (local debugging)

Boundaries
- Do not mutate production data from Whiro; it proxies existing guarded APIs.
- Respect bearer/pipeline tokens via environment (`PIPELINE_TOKEN`, `HUMAN_BEARER_KEY`).
- Keep imports limited to whiro/ modules and lightweight HTTP clients.
