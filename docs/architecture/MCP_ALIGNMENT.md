# MCP Integration & Alignment Report

## Overview
Your MCP suite is well-designed and complementary to The Awa Network. All 5 servers integrate cleanly with current realms and can be activated to maximize my (Haiku) capabilities.

---

## Current MCP Servers

### 1. **Git Server** ✅ Active/Ready
**Path:** `mcp/git_server/`
**Manifest:** `manifest.json`
**Language:** TypeScript (via MCP SDK)

**Capabilities:**
- Local git operations (commit, branch, tag)
- GitHub API integration (PR creation, tagging)
- Semantic versioning for realms
- Deployment workflows (auto-tag on deploy)

**Integration:**
- Triggered by: `te_hau` CLI commands (`tehau new`, `tehau deploy`, `tehau seal`)
- Flows: `pr_on_evolve`, `tag_on_deploy`
- Owner: Kitenga Whiro (bridges Te Hau → Git)

**Current Status:** Fully compatible. Ready to activate.

---

### 2. **Cloudflare Server** ✅ Active/Ready
**Path:** `mcp/cloudflare_server/`
**Manifest:** `manifest.json`
**Language:** Python

**Capabilities:**
- Pages deployment management
- Environment variable configuration
- Custom domain setup
- Cache management

**Integration:**
- Triggered by: `tehau deploy` command
- Te Ao (frontend) deployments to Cloudflare Pages
- Realm-specific domain setup (e.g., `realm-name.example.com`)

**Current Status:** Fully compatible. Depends on `CLOUDFLARE_API_TOKEN` env var.

---

### 3. **Render Server** ✅ Active/Ready
**Path:** `mcp/render_server/`
**Manifest:** `manifest.json`
**Language:** Python

**Capabilities:**
- Service deployment (Te Pō, Te Hau backends)
- Environment variable management
- Health checks & monitoring
- Service control (start/stop/restart)

**Integration:**
- Triggered by: `tehau deploy` command
- Mini Te Pō backend deployments
- Render API orchestration

**Current Status:** Fully compatible. Depends on `RENDER_API_KEY` env var.

---

### 4. **Te Pō Server** ⚠️ Needs Activation
**Path:** `mcp/tepo_server/`
**Config Files:** `routes.json`, `mauri.json`
**Language:** TypeScript (MCP SDK)

**What It Does:**
Provides direct access to Te Pō backend via custom `/awa/*` protocol routes:

**Routes:**
```
POST /awa/envelope       — Wrap message with realm context
POST /awa/task          — Execute kaitiaki task
POST /awa/handoff       — Transfer task between kaitiaki
POST /awa/memory/query  — Query vector memory
POST /awa/memory/store  — Store to vector memory
POST /awa/log           — Log activity
POST /awa/notify        — Send notification
POST /awa/kaitiaki/*    — Register/context kaitiaki
POST /awa/vector/*      — Embeddings & search
POST /awa/pipeline      — Run pipeline
```

**Pipelines:**
- `ocr` — OCR image/PDF
- `summarise` — Summarize document
- `translate` — Translate with dialect support
- `embed` — Generate embeddings
- `taonga` — Classify/protect/index protected content

**Kaitiaki in Te Pō:**
- `whiro` (root) — Global intelligence
- `awanui` — Translator
- `ruru` — OCR specialist
- `mataroa` — Research/summary
- `te_puna` — Knowledge portal

**Mauri Config:**
- Lineage enforcement & seal validation
- Tapu levels (NOA → ABSOLUTE)
- Mana types (WHENUA, TANGATA, ATUA)
- Validation sequences (realm check → glyph → seal → env → lineage → tapu)

**Current Status:** Ready to activate. Needs:
1. Implementation of `/awa/*` routes in `te_po/core/main.py`
2. Handler functions for each route
3. Integration with existing assistants/pipelines

**Impact on Haiku:** HIGH
- Gives me direct access to Te Pō operations (not just APIs)
- Can query/store vector memory
- Can execute pipelines programmatically
- Can manage kaitiaki tasks

---

### 5. **Supabase Server** ⚠️ Needs Activation
**Path:** `mcp/supabase_server/`
**Config Files:** `schema.json`, `commands.json`
**Language:** Python

**What It Does:**
Direct database inspection & management tool.

**Schema Includes:**
- `realm_registry` — All realms
- `ti_memory` — Vector memory (pgvector embeddings)
- `pdf_summaries` — Document summaries + embeddings
- `ocr_logs` — OCR processing history
- `translations` — Translation records + glossary
- `taonga` — Protected content with classification
- (+ more tables for documents, files, audit logs, etc.)

**Commands Available:**
- Schema inspection (list tables, columns, constraints)
- Safe queries (SELECT only by default)
- Migration suggestions
- RLS (Row-Level Security) rules inspection

**Current Status:** Ready to activate. Needs:
1. Environment setup (`SUPABASE_URL`, `SUPABASE_SERVICE_KEY`)
2. RLS policy configuration
3. Safe-query validation (ensure read-only by default)

**Impact on Haiku:** HIGH
- Direct database introspection
- Can query vector memory without API round-trip
- Can inspect schema for migrations
- Can validate data consistency
- Can audit logs

---

### 6. **Whakairo Codex (Te Hau)** ✅ Already Active
**Path:** `te_hau/whakairo_codex/mcp/`
**Manifest:** `manifest.yaml`
**Language:** Python + YAML

**What It Does:**
Carving/recording agent for state mutations. Inspects Supabase schema, proposes migrations, generates SQL.

**Tools:**
- `supabase_sql` — Execute SQL (schema inspection by default, safe)
- `supabase_storage` — Bucket/object inspection (read-only)
- `rules_writer` — Evaluate carving rules, output recommendations

