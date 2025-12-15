# TemplateRealm Project Structure

This is the structure generated when you create a new realm using the Realm Generator.

## Complete Directory Layout

```
TemplateRealm/                      ← Your realm name
├── te_po_proxy/                    ← Local backend (proxy to main Te Pō)
│   ├── main.py                     ← FastAPI app
│   ├── bootstrap.py                ← Initialization
│   ├── requirements.txt            ← Python dependencies
│   └── Dockerfile                  ← Container config
│
├── te_ao/                          ← Frontend (React + Vite)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── public/
│   └── Dockerfile
│
├── te_hau/                         ← CLI / Command orchestration
│   ├── __init__.py
│   ├── cli.py                      ← Command-line interface
│   └── commands/                   ← Command modules
│
├── mauri/                          ← State & Knowledge layer
│   ├── kaitiaki_templates/
│   │   └── [realm_kaitiaki].yaml   ← Kaitiaki definition (YAML source)
│   ├── state/
│   │   └── realm_state.json        ← Shared realm state
│   ├── documents/
│   │   └── md/                     ← Markdown documentation
│   └── archived/                   ← Legacy configurations
│
├── kaitiaki/                       ← Kaitiaki agents for this realm
│   └── [realm_kaitiaki]/
│       ├── [name]_manifest.json    ← Compiled manifest (generated)
│       ├── [name]_state.json       ← Agent state
│       ├── [name]_carving_log.jsonl ← Activity log
│       └── docs/
│           ├── README.md           ← Kaitiaki overview
│           └── CONTEXT.md          ← Development context
│
├── config/                         ← Realm configuration
│   ├── realm.json                  ← Realm metadata
│   ├── proxy.toml                  ← Cloudflare proxy config
│   └── tools.json                  ← Available tools spec
│
├── .github/                        ← GitHub workflows
│   └── workflows/
│       ├── cloudflare-pages.yml    ← Frontend deployment
│       └── health-check.yml        ← Status monitoring
│
├── scripts/                        ← Utility scripts
│   ├── new_realm.sh                ← Legacy realm setup
│   └── deploy.sh                   ← Deployment helper
│
├── docs/                           ← Documentation
│   ├── README.md
│   ├── setup.md                    ← Installation guide
│   └── deployment.md               ← Deployment guide
│
├── .env                            ← Configuration (local)
├── .env.template                   ← Configuration template
├── Dockerfile                      ← Main container (if deployed as one)
├── docker-compose.yaml             ← Local development setup
├── .gitignore
└── README.md                       ← Project overview
```

## Key Directories Explained

### `te_po_proxy/` — Local Backend
- **Purpose:** Proxy to the main Te Pō backend
- **Technology:** FastAPI (Python)
- **Runs on:** `localhost:8000` (development)
- **Routes:**
  - `/status` — Health check
  - `/chat` — Chat/processing endpoints
  - `/vector` — Vector store operations
- **Connects to:** Main Te Pō backend (configured in `.env`)

### `te_ao/` — Frontend
- **Purpose:** User-facing web interface
- **Technology:** React + Vite
- **Runs on:** `localhost:5173` (development)
- **Serves:** `TemplateRealm UI`
- **Communicates with:** `te_po_proxy` (local) and main Te Pō (when needed)

### `te_hau/` — CLI Layer
- **Purpose:** Command orchestration and automation
- **Technology:** Python Click CLI
- **Commands:**
  - `tehaus status` — Show realm status
  - `tehaus kaitiaki spawn` — Initialize Kaitiaki
  - `tehaus kaitiaki list` — List available agents

### `mauri/` — State & Knowledge
- **Purpose:** Realm state, knowledge base, and history
- **Subdirectories:**
  - `kaitiaki_templates/` — YAML agent definitions (source of truth)
  - `state/` — Shared realm state
  - `documents/` — Knowledge base
  - `archived/` — Legacy configurations

### `kaitiaki/` — Agents
- **Purpose:** Runtime Kaitiaki agents for this realm
- **Contents:**
  - `[realm_kaitiaki]/[name]_manifest.json` — Compiled manifest (generated from YAML)
  - `[realm_kaitiaki]/docs/` — Agent documentation and context

### `config/` — Configuration
- **Purpose:** Realm-specific configuration
- **Files:**
  - `realm.json` — Realm metadata (name, description, etc.)
  - `proxy.toml` — Cloudflare Tunnel configuration
  - `tools.json` — Tool specifications available in this realm

## te_ao Frontend Structure (Level 3, dist excluded)

