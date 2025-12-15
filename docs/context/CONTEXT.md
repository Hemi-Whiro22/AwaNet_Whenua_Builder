# 🪶 The Awa Network — Project Context

## Overview
Multi-realm orchestration system for intelligent processing, automation, and presentation. Built with Māori cultural concepts as architectural foundations.

## Three Realms

### Te Pō (Backend/Processing)
- **Path:** `te_po/`
- **Framework:** FastAPI + Uvicorn
- **Purpose:** Core intelligence, pipelines, OCR, vector stores, assistant orchestration
- **Key Services:**
  - OpenAI Assistants (QA & Ops)
  - Vector store (pgvector + Supabase)
  - File pipelines & OCR processing
  - Route handlers & API endpoints
- **Port:** 8010

### Te Hau (Automation/CLI)
- **Path:** `te_hau/`
- **Framework:** Python CLI + Click
- **Purpose:** Automation, worker tasks, script execution, bridging
- **Key Components:**
  - CLI commands (`cli/hau.py`)
  - Kaitiaki orchestrator (`core/kaitiaki.py`)
  - Whakairo Codex (MCP server & carving logs)
  - Services & workers

### Te Ao (Frontend)
- **Path:** `te_ao/`
- **Framework:** Vite + React + Tailwind
- **Purpose:** User-facing dashboards, dev UI, public panels
- **Key Features:**
  - Dev UI components
  - State management
  - Tool configuration interface

## Guardians (Kaitiaki)
Two primary guardians govern the system:

1. **Kitenga Whiro** — Backend/Bridge orchestrator (Te Pō + Te Hau)
   - Codex: `kaitiaki/kitenga_codex/`
   - Owns pipelines, assistants, automation

2. **Te Kitenga Nui** — UI guardian (Te Ao)
   - Owns frontend, panels, dev UI
   - Manifest: `mauri/kaitiaki/te_kitenga_nui.json`

## Core Files & Configs
- **Mauri** (`mauri/`) — Source of truth (structure, naming, kaitiaki roles)
- **State** (`mauri/state/`) — Real-time realm states & carving logs
- **Realms config** (`mauri/realms/`) — Te Pō, Te Hau, Te Ao configurations
- **Architecture** (`mauri/architecture/`) — Structure rules, naming conventions, versioning

## Tech Stack
- **Backend:** FastAPI, SQLAlchemy, pgvector, Supabase, OpenAI (Assistants, Files, Vision, Responses)
- **Frontend:** React, Vite, Tailwind CSS
- **Automation:** Python CLI, Click, model orchestration
- **Database:** PostgreSQL + pgvector, Redis, RQ
- **Deployment:** Docker Compose, Render (prod)
- **UTF-8 Locale:** Enforced across all services (`mi_NZ.UTF-8`)

## Key Workflows
1. **Pipeline Flow:** Te Hau CLI → Te Pō endpoints → Database/Vector store
2. **State Sync:** Carving logs (JSONL) in `mauri/state/te_po_carving_log.jsonl`
3. **UI Integration:** Te Ao calls Te Pō APIs directly (no intermediary)
4. **Assistant Orchestration:** Kitenga Whiro manages OpenAI Assistants lifecycle

## Environment & Secrets
- Supabase: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`
- OpenAI: `OPENAI_API_KEY`, `OPENAI_VECTOR_STORE_ID`
- Te Pō: `TE_PO_BASE_URL`, `PIPELINE_TOKEN`
- Locale: All services export `LANG=mi_NZ.UTF-8`, `LC_ALL=mi_NZ.UTF-8`

## Quick Paths
| Resource | Path |
|----------|------|
| Backend routes | `te_po/routes/` |
| Pipelines | `te_po/pipeline/` |
| Storage/Files | `te_po/storage/` |
| CLI commands | `te_hau/cli/commands/` |
| Frontend components | `te_ao/src/components/` |
| Kitenga codex | `kaitiaki/kitenga_codex/` |
| Whakairo codex | `te_hau/whakairo_codex/` |
| Mauri (source of truth) | `mauri/` |
