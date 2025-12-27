# Te Ao – AwaNet Frontend Realm

## Purpose

Te Ao delivers the React/Vite dashboard and overview UI that surfaces OCR, translation, and state awareness for whānau and kaitiaki. **Reason for recent changes:** capture the UI’s purpose, connection points, and memory dependencies so we can automate documentation for every realm before we start moving code.

## Structure
- **`src/`**: React entrypoints, state management utilities, and UI components that talk to Te Pō and Te Hau.
- **`config/, state/`**: Static config files plus the cached te_ao_state.json that keeps the interface aligned with the backend.
- **`public/, dist/`**: Static assets and production build output for deployments.
- **`package.json, node_modules/`**: Frontend tooling and dependencies managed by Vite and Tailwind.
- **`docs/, analysis/ (root)`**: Document how the UI fits into the wider awa and record any new routes or endpoints.

## How to Run
- **Dev Start:**
```sh
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

- **Tests:**
```sh
npm run build
npm run preview
```

- **Key Env Vars:**
  - VITE_API_BASE_URL
  - VITE_TE_HAU_PROXY_URL
  - VITE_SUPABASE_URL
  - VITE_SUPABASE_ANON_KEY
  - VITE_KITENGA_PORT

### Main Files/Folders
| Path | Purpose |
| --- | --- |
| `src/` | React components, state hooks, and API utilities targeting Te Pō/Te Hau. |
| `state/te_ao_state.json` | Cached context that informs UI flows and bookmarks. |
| `config/, public/` | Theme/config presets plus static assets (icons, logos). |
| `dist/` | Production bundle produced by npm run build. |
| `docs/, analysis/ (root)` | Human-readable architecture, route summaries, and automation expectations. |

## How it Connects
- **Connects to:** Te Pō FastAPI routes, Te Hau proxies, Supabase insights, Mauri/state files that keep UI state durable
- **Consumed by:** Product teams, Kaitiaki, Automation agents relying on the UI to monitor health, translation, and pipeline status

## Why This Structure?
- The split between UI code, state snapshots, and production/dist assets keeps build tooling tidy and makes it obvious where to update the front-end when APIs evolve.
- state/ holds the enduring context that Te Ao needs so the UI can replay the awa state even if the backend is still warming up.
- Referencing docs/ and analysis/ ensures the UI is described in the same language as the other realms.

## Kaitiaki Notes
- Keep state/te_ao_state.json and mauri/state/te_ao_state.json synced whenever new UI flows or statuses are added.
- When routes used in the UI change, update /analysis/routes_summary.json and rerun /analysis/kaitiaki_context_sync.py so automations know about the new surface area.
- Use docs/context/CONTEXT.md and docs/guides/DEVELOPMENT.md to explain how the UI should be consumed by future kaitiaki dashboards.