```
te_ao
├── config
│   ├── README.md
│   └── tools.json
├── Dockerfile
├── index.html
├── __init__.py
├── node_modules
├── package.json
├── package-lock.json
├── postcss.config.cjs
├── public
│   ├── favicon.ico
│   └── koru.svg
├── README.md
├── src
│   ├── App.jsx
│   ├── assets
│   │   ├── AwaNet_Koru.svg
│   │   ├── favicon.ico
│   │   ├── koru_spiral.svg
│   │   ├── koru.svg
│   │   ├── stone-koru-lv9Nht-r.png
│   │   └── stone-koru.png
│   ├── components
│   │   ├── chat
│   │   └── ui
│   ├── data
│   │   └── public_schema_te_puna.json
│   ├── hooks
│   │   ├── useApi.js
│   │   ├── useAwa.ts
│   │   ├── useEvents.ts
│   │   └── useIwiPortal.js
│   ├── index.css
│   ├── layouts
│   │   └── KitengaShell.jsx
│   ├── main.jsx
│   ├── mauri.js
│   └── panels
│       ├── AdminPanel.jsx
│       ├── ChatPanel.jsx
│       ├── CulturalScanPanel.jsx
│       ├── IwiPortalPanel.jsx
│       ├── MemoryPanel.jsx
│       ├── OCRPanel.jsx
│       ├── PronunciationPanel.jsx
│       ├── RealmHealthPanel.tsx
│       ├── ReoPanel.jsx
│       ├── ResearchPanel.tsx
│       ├── SummaryPanel.jsx
│       ├── TranslatePanel.jsx
│       ├── TranslationPanel.jsx
│       └── VectorSearchPanel.jsx
├── start_frontend.sh
├── state
│   └── state.yaml
├── tailwind.config.cjs
└── vite.config.js
```

