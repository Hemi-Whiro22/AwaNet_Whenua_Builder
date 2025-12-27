# Te Pō – AwaNet Backend Realm

## Purpose

Te Pō houses the FastAPI-driven intelligence, pipelines, and OCR services that power AwaNet. **Reason for recent changes:** clarify the backend role and surface the state, manifest, and pipeline touchpoints so our kaitiaki tooling and Codex agents can keep context fresh while we reorganise the wider awa.

## Structure
- **`app.py / main.py`**: Expose the FastAPI app that federates routes, helpers, and diagnostics.
- **`core/, services/, pipeline/`**: Encapsulate domain logic, OpenAI workflows, Supabase connectors, and automated jobs.
- **`mauri/, state/, storage/`**: Hold guarded context, carving logs, and Supabase schema/state definitions.
- **`scripts/, tests/`**: Utility helpers, dev scripts, and pytest suites that keep the backend resilient.
- **`analysis/, docs/ (root)`**: Explain architecture, manifest intent, and route summaries for humans and kaitiaki.

## How to Run
- **Dev Start:**
```sh
uvicorn te_po.main:app --reload --host 0.0.0.0 --port 8010
```

- **Tests:**
```sh
pytest
```

- **Key Env Vars:**
  - OPENAI_API_KEY
  - KITENGA_ASSISTANT_ID
  - KITENGA_VECTOR_STORE_ID
  - OPENAI_BASE_URL
  - SUPABASE_URL
  - SUPABASE_SERVICE_ROLE_KEY
  - TE_PO_STATE_BUCKET

### Main Files/Folders
| Path | Purpose |
| --- | --- |
| `core/, services/` | Business logic, assistant orchestration, OCR, vector helpers. |
| `pipeline/, migrations/` | ETL jobs, data drift detection, schema updates. |
| `state/, mauri/, storage/` | Context snapshots, carving logs, Supabase/pgvector state. |
| `scripts/, tests/` | Dev tools, export helpers, pytest suites. |
| `analysis/, docs/ (root)` | Route catalogs, sync scripts, and architecture intent. |

## How it Connects
- **Connects to:** Supabase vector tables, OpenAI APIs, kitenga_mcp tooling, mauri/state/te_po_state.json, analysis root reviews
- **Consumed by:** te_ao dashboards, te_hau CLI proxies, analysis sync jobs, external UIs needing translation/OCR

## Why This Structure?
- The split keeps API logic, memory/state snapshots, and automation tooling in well-defined folders so updates stay readable.
- Manifest and state directories keep kaitiaki context packaged for Codex and downstream syncs.
- `analysis/` + `docs/` act as the living map so the backend intent is discoverable before we move code around.

## Kaitiaki Notes
- After touching routes, tools, or manifests, rerun /analysis/kaitiaki_context_sync.py and update /analysis/routes_summary.json so the wake and memory stay aligned.
- Keep mauri/state/te_po_state.json and the Supabase schema snapshots in sync with any schema/pipeline changes.
- Document architectural shifts in docs/architecture/ and docs/context/CONTEXT.md so future kaitiaki inherit the intent.
