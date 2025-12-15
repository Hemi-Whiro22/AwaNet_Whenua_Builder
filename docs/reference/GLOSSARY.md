# Glossary — The Awa Network Terms & Concepts

## Realms (Physical Domains)

### Te Pō — The Night / Backend Processing
The backend intelligence layer. Where all processing, analysis, and computation happens. Named after the Māori concept of potential and depth.
- **Contains:** Pipelines, databases, AI assistants, storage systems
- **Owned by:** Kitenga Whiro
- **Port:** 8010 (localhost)

### Te Hau — The Wind / Automation & CLI
The movement and orchestration layer. CLI commands, worker tasks, and bridging between realms.
- **Contains:** CLI interface, scheduled tasks, workers, event listeners
- **Owned by:** Kitenga Whiro
- **Metaphor:** Wind that carries information between Te Pō and Te Ao

### Te Ao — The Light / Frontend & Presentation
The user-facing interface. Dashboards, panels, and interactive tools for humans.
- **Contains:** React components, state management, UI layouts
- **Owned by:** Te Kitenga Nui
- **Metaphor:** Light that reveals Te Pō's intelligence to humans

---

## Guardians & Authority (Kaitiaki)

### Kitenga Whiro — The Navigator
The primary orchestrator of backend systems and automation. Manages pipelines, assistants, CLI, and bridge operations.
- **Codex:** `kaitiaki/kitenga_codex/`
- **Realms:** Te Pō, Te Hau
- **Responsibilities:** Assistants, pipelines, database, vector store, CLI, workers

### Te Kitenga Nui — The Great Navigator (UI Aspect)
The guardian of user interfaces and presentation. Manages all public-facing elements.
- **Codex:** `mauri/kaitiaki/te_kitenga_nui.json`
- **Realm:** Te Ao
- **Responsibilities:** Components, layouts, UX, dashboards

### Haiku (Copilot Agent)
The development assistant and context keeper. Synthesizes code, manages documentation, and orchestrates multi-step tasks.
- **Codex:** `kaitiaki/haiku_codex/`
- **Realms:** All (read-only mostly)
- **Responsibilities:** Implementation, documentation, research, debugging

---

## State & Operations

### Mauri — The Source of Truth
The canonical configuration and governance system. Contains naming rules, structure definitions, and kaitiaki signatures. All changes flow through here.
- **Path:** `mauri/`
- **Contains:** Architecture rules, pipeline maps, realm definitions, versioning rules
- **Authority:** Master branch is always live

### Carving Log (Te Po Carving / Whakairo)
An immutable, append-only record of all operations. Each entry is a "carving" — a permanent mark in the system's history.
- **Format:** JSON Lines (`.jsonl`)
- **Examples:**
  - `mauri/state/te_po_carving_log.jsonl` — Backend operations
  - `mauri/state/te_hau_carving_log.jsonl` — CLI & automation operations
- **Purpose:** Audit trail, debugging, state reconstruction

### Whakairo — Carving / Recording
Literally: Māori traditional carving. In this context: recording meaningful operations in carving logs.
- **Tool:** `te_hau/whakairo_codex/` — The codex for recording state changes
- **Process:** Every significant operation appends a carving log entry

---

## Data & Processing

### Vector Store
A pgvector-backed embedding database for semantic search and RAG.
- **Provider:** Supabase (PostgreSQL + pgvector extension)
- **Contents:** Document embeddings, metadata, timestamps
- **Purpose:** Enable semantic search across knowledge base
- **Managed by:** Kitenga Whiro

### Pipeline
A sequence of steps for processing data. OCR, vector sync, file ingestion, etc.
- **Examples:**
  - OCR pipeline: PDF → images → text → embeddings
  - Vector sync: Ingest → embed → store → index
- **Execution:** Via Te Hau CLI or scheduled in Te Pō
- **Idempotent:** Safe to retry without side effects

### Assistant
An OpenAI Assistant instance. Persistent, tool-enabled AI agents.
- **Types:**
  - QA Assistant: Retrieval-augmented question answering
  - Ops Assistant: Tool-enabled operations
- **Lifecycle:** Create → Configure tools → Deploy → Monitor → Update
- **Managed by:** Kitenga Whiro