### Template Notes
- **config/** — Keep `tools.json` and README as the contract for local tooling. For new projects, drop environment-specific instructions here so each mini Te Pō proxy knows how to register tools.
- **Dockerfile / start_frontend.sh** — Ready-to-clone deployment + dev launch scripts. Parameterize the backend URL via build args so future spin-ups can proxy to different Te Pō instances without editing source.
- **public/** — Shared branding assets (koru, favicon). Swap here for realm-specific skins while leaving React pipeline untouched.
- **src/assets & layouts/** — Centralize visual identity (koru stones, `KitengaShell`). Ideal place to inject context-aware theming toggles.
- **src/hooks/useApi.js** — Already computes base URL + token fallback. Extract this into a reusable hook package so each mini frontend automatically respects env overrides.
- **src/panels/** — Primary UX modules. For future spin-ups, consider generating these from a manifest (e.g., `panels.json`) so you can enable/disable features per client realm.
- **state/state.yaml** — Handy for persisting lightweight UI config; extend for context-aware defaults (e.g., locale, allowed taonga scopes).

_Note: `dist/` was omitted intentionally to keep the template focused on source + config._

## te_po Backend Structure (Level 2 snapshot)

```
te_po
├── assistants/              # OpenAI assistant bootstrap scripts
├── core/                    # FastAPI entrypoints, env loader, backend config
├── kitenga/                 # MCP server, manifest, tools, logs/state
├── models/                  # Pydantic schemas (auth, reo, memory, vector, etc.)
├── pipeline/                # Chunker, embedder, OCR, research jobs/workers
├── routes/                  # FastAPI routers (status, vector, reo, chat, etc.)
├── scripts/                 # CLI helpers (supabase sync, register tools, smoke tests)
├── services/                # Business logic: memory, OCR, vector, supabase logging
├── storage/                 # Raw/clean files, chunks, supabase exports, test fixtures
├── utils/                   # Shared helpers (env, middleware, openai client, safety)
├── openai_assistants.json / openai_tools.json
├── README.md / render.yaml / run_tests.sh
└── main.py / mauri.py / stealth_ocr.py / kitenga bootstrap, etc.
```

For a mini deployment, mirror only the subfolders you need (e.g., `core`, `routes`, `kitenga`, `services`), but keep the layout so imports stay compatible with the primary Te Pō repo.

## Recommended Template Additions for Mini Te Pō Sync

To keep each mini realm aligned with the primary Te Pō stack, scaffold these extra pieces alongside `te_ao/`:

1. **`project_template/mini_te_po/` (FastAPI proxy)**
   - `main.py` exposing only the routes needed for the satellite realm, mounting shared routers from `te_po`.
   - `requirements.txt` pinned to match the main project plus any realm-specific deps.
   - `bootstrap.py` to register assistant/vector metadata and point to the canonical Te Pō services.

2. **`project_template/mauri/` (minimal state)**
   - `realm_lock.json` capturing allowed korowai + assistant IDs.
   - `state/` directory with lightweight manifests (`den_manifest.json`, `mauri_state.json`) for context-aware defaults.
   - `config/mauri.env` for secrets that stay with the mini realm.

3. **Environment & tooling config**
   - Root `project_template/.env.template` including Python version, Node version, UTF-8 + `mi_NZ` locale defaults, and shared bearer tokens.
   - `.devcontainer/` with `devcontainer.json`, `Dockerfile`, and `cloudflare_start.sh` so Codespaces/containers match the main project.
   - `docker-compose.yml` (or updated Dockerfile) that runs the mini backend plus the frontend proxy, wiring ports 8000/5173 → primary Te Pō.
   - `project_template/scripts/bootstrap.sh` to spin everything up (install deps, run migrations, start tunnels).
   - `project_template/context/context_seed.json` generated per realm and `scripts/seed_context.py` to push to Supabase.

4. **Shared config artifacts**
   - `config/realm.json` describing which panels/routes to enable.
   - `config/proxy.toml` for reverse-proxy rules if you need to bounce traffic through Cloudflare or Warp routing.
   - `template.config.json` enumerating placeholders and secrets the CLI must fill.
   - `archetypes.json` listing archetype presets the CLI can apply.

Adding these ensures every spin-up project ships with the same Python/Node toolchain, locale, security expectations (bearer keys, UTF-8 enforcement), and a miniature Mauri state so it can authenticate back into the mothership safely. Let me know if you want this scaffold generated automatically.***

### Security Considerations
- This documentation doesn’t expose secrets; `te_ao` still talks to Te Pō exclusively via the authenticated HTTP API guarded by `BearerAuthMiddleware`, so duplicating the structure poses no extra risk.
- Each mini realm should generate its own bearer key + `.env`. Keep only a placeholder in the template (`HUMAN_BEARER_KEY=`); at spin-up time mint a unique token, register it in the primary Te Pō `.env`/secrets store, and hand it to that realm. If the satellite is compromised, you can revoke its key without touching the others.
- Keep Mauri realm locks + manifests versioned to prevent a satellite build from escalating capabilities beyond what the main Te Pō permits.***

### Automation & Deployment Flow
To make the “clone → rename → deploy” loop painless:

1. **Bootstrap script (`project_template/scripts/bootstrap.sh`)**
   - Installs Python/Node deps, copies `project_template/.env.template` → `.env`, prompts for the realm’s bearer token + Cloudflare tunnel IDs, and writes them into the correct files.
   - Calls `project_template/mini_te_po/bootstrap.py` to register assistant/vector IDs with the mothership.

2. **Git helpers**
   - `project_template/scripts/new_realm.sh <RealmName>`: renames folders, updates manifests, initializes a new Git repo if desired.
   - Optional GitHub Actions workflow templates (`.github/workflows/cloudflare-pages.yml`, `health-check.yml`) so new repos deploy automatically to Cloudflare Pages and ping `/status/full`.

3. **CI jobs**
   - Lint/test both `te_ao` and `project_template/mini_te_po`.
   - Run a `health-check` job that curls the primary Te Pō `/status/full` using the realm’s bearer token before deployment to confirm connectivity.

4. **Cloudflare integration**
   - Provide environment-variable manifests listing the required secrets (bearer token, PIPELINE_TOKEN fallback, Supabase keys).
   - Ship `cloudflare_start.sh` so local dev containers mimic the production tunnel.

With these scripts in the template repo, a new realm can: clone → run `project_template/scripts/new_realm.sh` → commit/push → watch CI deploy to Cloudflare Pages + Render while automatically wiring bearer tokens back to your central Te Pō backend.***

## Minimal Working Stubs & Routing Overview

To make this document IDE-ready, include the following placeholder files/modules with the indicated wiring:

### project_template/mini_te_po/
- `main.py`
  ```python
  # FastAPI proxy exposing a subset of te_po routes
  from fastapi import FastAPI
  from te_po.core.env_loader import load_env
  from te_po.routes import status, chat, vector

  load_env()
  app = FastAPI(title="Mini Te Pō Proxy")
  app.include_router(status.router)
  app.include_router(chat.router, prefix="/chat")
  app.include_router(vector.router, prefix="/vector")
  ```
- `bootstrap.py`
  ```python
  from te_po.kitenga.bootstrap import bootstrap as kitenga_bootstrap

  def bootstrap():
      kitenga_bootstrap()

  if __name__ == "__main__":
      bootstrap()
  ```
- `requirements.txt`
  ```
  -r ../requirements.txt
  uvicorn
  fastapi
  ```

### te_ao/src/hooks/useApi.js (already in repo)
- Ensure it points to `import.meta.env.VITE_API_URL || window.origin:8000` so the frontend automatically hits the mini backend which proxies to the main Te Pō instance.

### project_template/scripts/bootstrap.sh
```
#!/usr/bin/env bash
set -euo pipefail

cp project_template/.env.template .env
read -p "Enter bearer token for this realm: " BEARER
echo "HUMAN_BEARER_KEY=${BEARER}" >> .env

pip install -r requirements.txt
npm install --prefix te_ao
python project_template/mini_te_po/bootstrap.py
```

### routing summary
- Frontend → `VITE_API_URL` (default `http://localhost:8000`).
- `project_template/mini_te_po/main.py` runs on port 8000, includes necessary routers, and forwards to the main Te Pō services (shared imports ensure parity).
- Cloudflare Pages deploys `te_ao` (`npm run build` → `dist/`); deploy the mini backend wherever you prefer when ready.

These stubs give IDEs enough context to generate files and let developers fill in the specifics per realm.***

## Master Stub File Checklist / System Prompt
Use this list as the canonical “source of truth” when bootstrapping a new mini realm:

1. **Environment**
   - `project_template/.env.template` with placeholders for `HUMAN_BEARER_KEY`, `PIPELINE_TOKEN`, Supabase creds, OpenAI keys, locale (`LANG=mi_NZ.UTF-8`), Python/Node versions.
   - `.devcontainer/devcontainer.json` + `.devcontainer/Dockerfile` ensuring Ubuntu base, Python 3.12, Node 20, UTF-8 locale, and scripts to run `cloudflare_start.sh`.

2. **Frontend (`te_ao/`)**
   - `project_template/STRUCTURE.md` (this file).
   - `te_ao/src/hooks/useApi.js` (already present) referencing `VITE_API_URL`.
   - `te_ao/src/panels/README.md` explaining how to enable/disable panels via `config/realm.json`.
   - `project_template/config/realm.json` as the source for panel flags the CLI will update.

3. **Mini backend (`project_template/mini_te_po/`)**
   - `project_template/mini_te_po/main.py` stub above.
   - `project_template/mini_te_po/bootstrap.py` stub above.
   - `project_template/mini_te_po/requirements.txt` referencing `../requirements.txt`.

4. **Mauri**
   - `project_template/mauri/realm_lock.json`
     ```json
     {
       "realm": "TemplateRealm",
       "assistant_id": "asst_TemplateRealm",
       "vector_store_id": "vs_template",
       "allowed_panels": ["chat", "vector", "ocr"]
     }
     ```
   - `project_template/mauri/state/den_manifest.json` minimal manifest referencing the assistant.

5. **Scripts**
   - `project_template/scripts/bootstrap.sh` (above).
   - `project_template/scripts/new_realm.sh`
     ```bash
     #!/usr/bin/env bash
     set -euo pipefail
     REALM="$1"
     BEARER=$(openssl rand -hex 32)
     find . -type f -not -path ".git/*" -print0 | xargs -0 sed -i "s/TemplateRealm/${REALM}/g"
     sed -i "s/HUMAN_BEARER_KEY=/HUMAN_BEARER_KEY=${BEARER}/" .env
     echo "Generated bearer token: ${BEARER}"
     git init && git add . && git commit -m "Initial ${REALM} realm"
     ```
   - `project_template/scripts/health_check.sh`:
     ```bash
     curl -sf -H "Authorization: Bearer ${HUMAN_BEARER_KEY}" "${VITE_API_URL}/status/full"
     ```

6. **Master prompt**
   - Include a `project_template/docs/MASTER_PROMPT.md` with instructions for future coders/IDEs:
     ```
     You are bootstrapping a mini Te Pō realm. Always:
     1. Copy `project_template/.env.template` → `.env` and set a unique HUMAN_BEARER_KEY.
     2. Run `project_template/scripts/bootstrap.sh` to install deps and register the realm.
     3. Use `project_template/STRUCTURE.md` to understand folder relationships.
     4. Deploy frontend via Cloudflare Pages, backend via Render.
     5. Confirm connectivity by running `project_template/scripts/health_check.sh`.
     ```

Populate these stubs once per template repository so anyone (human or IDE agent) can spin up a new realm without further clarification.***

### Secrets Manifest
Create `project_template/docs/secrets.md` detailing where each secret lives:

| Secret                | Local `.env` | Cloudflare Pages | Render | Source of Truth          |
|-----------------------|--------------|------------------|--------|--------------------------|
| `HUMAN_BEARER_KEY`    | ✅            | ✅ (Frontend env) | ✅      | Generated via `new_realm.sh`; register in main Te Pō backend |
| `PIPELINE_TOKEN`      | ✅            | ✅                | ✅      | Main Te Pō `.env`        |
| `SUPABASE_URL/KEYS`   | ✅            | ✅                | ✅      | Shared vault (Supabase)  |
| `OPENAI_API_KEY`      | ✅            | ❌ (front)        | ✅      | Shared vault             |
| `CF_TUNNEL_ID/NAME`   | ✅            | ✅ (if Pages needs) | ✅   | Cloudflare dashboard     |

This allows automation to prompt for only what’s missing and ensures every deployment target gets the right secrets without guesswork.***
