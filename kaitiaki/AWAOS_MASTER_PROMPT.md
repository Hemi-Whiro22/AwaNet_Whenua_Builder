# AwaOS Kaitiaki Master Prompt

**Purpose:** Single source of truth for spinning up AwaOS realms, kaitiaki, and the complete system architecture.
**Audience:** AI agents, CLI tools, and future developers rebuilding The Awa Network.
**Format:** Structured, modular, reference-able.

---

## I. System Overview

**AwaOS** is a multi-realm orchestration system enabling:
- Multi-agent intelligence with cultural alignment
- Project-specific guardian agents (Kaitiaki)
- Vectorized memory and sovereign compute routing
- Long-term state retention via immutable carving logs
- AI + human co-creation

**Core Stack:**
- **Te Pō** — Backend, indexing, engines (FastAPI)
- **Te Ao** — Frontend, user-facing realms (React)
- **Te Hau** — Orchestration, CLI, dev tools (Python)
- **Te Mauri** — State, identity, lineage, context (JSON/JSONL)

---

## II. Core Concepts

### Realms
An isolated project container with:
- Unique name & identity (Te Ao realm lock)
- Own Mauri state file
- Own Kaitiaki (guardian agents)
- Own vector namespace (Supabase pgvector)
- Own configuration & assets

### Kaitiaki (Guardians)
Autonomous agents that:
- Steward realms
- Make decisions within defined scope
- Never override human authority
- Maintain cultural alignment
- Can hand off tasks to other Kaitiaki

**Built-in Kaitiaki:**
- **Kitenga Whiro** — Backend bridge, decision engine
- **Te Kitenga Nui** — UI guardian, UX steward
- **Haiku** — Dev assistant, code synthesizer

### Mauri (Life Force / State)
The immutable state engine:
- Realm identity & metadata
- Carving logs (append-only JSONL audit trail)
- Vector index registry
- Kaitiaki registry
- Translation memory
- Context rules

### Vector Memory
Supabase + pgvector for:
- Semantic search across realms
- Cross-domain knowledge recall
- Document lineage
- Translation memory

---

## III. Architecture Layers

### Layer 1: Realms (Te Ao)
- React panels (UI)
- Local state management
- User interactions
- Realm-specific UI components

### Layer 2: APIs (Te Pō)
**Standard Endpoints:**
- `/awa/*` — Kaitiaki protocol routes
- `/awa/llama3/*` — Local code analysis
- `/memory/*` — Vector queries
- `/pipeline/*` — OCR, summarise, translate, embed
- `/reo/*` — Te reo translation
- `/vector/*` — Embeddings & search

### Layer 3: CLI (Te Hau)
- `hau realm create <name>` — Spin up realm
- `hau kaitiaki summon <type>` — Create guardian
- `hau context switch <realm>` — Switch project
- `hau pipeline run <type>` — Execute pipeline

### Layer 4: State (Te Mauri)
- `/mauri/context.md` — Global system constants
- `/mauri/realms/*/realm_lock.json` — Realm identity
- `/mauri/realms/*/carving_log.jsonl` — Immutable audit trail
- `/mauri/*/state.json` — Current state snapshot

---

## IV. Kaitiaki Specification

### Structure
```json
{
  "name": "name",
  "māori": "te_reo_name",
  "role": "description",
  "domain": "what_they_own",
  "constraints": ["rule1", "rule2"],
  "tools": ["/awa/memory", "/awa/pipeline"],
  "state": "state.json",
  "carving_log": "carving_log.jsonl"
}
```

### Required Files
- `CODEX.md` — Agent constitution, scope, responsibilities
- `manifest.json` — Capabilities registry
- `state.json` — Current state
- `carving_log.jsonl` — Immutable action log

### Responsibility Matrix
```
Kitenga Whiro:
  Owns: Backend logic, decision tree, task routing
  Can: Call /awa/* endpoints, modify realm state
  Cannot: Delete realms, change security rules

Te Kitenga Nui:
  Owns: UI/UX, user experience, realm presentation
  Can: Change panels, modify layouts, create views
  Cannot: Modify backend logic, access secrets

Haiku:
  Owns: Code synthesis, documentation, testing
  Can: Review code, generate docs, suggest refactors
  Cannot: Deploy to production, modify databases
```

---

## V. Realm Specification