### Embedding / Vector
A high-dimensional representation of text/meaning. Used for semantic search.
- **Model:** OpenAI's embedding model (specified in config)
- **Dimension:** Typically 1536 (depends on model)
- **Purpose:** Enable "fuzzy" search across documents
- **Storage:** pgvector in Supabase

---

## Architecture Concepts

### Realm Lock
A mutual exclusion mechanism to prevent concurrent state mutations.
- **Location:** `mauri/realms/realm_lock.json`
- **Duration:** Max 5 minutes
- **Purpose:** Ensure data consistency during writes
- **Owner:** Kitenga Whiro

### Drift Protection
Rules to detect and prevent architecture violations.
- **File:** `mauri/architecture/drift_protection.json`
- **Examples:**
  - "Te Ao must not access storage directly"
  - "Only Kitenga can write to carving logs"
- **Enforcement:** Pre-commit hooks, linters, CI checks

### Naming Conventions
Canonical rules for naming files, functions, classes, and concepts.
- **File:** `mauri/architecture/naming_conventions.json`
- **Examples:**
  - Routes: `/api/v1/<resource>/<action>`
  - Components: `<Feature><Type>.jsx` (e.g., `ChatPanel.jsx`)
  - Functions: `snake_case` (Python), `camelCase` (JavaScript)

### Versioning Rules
How to manage API versions, schema changes, and backward compatibility.
- **File:** `mauri/architecture/versioning_rules.json`
- **Current API:** v1
- **Breaking changes:** Get own version number (v2, v3, etc.)

---

## Development Concepts

### Dev Container
Docker + VSCode Remote integration for consistent development environment.
- **Config:** `.devcontainer/devcontainer.json`
- **Benefits:**
  - Reproducible environment
  - Automatic dependency installation
  - GPU access for local testing
- **UTF-8:** Pre-configured with `mi_NZ.UTF-8` locale

### Hot Reload (HMR)
Vite feature that updates frontend without full page refresh.
- **Te Ao:** Enabled by default in dev mode
- **Te Pō:** Python auto-reload via `--reload` flag in uvicorn

### Render Deployment
Cloud platform for hosting prod services.
- **Config:** `render.yaml` per realm
- **Deployment:** Automatic on master push
- **Secrets:** Passed via Render dashboard (never in git)

---

## Process Concepts

### Async / Decoupled
Operations don't block each other. Te Ao doesn't wait for Te Pō; it polls/subscribes instead.
- **Benefits:** Resilience, scalability
- **Trade-offs:** Eventual consistency (not immediate)

### Idempotent
Safe to retry. Running operation twice = running once.
- **Examples:** File uploads, vector indexing, state writes
- **Critical for:** Pipelines, webhooks, recovery flows

### UTF-8 Enforcement
All services handle Māori text correctly.
- **Locale:** `mi_NZ.UTF-8`
- **Verification:** Health endpoint confirms UTF-8 status
- **Scope:** Database, file I/O, API responses

---

## Files & Locations Quick Reference

| Concept | Primary Path |
|---------|--------------|
| Mauri (source of truth) | `mauri/` |
| Architecture rules | `mauri/architecture/` |
| Guardian signatures | `mauri/kaitiaki/` |
| State files | `mauri/state/` |
| Carving logs | `mauri/state/*_carving_log.jsonl` |
| Kitenga Whiro codex | `kaitiaki/kitenga_codex/` |
| Whakairo (recording) | `te_hau/whakairo_codex/` |
| Te Pō backend | `te_po/` |
| Te Hau CLI/automation | `te_hau/` |
| Te Ao frontend | `te_ao/` |
| Backend routes | `te_po/routes/` |
| Pipelines | `te_po/pipeline/` |
| Storage/files | `te_po/storage/` |
| CLI commands | `te_hau/cli/commands/` |
| React components | `te_ao/src/components/` |

---

## Related Concepts

### Pūtea (Budget/Treasure)
Resource management concept. Not yet implemented, but relevant for token counting and rate limiting.

### Whānau (Family/Group)
Multiple agents/processes working together. Kitenga Whiro + Te Kitenga Nui + Haiku form the whānau.

### Manaakitanga (Hospitality/Care)
Guides error handling and user-facing messaging. Be clear, helpful, respectful.

### Kaitiakitanga (Guardianship/Stewardship)
The principle underlying guardian roles. Each kaitiaki cares for their domain.
