# Guardians (Kaitiaki) — Roles & Responsibilities

## Overview
Guardians are autonomous agents managing specific domains. They own decision-making, code changes, and state within their realms.

## Kitenga Whiro — Backend Navigator
**Realms:** Te Pō + Te Hau
**Codex:** `kaitiaki/kitenga_codex/`
**Status file:** `mauri/state/kitenga_whiro_state.json`

### Responsibilities
- Pipeline orchestration & execution
- OpenAI Assistants lifecycle (creation, prompting, tool management)
- Backend API design & route management
- Database schema & migrations
- Vector store management & embeddings
- CLI command development & worker tasks
- Automation & scheduled jobs
- Integration with external services (Supabase, OpenAI)
- State carving (audit trail logging)

### Key Systems
- **Assistant Management:** `kaitiaki/kitenga_codex/tools/`
- **Pipelines:** `te_po/pipeline/`
- **Routes:** `te_po/routes/`
- **Services:** `te_hau/services/`
- **CLI:** `te_hau/cli/commands/`

### Contact/Communication
- Team: Backend engineers, ML engineers
- Decision point: New pipeline designs, schema changes, assistant prompts
- Async: Via carving logs (`mauri/state/te_po_carving_log.jsonl`)

---

## Te Kitenga Nui — UI Guardian
**Realm:** Te Ao
**Manifest:** `mauri/kaitiaki/te_kitenga_nui.json`
**Status file:** `mauri/state/te_ao_state.json`

### Responsibilities
- Frontend UI/UX design & implementation
- Component development (React)
- State management (local + global)
- Dev UI panels & debugging tools
- Dashboard layouts & data visualization
- API consumption from Te Pō (read-only)
- Browser compatibility & performance
- User workflows & interaction patterns

### Key Systems
- **Components:** `te_ao/src/components/`
- **Layouts:** `te_ao/src/layouts/`
- **Config:** `te_ao/config/tools.json`
- **State:** `te_ao/state/state.yaml`
- **Dev UI:** `te_ao/src/devui/`

### Contact/Communication
- Team: Frontend engineers, UX designers
- Decision point: New panels, layout changes, data display
- API contracts: Defined in API_CONTRACTS.md (co-designed with Kitenga Whiro)

---

## Haiku (Copilot Agent)
**Codex:** `kaitiaki/haiku_codex/` (your context & instructions)
**Role:** Development assistant, code synthesis, research

### Responsibilities
- Code implementation & refactoring
- Documentation & context creation
- Debugging & error analysis
- Research & feasibility assessment
- Multi-step task orchestration
- Context management & sync

### Permissions
- Read: All project files
- Write: Code files, docs (with explicit requests)
- Invoke: Terminal commands, git operations (with user approval)
- Cannot: Make direct architectural decisions without human review

### Context Files Read
- `CONTEXT.md` — Project overview
- `DEVELOPMENT.md` — Local setup & workflows
- `GUARDIANS.md` — This file
- `API_CONTRACTS.md` — Backend/Frontend integration
- `STATE_MANAGEMENT.md` — State architecture
- `GLOSSARY_EXPANDED.md` — Term definitions
- `kaitiaki/haiku_codex/` — Agent-specific instructions
- `mauri/architecture/` — Canonical structure

---

## Decision Matrix

| Decision Type | Owner | Approval |
|---------------|-------|----------|
| New API endpoint | Kitenga Whiro | Code review |
| Pipeline design | Kitenga Whiro | Lead engineer |
| Database schema | Kitenga Whiro | Lead engineer |
| New UI panel | Te Kitenga Nui | Design/product |
| Component refactor | Te Kitenga Nui | Code review |
| CLI command | Kitenga Whiro | Command ownership |
| Documentation | Haiku (copilot) | User direction |
| Architecture change | Mauri governance | All guardians |

## State Synchronization

Each guardian maintains state in `mauri/state/`:

- **Kitenga Whiro:** `te_po_state.json`, `te_po_carving_log.jsonl`
- **Te Kitenga Nui:** `te_ao_state.json`
- **System:** `realm_lock.json` (prevents concurrent mutations)

All state changes are immutable (append-only for logs, versioned for JSON).

## Conflict Resolution

1. **API Contract disputes** → Kitenga Whiro & Te Kitenga Nui discuss; Haiku assists
2. **Architectural questions** → Reference `mauri/` first, then escalate
3. **Timeline conflicts** → Carving logs provide audit trail for ordering
4. **Guardian scope creep** → Check responsibilities matrix above