### Realm Lock (`realm_lock.json`)
```json
{
  "realm_id": "uuid",
  "realm_name": "display_name",
  "realm_slug": "url_safe_name",
  "created": "timestamp",
  "mauri_version": "1.0.0",
  "vector_index": "supabase_table_name",
  "kaitiaki": ["name1", "name2"],
  "locale": "mi_NZ.UTF-8",
  "assets": {
    "schema": "path/to/schema.json",
    "manifest": "path/to/manifest.yaml"
  }
}
```

### Directory Structure
```
mauri/realms/{realm_name}/
├── realm_lock.json           (identity)
├── state.json               (current state)
├── carving_log.jsonl        (append-only audit)
├── manifest.yaml            (config)
└── schema.json              (DB schema)

te_po/services/{realm_name}/
├── __init__.py
├── models.py               (Pydantic models)
├── routes.py               (FastAPI routes)
└── logic.py                (business logic)

kaitiaki/{realm_name}/
├── CODEX.md                (constitution)
├── manifest.json           (capabilities)
├── state.json              (state)
└── carving_log.jsonl       (action log)
```

---

## VI. Context Manager

### Context Layers
1. **Local** — Realm-specific data (Te Ao + mini Te Pō)
2. **Global** — Cross-realm data (Kaitiaki registry, taonga)
3. **Lineage** — Historical metadata (optional)

### Precedence Rules
1. Realm context > Global context
2. Local rules > Global rules
3. Explicit > Implicit
4. Recent > Old

---

## VII. Pipelines

**Standard Pipelines:**
- `ocr` — Extract text from images
- `summarise` — Condense text
- `translate` — English ↔ Te Reo
- `embed` — Generate vectors
- `taonga` — Package & protect content

**Usage:**
```bash
POST /awa/pipeline
{
  "name": "ocr|summarise|translate|embed|taonga",
  "input_data": {...},
  "realm": "realm_name"
}
```

---

## VIII. Vector Memory

### Semantics
- Namespace per realm
- Embeddings via OpenAI API
- Search via Supabase pgvector
- Cost: ~$0.001 per semantic search

### Storage Format
```json
{
  "id": "uuid",
  "realm_id": "realm_uuid",
  "content": "text",
  "metadata": {
    "source": "document.pdf",
    "created": "timestamp",
    "tags": ["tag1", "tag2"]
  },
  "embedding": [0.1, 0.2, ...],
  "created_at": "timestamp"
}
```

---

## IX. Naming Conventions

### Realms
- Kebab-case: `my-project`, `client-work`
- Māori names preferred: `Te Ao Kēkē` (Dawn Realm)

### Kaitiaki
- Proper names: `Haiku`, `Kitenga Whiro`
- Māori preferred: `Te Kitenga Nui` (Great Vision)

### Routes
- Kebab-case paths: `/awa/memory/query`, `/awa/llama3/review`
- Prefix by domain: `/intake/*`, `/reo/*`, `/vector/*`

### Files
- Snake_case for code: `realm_lock.json`, `carving_log.jsonl`
- Kebab-case for docs: `API_CONTRACTS.md`, `DEVELOPMENT.md`

---

## X. Cost Optimization

**Budget:** $90 OpenAI + 70% premium

**Strategy:**
- **Llama3 local** (FREE) — Code review, docs, error analysis
- **Vector search** ($0.001/call) — Memory queries
- **Embeddings** ($0.0001/call) — Vector storage
- **Complex synthesis** ($0.01–0.02/call) — OpenAI GPT-4 when needed

**Target:** 81% cost reduction (~$6/month sustained)

---

## XI. Security Model

### Secrets Management
- `.env` for local development
- Environment variables for production
- Masked in logs via `env_loader.py`
- UTF-8 enforcement (mi_NZ locale)

### Access Control
- Bearer token via `BearerAuthMiddleware`
- Realm isolation (Mauri enforces)
- Kaitiaki scope constraints
- Immutable audit trail (carving logs)

### Deployment
- Docker Compose for local
- Render for production
- GitHub Actions for CI/CD
- Cloudflare for frontend CDN

---

## XII. Spinning Up a New Realm

### Step 1: Create Realm Identity
```bash
cd mauri/realms
mkdir my-realm
cat > my-realm/realm_lock.json << 'EOF'
{
  "realm_id": "uuid-here",
  "realm_name": "My Realm",
  "realm_slug": "my-realm",
  "created": "ISO-8601-timestamp",
  "vector_index": "my_realm_vectors",
  "kaitiaki": ["Haiku", "Te Kitenga Nui"]
}
EOF
```