**Rules:**
- Never delete/drop without confirmation
- Always show migrations before applying

**Current Status:** LIVE. This is where I should carve state changes.

---

## Compatibility Matrix

| Server | Language | State | Owner | Depends On | Enhances |
|--------|----------|-------|-------|-----------|----------|
| Git | TypeScript | Ready | Kitenga | Git binary | Versioning, PRs |
| Cloudflare | Python | Ready | Kitenga | CF API token | Te Ao deployment |
| Render | Python | Ready | Kitenga | Render API key | Te Pō/Hau deployment |
| **Te Pō** | TypeScript | **Needs impl** | Kitenga | Te Pō running | Vector ops, pipelines |
| **Supabase** | Python | **Needs impl** | Kitenga | Supabase access | DB queries, audits |
| Whakairo | Python | **Live** | Kitenga | Supabase | State carving |

---

## How They Align With The Awa Network

### Realm Mapping
```
Te Ao (Frontend)
  ↓ (deploy via Cloudflare Server)
  Cloudflare Pages

Te Pō (Backend)
  ↓ (deploy via Render Server)
  Render.com
  ↓ (accessed via Te Pō Server MCP)
  /awa/* routes for kaitiaki tasks, pipelines, memory

Te Hau (CLI/Automation)
  ↓ (versioning via Git Server)
  GitHub tags & PRs
  ↓ (state recording via Whakairo)
  mauri/state/*.jsonl carving logs

All Realms
  ↓ (database layer via Supabase Server)
  PostgreSQL + pgvector
```

### Guardian Integration
**Kitenga Whiro** orchestrates all deployment & backend operations:
- Git Server: Version releases, tag builds
- Render Server: Deploy backends
- Cloudflare Server: Deploy frontends
- Te Pō Server: Execute tasks, manage memory
- Supabase Server: Inspect/audit database
- Whakairo: Record all mutations

---

## Recommended Activation Plan

### Phase 1: Immediate (Already Ready)
✅ Git Server — Use for tagging and PR workflows
✅ Cloudflare Server — Deploy Te Ao updates
✅ Render Server — Deploy Te Pō/Hau updates
✅ Whakairo — Record state changes

**Action:** Install these servers in MCP config (claude_desktop_config.json or similar)

### Phase 2: Implementation (1-2 hours)
⚠️ **Te Pō Server:** Implement `/awa/*` routes in `te_po/core/main.py`
- Create route handlers for envelope, task, memory, pipeline, kaitiaki
- Integrate with existing assistants
- Add validation & auth

⚠️ **Supabase Server:** Configure safe SQL queries
- Set up read-only mode by default
- Configure RLS for multi-tenant safety
- Add schema inspection tools

### Phase 3: Advanced (Optional)
- Custom prompts for each server (e.g., "Create a migration for table X")
- Batch operations (tag + deploy + record in one command)
- Cross-realm workflows (deploy Te Pō → update Te Ao API config → deploy Te Ao)

---

## How Haiku Benefits

### Current (Without Implementation)
- ❌ Can't directly execute Te Pō tasks
- ❌ Can't query vector memory directly
- ❌ Can't inspect/modify database
- ❌ Limited version/deployment control

### After Phase 1 (Ready Now)
- ✅ Can tag releases (Git Server)
- ✅ Can deploy frontends (Cloudflare Server)
- ✅ Can deploy backends (Render Server)
- ✅ Can record state changes (Whakairo)

### After Phase 2 (Implementation)
- ✅ Can execute pipelines (OCR, summarize, embed)
- ✅ Can query vector memory (semantic search)
- ✅ Can manage kaitiaki tasks
- ✅ Can inspect/audit database
- ✅ Can propose/validate migrations
- ✅ Can handle multi-step workflows autonomously

---

## Next Steps

1. **Confirm env vars are set:**
   ```bash
   echo $CLOUDFLARE_API_TOKEN
   echo $RENDER_API_KEY
   echo $SUPABASE_URL
   echo $SUPABASE_SERVICE_KEY
   ```

2. **Choose your MCP integration:**
   - VS Code Remote MCP extension
   - Claude desktop config
   - Cline/other IDE integration

3. **Implement Phase 2** (Te Pō + Supabase servers):
   - Create `/awa/*` routes in te_po
   - Set up Supabase MCP handlers
   - Test each endpoint

4. **Create MCP-aware prompts** in mauri (optional):
   ```yaml
   # mauri/mcp_prompts.yaml
   - id: deploy_te_ao
     tools: [cloudflare_server, git_server]
   - id: query_knowledge_base
     tools: [supabase_server, tepo_server]
   ```

---

## Files to Create/Update

### Create
- `mcp/tepo_server/server.py` — Implement Te Pō MCP server
- `mcp/supabase_server/server.py` — Implement Supabase MCP server
- `mcp/README.md` — MCP setup & usage guide
- `.mcp/config.json` — MCP server registry

### Update
- `te_po/core/main.py` — Add `/awa/*` routes
- `te_hau/cli/start_whakairo.py` — Add Supabase server startup
- `mauri/architecture/mcp_integration.json` — Governance for MCP
- `kaitiaki/HAIKU_CODEX.md` — Add MCP usage guidelines

---

## Summary

Your MCP setup is **production-ready** for git/deployment. With ~2 hours of implementation, you can unlock:
- Direct Te Pō task execution
- Vector memory queries
- Database inspection & audits
- Multi-step autonomous workflows
- Real-time carving logs

This gives Haiku (me) the ability to work **without context window bloat** — I can fetch what I need directly from the database instead of reading 50 files.

**Recommendation:** Activate Phase 1 immediately, then tackle Phase 2 to unlock full potential.
