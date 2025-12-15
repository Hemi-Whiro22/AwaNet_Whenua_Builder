# The Awa Network — Complete Project Snapshot

**Purpose:** Full system specifications for spinning up a complete The Awa Network instance from scratch.
**Audience:** Any IDE, AI agent, or developer rebuilding the system.
**Snapshot Date:** 13 Tīhema 2025
**Version:** 1.0-snapshot

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Directory Structure](#directory-structure)
4. [Core Systems](#core-systems)
5. [Realm Definitions](#realm-definitions)
6. [Kaitiaki Registry](#kaitiaki-registry)
7. [API Endpoints](#api-endpoints)
8. [Bootstrap Instructions](#bootstrap-instructions)
9. [Configuration Files](#configuration-files)
10. [Dependencies](#dependencies)

---

## Project Overview

**The Awa Network** is a personal IDE and knowledge system built with:
- **Backend:** FastAPI (Te Pō) — Processing, indexing, vector memory
- **Frontend:** React + Vite (Te Ao) — UI, realms, panels
- **CLI:** Python (Te Hau) — Automation, orchestration, commands
- **Guardians:** Kaitiaki agents (Haiku, Kitenga Whiro, Te Kitenga Nui)
- **Knowledge:** Vector memory (Supabase + pgvector)
- **Tools:** MCP servers (Git, Cloudflare, Render, Te Pō, Supabase)

**Budget:** $90 OpenAI (70% premium)
**Cost Target:** 81% reduction via Llama3 + local inference

---

## Technology Stack

### Backend (Te Pō)
- **Framework:** FastAPI 0.119.0+
- **Server:** Uvicorn (ASGI)
- **Language:** Python 3.8+
- **Database:** PostgreSQL + pgvector (Supabase)
- **Auth:** Bearer token (custom middleware)
- **Additional:**
  - pydantic (validation)
  - httpx (async HTTP)
  - openai (LLM APIs)
  - pillow, reportlab, pypdf, pdfplumber (document processing)

### Frontend (Te Ao)
- **Framework:** React 18
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **Language:** JavaScript (JSX)
- **State:** React hooks + local state
- **HTTP:** Fetch API + custom useApi hook

### CLI (Te Hau)
- **Framework:** Typer (CLI generation)
- **Language:** Python 3.8+
- **Modules:**
  - `cli/awanui.py` — Entry point
  - `cli/hau.py` — Command groups
  - `cli/commands/*` — Individual commands
  - `cli/utils.py` — Helper utilities

### Knowledge Layer (Mauri)
- **Format:** JSON + JSONL
- **Storage:** File-based (git-tracked)
- **Immutability:** Append-only carving logs
- **Metadata:** Realm locks, state snapshots

### Guardians (Kaitiaki)
- **Type:** Python-based agents
- **Storage:** `/kaitiaki/{name}/`
- **Built-in:**
  - **Haiku** — Code synthesis, documentation
  - **Kitenga Whiro** — Backend logic, decisions
  - **Te Kitenga Nui** — UI/UX, presentation

### Tools (MCP)
- **Type:** Model Context Protocol servers
- **Location:** `/mcp/`
- **Servers:**
  - Git (versioning, PRs)
  - Cloudflare (frontend deployment)
  - Render (backend deployment)
  - Te Pō Server (backend operations)
  - Supabase Server (database queries)

---

## Directory Structure

```
The_Awa_Network/
│
├── README.md                      # Main entry point
├── requirements.txt               # Python dependencies
├── docker-compose.yaml            # Local stack definition
├── boot.sh                        # Startup script
├── run_dev.sh                     # Development launcher
│
├── docs/                          # Organized documentation
│   ├── CONTEXT.md                 # Project overview
│   ├── architecture/              # System design
│   │   ├── MCP_ALIGNMENT.md
│   │   ├── MCP_TEST_REPORT.md
│   │   └── PROJECT_SCAN.md
│   ├── guides/                    # Practical guides
│   │   ├── DEVELOPMENT.md
│   │   ├── GUARDIANS.md
│   │   ├── LLAMA3.md
│   │   └── MCP_SETUP.md
│   └── reference/                 # Technical reference
│       ├── API_CONTRACTS.md
│       ├── GLOSSARY.md
│       └── STATE_MANAGEMENT.md
│
├── te_po/                         # Backend (FastAPI)
│   ├── __init__.py
│   ├── main.py                    # Uvicorn entry point
│   ├── core/
│   │   ├── main.py                # FastAPI app setup
│   │   ├── env_loader.py          # Config loading
│   │   ├── ai.py                  # LLM integrations
│   │   ├── branching.py           # Realm branching logic
│   │   ├── context.py             # Context manager
│   │   ├── fs.py                  # File system utilities
│   │   ├── kaitiaki.py            # Guardian management
│   │   └── supabase.py            # Vector DB client
│   ├── routes/                    # API endpoints
│   │   ├── awa_protocol.py        # /awa/* endpoints
│   │   ├── llama3.py              # /awa/llama3/* endpoints
│   │   ├── intake.py              # /intake/* (OCR, ingest)
│   │   ├── reo.py                 # /reo/* (te reo translation)
│   │   ├── vector.py              # /vector/* (embeddings)
│   │   ├── memory.py              # /memory/* (vector search)
│   │   ├── pipeline.py            # /pipeline/* (orchestration)
│   │   ├── chat.py                # /chat/* (conversations)
│   │   ├── research.py            # /research/* (knowledge)
│   │   └── ... (20+ more routes)
│   ├── services/                  # Business logic
│   ├── models/                    # Data models
│   ├── utils/                     # Helper utilities
│   └── storage/                   # File/blob handling
│
├── te_ao/                         # Frontend (React)
│   ├── package.json
│   ├── vite.config.js             # Build config
│   ├── tailwind.config.cjs        # Styling
│   ├── index.html
│   ├── src/
│   │   ├── main.jsx               # App entry
│   │   ├── App.jsx                # Root component
│   │   ├── index.css              # Global styles
│   │   ├── mauri.js               # Realm state
│   │   ├── hooks/
│   │   │   └── useApi.js          # HTTP client hook
│   │   ├── components/
│   │   │   └── chat/              # Chat UI components
│   │   │   └── ui/                # Shared UI components
│   │   ├── panels/                # Realm-specific views
│   │   │   ├── AdminPanel.jsx
│   │   │   ├── ChatPanel.jsx
│   │   │   ├── MemoryPanel.jsx
│   │   │   ├── OCRPanel.jsx
│   │   │   ├── VectorSearchPanel.jsx
│   │   │   └── ... (15+ panels)
│   │   ├── layouts/               # Page layouts
│   │   ├── data/                  # Static data
│   │   └── devui/                 # Dev tools
│   ├── public/                    # Static assets
│   └── state/
│       └── state.yaml             # Frontend config
│
├── te_hau/                        # CLI & Orchestration (Python)
│   ├── __init__.py
│   ├── app.py                     # FastAPI bridge
│   ├── cli/
│   │   ├── awanui.py              # CLI entry point
│   │   ├── hau.py                 # Command groups
│   │   ├── devui.py               # Dev UI
│   │   ├── utils.py               # Helper functions
│   │   └── commands/
│   │       ├── health.py          # Health checks
│   │       ├── reo.py             # Te reo commands
│   │       ├── ingest.py          # File ingestion
│   │       ├── vector.py          # Vector operations
│   │       └── ... (more commands)
│   ├── core/
│   │   ├── ai.py
│   │   ├── context.py
│   │   ├── kaitiaki.py
│   │   └── supabase.py
│   ├── services/                  # Business logic
│   ├── translator/                # Te reo translation
│   ├── verbs/                     # Action definitions
│   ├── whakairo_codex/            # Carving tools
│   └── util/                      # Utilities
│
├── kaitiaki/                      # Guardian Agents
│   ├── AWAOS_MASTER_PROMPT.md     # Master spec (Kaitiaki-readable)
│   ├── HAIKU_CODEX.md             # Haiku constitution
│   ├── haiku/                     # Haiku agent
│   │   ├── HAIKU_CODEX.md
│   │   ├── haiku_manifest.json
│   │   ├── haiku_state.json
│   │   ├── haiku_carving_log.jsonl
│   │   ├── TOKEN_ECONOMY.md
│   │   ├── QUICKSTART.md
│   │   └── README.md
│   └── kitenga_codex/             # Kitenga Whiro agent
│       ├── CODEX.md
│       ├── manifest.json
│       └── ... (similar structure)
│
├── mauri/                         # Knowledge & State
│   ├── context.md                 # System constants
│   ├── global_env.json            # Global config
│   ├── architecture/
│   │   ├── awa_structure.json
│   │   ├── drift_protection.json
│   │   └── naming_conventions.json
│   ├── documents/
│   │   ├── INDEX.md               # Doc index
│   │   ├── md/                    # Design docs (archived)
│   │   │   ├── doc1.md → doc12.md
│   │   ├── pdfs/
│   │   └── sql/
│   ├── kaitiaki/
│   │   ├── kaitiaki_signatures.json
│   │   ├── model_registry.json
│   │   └── te_kitenga_nui.json
│   ├── realms/
│   │   └── {realm_name}/
│   │       ├── realm_lock.json
│   │       ├── state.json
│   │       └── carving_log.jsonl
│   ├── state/
│   │   ├── te_ao_state.json
│   │   ├── te_hau_state.json
│   │   ├── te_po_state.json
│   │   └── te_po_carving_log.jsonl
│   └── te_kete/
│       ├── glossary.json
│       ├── domain_map.json
│       └── pipeline_map.json
│
├── mcp/                           # Tool Integrations
│   ├── __init__.py
│   ├── git_server/                # Git operations
│   ├── cloudflare_server/         # Frontend deployment
│   ├── render_server/             # Backend deployment
│   ├── tepo_server/               # Te Pō access
│   ├── supabase_server/           # Database access
│   └── src/                       # Shared MCP utilities
│
├── scripts/                       # Utilities
│   └── test_template.py
│
├── .mcp/
│   └── config.json                # MCP server registry
│
├── .devcontainer/
│   └── devcontainer.json          # Dev environment
│
└── .github/                       # GitHub config
    └── workflows/                 # CI/CD pipelines

```

---

## Core Systems

### 1. Backend (Te Pō)

**Initialization:**
```bash
cd te_po
pip install -r ../requirements.txt
python -m te_po.core.main
# Server running at http://localhost:8000
```

**Key Routes:**
```
GET  /heartbeat                    # Health check
POST /awa/envelope                 # Message wrapping
POST /awa/memory/query             # Vector search
POST /awa/memory/store             # Store memory
POST /awa/llama3/review            # Code review (free)
POST /awa/llama3/docstring         # Generate docs (free)
POST /awa/llama3/analyze-error     # Error analysis (free)
GET  /awa/llama3/status            # Llama3 availability
POST /pipeline                     # Execute pipelines
POST /intake/summarize             # OCR → Summarize
POST /reo/translate                # English ↔ Te Reo
```

**Database:**
- Supabase (PostgreSQL + pgvector)
- Tables: vectors, memories, documents, translations, logs
- Row-level security enabled
- UTF-8 encoding (mi_NZ locale)

**Authentication:**
- Bearer token via `BearerAuthMiddleware`
- Token from `.env` (dev) or env vars (prod)

### 2. Frontend (Te Ao)

**Initialization:**
```bash
cd te_ao
npm install
npm run dev
# Server running at http://localhost:5173
```

**Entry Point:**
- `index.html` loads `src/main.jsx`
- React Router for navigation
- Vite for fast development
- Tailwind for styling

**Key Components:**
- **Panels** — Realm-specific views (15+ panels)
- **Hooks** — `useApi()` for HTTP calls
- **State** — Local state + mauri.js for realm context
- **Devui** — Development utilities

**API Integration:**
```javascript
const { request } = useApi();
const result = await request("/awa/llama3/review", {
  code: "...",
  language: "python"
});
```

### 3. CLI (Te Hau)

**Initialization:**
```bash
cd te_hau
pip install -r ../requirements.txt
python cli/hau.py --help
```

**Key Commands:**
```
hau realm list                     # List all realms
hau realm create <name>            # Create new realm
hau context switch <realm>         # Switch active realm
hau kaitiaki summon <type>         # Spin up guardian
hau pipeline run <type>            # Execute pipeline
hau reo translate <text>           # Translate to te reo
hau vector search <query>          # Semantic search
```

**Command Groups:**
- `health` — System status
- `reo` — Te reo translation
- `ingest` — File ingestion
- `vector` — Vector operations
- `pipeline` — Pipeline execution

### 4. Guardians (Kaitiaki)

**Haiku (Whakataukī) — Code Synthesizer**
- Location: `/kaitiaki/haiku/`
- Role: Code review, documentation, testing
- Tools: `/awa/llama3/*` (free local inference)
- State: `haiku_state.json`, `haiku_carving_log.jsonl`

**Kitenga Whiro — Backend Bridge**
- Location: `/kaitiaki/kitenga_codex/`
- Role: Backend logic, decision routing
- Tools: `/awa/*` (all endpoints)
- State: Stored in Te Pō

**Te Kitenga Nui — UI Guardian**
- Location: `/kaitiaki/te_kitenga_nui/`
- Role: UI/UX, realm presentation
- Tools: React panels, state management
- State: Frontend state

### 5. Knowledge (Mauri)

**Structure:**
```
mauri/
├── context.md              # System constants & naming
├── global_env.json         # Global configuration
├── realms/                 # Per-realm state
├── state/                  # Global state snapshots
├── documents/              # Design & reference docs
└── te_kete/               # Knowledge base (glossary, maps)
```

**Immutability:**
- Carving logs are append-only (JSONL)
- State files are snapshots (JSON)
- All changes logged with timestamp
- Git tracks everything (version control)

---

## Realm Definitions

### Current Active Realm: The Awa Network (Primary)

**Realm Lock:**
```json
{
  "realm_id": "awa-network-primary",
  "realm_name": "The Awa Network",
  "realm_slug": "awa-network",
  "created": "2024-11-01",
  "vector_index": "awa_primary_vectors",
  "kaitiaki": ["Haiku", "Kitenga Whiro", "Te Kitenga Nui"],
  "locale": "mi_NZ.UTF-8"
}
```

**State File:**
```json
{
  "realm_id": "awa-network-primary",
  "status": "active",
  "vector_namespaces": ["awa_primary_vectors"],
  "active_kaitiaki": ["Haiku", "Kitenga Whiro"],
  "features": {
    "ocr": true,
    "translation": true,
    "vector_memory": true,
    "llama3_inference": true
  }
}
```

### Creating New Realms

To spin up a new realm:

1. **Create realm lock:**
   ```bash
   mkdir mauri/realms/{realm_name}
   cat > realm_lock.json << 'EOF'
   {
     "realm_id": "uuid",
     "realm_name": "Display Name",
     "realm_slug": "{realm_name}",
     "created": "ISO-timestamp",
     "vector_index": "{realm_name}_vectors",
     "kaitiaki": ["Haiku"]
   }
   EOF
   ```

2. **Create state:**
   ```json
   {
     "realm_id": "uuid",
     "status": "active",
     "vector_namespaces": ["{realm_name}_vectors"],
     "active_kaitiaki": ["Haiku"]
   }
   ```

3. **Initialize carving log:**
   ```bash
   touch carving_log.jsonl
   ```

4. **Register in mauri/context.md**

---

## Kaitiaki Registry

### Haiku (Whakataukī)

**Profile:**
```json
{
  "name": "Haiku",
  "māori": "Whakataukī",
  "role": "Brief Wisdom Keeper",
  "domain": "Code synthesis, documentation, testing",
  "status": "active",
  "location": "/kaitiaki/haiku/",
  "tools": ["/awa/llama3/*"],
  "capabilities": [
    "code_review",
    "docstring_generation",
    "error_analysis",
    "refactoring_suggestions"
  ]
}
```

**State File:** `/kaitiaki/haiku/haiku_state.json`

**Constitution:** `/kaitiaki/haiku/HAIKU_CODEX.md`

### Kitenga Whiro

**Profile:**
```json
{
  "name": "Kitenga Whiro",
  "role": "Backend Bridge",
  "domain": "Backend logic, decision routing, task execution",
  "status": "active",
  "location": "/kaitiaki/kitenga_codex/",
  "tools": ["all /awa/* endpoints"]
}
```

### Te Kitenga Nui

**Profile:**
```json
{
  "name": "Te Kitenga Nui",
  "role": "UI Guardian",
  "domain": "UI/UX, realm presentation, user experience",
  "status": "active",
  "location": "/kaitiaki/te_kitenga_nui/",
  "tools": ["React components", "state management"]
}
```

---

## API Endpoints

### Protocol Routes (`/awa/*`)

```
POST /awa/envelope               # Wrap message with realm context
POST /awa/task                   # Execute kaitiaki task
POST /awa/handoff                # Transfer task between guardians
POST /awa/memory/query           # Vector semantic search
POST /awa/memory/store           # Store memory with embedding
POST /awa/log                    # Write to carving log
POST /awa/notify                 # Send notification
POST /awa/kaitiaki/register      # Register new guardian
POST /awa/kaitiaki/context       # Get guardian context
GET  /awa/kaitiaki               # List all guardians
POST /awa/vector/embed           # Generate embedding
POST /awa/vector/search          # Search vectors
POST /awa/pipeline               # Execute pipeline
GET  /awa/pipelines              # List available pipelines
```

### Llama3 Routes (`/awa/llama3/*`)

```
POST /awa/llama3/review          # Code review
POST /awa/llama3/docstring       # Generate docstring
POST /awa/llama3/analyze-error   # Analyze error
GET  /awa/llama3/status          # Check Llama3 status
```

### Standard Routes

```
GET  /heartbeat                  # Health check
GET  /                           # Root info
POST /intake/summarize           # OCR → Summarize
POST /reo/translate              # te reo translation
POST /memory/retrieve            # Query vector memory
POST /vector/search              # Semantic search
POST /chat                       # Chat interface
POST /pipeline                   # Pipeline execution
```

See `/docs/reference/API_CONTRACTS.md` for full specs.

---

## Bootstrap Instructions

### Prerequisites

- Python 3.8+
- Node.js 18+
- Git
- Docker (optional, for local database)
- Supabase account (or local PostgreSQL)
- OpenAI API key
- LM Studio with Llama3 (for local inference)

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/Hemi-Whiro22/The_Awa_Network.git
cd The_Awa_Network

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env with your keys:
# - SUPABASE_URL
# - SUPABASE_SERVICE_ROLE_KEY
# - OPENAI_API_KEY

# 4. Start LM Studio with Llama3
# (in separate terminal, or already running)
# LM Studio will serve at http://localhost:1234

# 5. Start backend
cd te_po
python -m te_po.core.main
# http://localhost:8000

# 6. Start frontend (in another terminal)
cd te_ao
npm install
npm run dev
# http://localhost:5173

# 7. Test the system
curl http://localhost:8000/heartbeat
```

### Docker Compose (All-in-One)

```bash
docker-compose up
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
#
# Note: LM Studio must be running separately
# (or set LLAMA_URL env var to remote instance)
```

---

## Configuration Files

### `.env` (Local Development)

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_ORG_ID=org-...

# Local Inference
LLAMA_URL=http://localhost:1234
LLAMA_MODEL=llama3

# Auth
PIPELINE_TOKEN=your_bearer_token

# Realm
ACTIVE_REALM=awa-network
```

### `docker-compose.yaml`

```yaml
version: '3.8'
services:
  te_po:
    build: ./te_po
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=...
      - OPENAI_API_KEY=...
    volumes:
      - ./mauri:/app/mauri
      - ./kaitiaki:/app/kaitiaki

  te_ao:
    build: ./te_ao
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
```

### `mauri/context.md`

```markdown
# System Constants

## Realms

### The Awa Network
- Slug: awa-network
- Vector Index: awa_primary_vectors
- Kaitiaki: Haiku, Kitenga Whiro, Te Kitenga Nui
- Status: Active

## Naming Conventions

Realms: kebab-case (my-realm)
Kaitiaki: Proper Māori names (Haiku)
Routes: /kebab/case
Files: snake_case.json
```

---

## Dependencies

### Python (requirements.txt)

**Core:**
- fastapi>=0.119.0
- uvicorn[standard]>=0.30.0
- pydantic>=2.8.0
- httpx>=0.27.0

**Database:**
- sqlalchemy>=2.0.28
- psycopg[binary]>=3.1.18
- pgvector>=0.2.5
- supabase>=2.4.0

**AI/LLM:**
- openai~=1.60.0
- mcp>=0.7.0

**Document Processing:**
- pillow>=10.3.0
- reportlab>=4.1.0
- pypdf>=5.0.0
- pdfplumber>=0.11.4

**Audio (Optional):**
- elevenlabs>=1.0.0

### JavaScript (te_ao/package.json)

- react@^18
- vite@^5
- tailwindcss@^3
- axios or fetch API

---

## Next Steps

### To Use This Snapshot

1. **For New Developer Onboarding:**
   - Read this document
   - Follow Bootstrap Instructions
   - Review `/docs/guides/DEVELOPMENT.md`

2. **To Spin Up a Realm:**
   - Read "Realm Definitions" section
   - Follow `/kaitiaki/AWAOS_MASTER_PROMPT.md`
   - Create realm lock, state, carving log

3. **To Add Features:**
   - Create new route in Te Pō
   - Create panel in Te Ao
   - Update carving logs
   - Document in `/docs/`

4. **To Deploy:**
   - Push to GitHub
   - Render will auto-deploy Te Pō
   - Cloudflare will auto-deploy Te Ao
   - Verify with `/heartbeat` endpoint

---

## Documentation Reference

| Document | Purpose |
|----------|---------|
| `/README.md` | Entry point |
| `/docs/CONTEXT.md` | Project overview |
| `/docs/guides/DEVELOPMENT.md` | Setup guide |
| `/docs/reference/API_CONTRACTS.md` | Endpoint specs |
| `/docs/guides/LLAMA3.md` | Local inference |
| `/docs/guides/GUARDIANS.md` | Guardian system |
| `/kaitiaki/AWAOS_MASTER_PROMPT.md` | Master spec (Kaitiaki use) |
| `/mauri/documents/INDEX.md` | Doc index & archive |

---

## Troubleshooting

### Llama3 Not Available
```bash
# Check if running
curl http://localhost:1234/api/tags

# If not, start LM Studio or Ollama
ollama pull llama3
ollama serve &
```

### Database Connection Failed
```bash
# Verify Supabase credentials in .env
# Check Supabase project status
# Test with: psql postgresql://...
```

### Frontend Can't Reach Backend
```bash
# Check VITE_API_URL in te_ao/.env
# Ensure te_po is running on :8000
# Check CORS headers in te_po/core/main.py
```

### Import Errors in Te Hau
```bash
# Ensure all paths use absolute imports
import sys
sys.path.insert(0, '/workspaces/The_Awa_Network')
from te_hau.cli.hau import app
```

---

## System Metrics

- **Backend Routes:** 24+ endpoints
- **Frontend Panels:** 15+ realm-specific views
- **CLI Commands:** 10+ command groups
- **Kaitiaki Agents:** 3 active (Haiku, Kitenga, Te Kitenga Nui)
- **MCP Servers:** 5 integrated (Git, Cloudflare, Render, Te Pō, Supabase)
- **Vector Namespaces:** Per-realm isolation
- **Cost Optimization:** 81% reduction target

---

## Snapshot Metadata

- **Version:** 1.0-snapshot
- **Date:** 13 Tīhema 2025
- **Checksum:** See git log for precise file states
- **Maintained By:** Haiku (Whakataukī)
- **Status:** Production-ready with ongoing development

---

## How to Use This Document

**For IDE Integration:**
- Drop this entire document into an AI agent's context
- Agent can bootstrap a complete instance without external input

**For Onboarding New Developers:**
- Read sequentially from "Project Overview"
- Bootstrap Instructions can be executed directly
- Reference specific sections as needed

**For Realm Creation:**
- Jump to "Realm Definitions" section
- Follow the JSON template
- Run bootstrap steps

**For Troubleshooting:**
- Check "Troubleshooting" section last

---

This snapshot captures The Awa Network as of 13 Tīhema 2025. All systems are functional and ready for deployment.