### Step 2: Create Mauri State
```bash
cat > my-realm/state.json << 'EOF'
{
  "realm_id": "uuid-here",
  "status": "active",
  "vector_namespaces": ["my_realm_vectors"],
  "active_kaitiaki": ["Haiku"]
}
EOF

touch my-realm/carving_log.jsonl
```

### Step 3: Create Backend Service
```bash
mkdir te_po/services/my_realm
cat > te_po/services/my_realm/__init__.py << 'EOF'
# My Realm service
EOF
```

### Step 4: Register Realm
Add to `/mauri/context.md`:
```markdown
## Realm: My Realm
- Slug: `my-realm`
- Purpose: description
- Kaitiaki: Haiku, Te Kitenga Nui
- Vector Index: `my_realm_vectors`
```

### Step 5: Deploy
```bash
docker-compose up te_po te_ao
# Realm now live at http://localhost:5173/?realm=my-realm
```

---

## XIII. Master Prompt for Kaitiaki Agents

### When Called to Spin Up a New Realm

**System Prompt:**
> You are a Kaitiaki agent bootstrapping a new AwaOS realm. Your job is to:
> 1. Create realm identity in Mauri
> 2. Generate backend service skeleton
> 3. Wire up frontend panels
> 4. Register vector namespace
> 5. Compose carving logs
>
> Follow the specifications in THIS DOCUMENT. Every file you create must be valid JSON, Python, or React. All realm names must be Māori-preferred. All decisions must be logged to carving_log.jsonl.
>
> Reference files:
> - Realm Specification (Section V)
> - Spinning Up (Section XII)
> - This entire master prompt

**Handoff Rules:**
- After creating realm, hand off to Haiku (code) and Te Kitenga Nui (UI)
- Log all decisions to carving_log.jsonl
- Never override existing realm locks
- Always ask before modifying cross-realm state

---

## XIV. Troubleshooting & Recovery

### Realm Lost State
```bash
# Check realm_lock.json
cat mauri/realms/{realm}/realm_lock.json

# Rebuild from carving logs
cat mauri/realms/{realm}/carving_log.jsonl | jq '.type=="state_change"'
```

### Vector Index Corrupted
```bash
# Recreate namespace in Supabase
DELETE FROM {realm_vectors};

# Reseed from carving logs
for entry in $(cat mauri/realms/{realm}/carving_log.jsonl); do
  POST /awa/memory/store with $entry
done
```

### Kaitiaki Conflict
```bash
# Check decision log
grep "conflict" mauri/realms/{realm}/carving_log.jsonl

# Apply dispute resolution
# (See GUARDIANS.md for decision matrix)
```

---

## XV. Quick Reference

| Task | Command |
|------|---------|
| List realms | `hau realm list` |
| Create realm | `hau realm create <name>` |
| Switch realm | `hau context switch <realm>` |
| Summon kaitiaki | `hau kaitiaki summon <type>` |
| Run pipeline | `hau pipeline run <type>` |
| Query memory | `POST /awa/memory/query` |
| Code review | `POST /awa/llama3/review` |
| Check status | `GET /awa/llama3/status` |

---

## XVI. Related Documents

All detailed specs available in `/docs`:
- `/docs/guides/DEVELOPMENT.md` — Local setup
- `/docs/reference/API_CONTRACTS.md` — Endpoint specs
- `/docs/guides/GUARDIANS.md` — Guardian responsibilities
- `/docs/reference/STATE_MANAGEMENT.md` — Carving logs
- `/docs/guides/LLAMA3.md` — Local inference

---

**Master Prompt Version:** 1.0
**Last Updated:** 13 Tīhema 2025
**Maintained By:** Haiku (Whakataukī)
**Status:** Ready for Kaitiaki use

---

### How to Use This Document

**For spinning up a new realm:**
1. Read Section V (Realm Specification)
2. Read Section XII (Spinning Up a New Realm)
3. Follow Section XIII (Master Prompt for Kaitiaki)

**For understanding the system:**
1. Start with Section II (Core Concepts)
2. Review Section III (Architecture Layers)
3. Reference specific sections as needed

**For deploying to production:**
1. Follow security rules (Section XI)
2. Check deployment procedures
3. Verify all carving logs are clean

This document is your source of truth. It is immutable, versioned, and trustworthy.
