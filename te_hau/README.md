# Te Hau – AwaNet Automation Realm

## Purpose

Te Hau orchestrates CLI tooling, automation, and proxy layers that keep Te Pō reachable for developers and other kaitiaki. **Reason for recent changes:** document how the CLI, event routing, and manifest generation bridge the backend and frontend so we can automate context syncs without losing the wai/tikanga embedded in this layer.

## Structure
- **`app.py`**: FastAPI bridge that relays Te Ao/Kitenga requests to Te Pō and emits events onto the awa bus.
- **`cli/, core/, services/`**: CLI commands, kaitiaki orchestration helpers, request emitters, and context stores.
- **`mauri/, state.yaml, mauri/scripts/`**: Templates and compiled manifests that define agent memory for automation tasks.
- **`scripts/, start_tehau.sh`**: Boot scripts that wire Te Hau into the infrastructure and capture logs.
- **`docs/, analysis/ (root)`**: Share knowledge of proxies, automation intent, and context sync guidance with other realms.

## How to Run
- **Dev Start:**
```sh
uvicorn te_hau.app:app --reload --host 0.0.0.0 --port 8020
```

- **Tests:**
```sh
pytest
```

- **Key Env Vars:**
  - TE_HAU_MAURI_PATH
  - TE_PO_URL
  - KITENGA_PORT
  - SUPABASE_URL
  - SUPABASE_SERVICE_ROLE_KEY
  - CF_TUNNEL_ID
  - CF_TUNNEL_NAME
  - CF_TUNNEL_HOSTNAME
  - OPENAI_API_KEY

### Main Files/Folders
| Path | Purpose |
| --- | --- |
| `cli/, core/, services/` | CLI commands, orchestration helpers, awa bus emitters, OCR/proxy clients. |
| `start_tehau.sh, Dockerfile` | Launch scripts that wire Te Hau into the wider CD pipeline. |
| `mauri/, state.yaml, mauri/scripts/` | Templates and compiled manifests capturing automation memory and agent identities. |
| `scripts/, kitenga_whakairo/` | Utility scripts and carving tools used by governance kaitiaki. |
| `docs/, analysis/ (root)` | Explanation of proxies, automation intent, and context sync guidance. |

## How it Connects
- **Connects to:** Te Pō APIs, kitenga_mcp, Supabase for event persistence, Local mauri store for agent memory
- **Consumed by:** Te Ao UI, Kitenga CLI consumers, Codex/IDE assistants, Automation jobs that inject context or emit events

## Why This Structure?
- Separating CLI tooling, proxies, and mauri compilations keeps automation logic simple to audit and adjust as we restructure the awa.
- The manifest/state folders ensure every change is mirrored in the kaitiaki templates that feed other realms.
- Scripts and start_tehau.sh centralize environment loading so Te Hau can keep emitting events even when infrastructure shifts.

## Kaitiaki Notes
- After touching CLI endpoints, rerun mauri/scripts/compile_kaitiaki.py so every automation kaitiaki manifest aligns with the new intent.
- Keep /analysis/routes_summary.json and /analysis/mcp_tools_manifest.json updated with any new proxies, CLI routes, or tool loaders that Te Hau introduces.
- Use docs/context/CONTEXT.md and docs/guides/GUARDIANS.md to narrate changes so future kaitiaki understand the automation contracts.
