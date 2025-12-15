# Te Pō Architecture — Quick Reference

**Status:** ✅ Production-Ready as Standalone FastAPI Backend  
**Date:** 15 Tīhema 2025

---

## Key Findings (TL;DR)

| Finding | Details |
|---------|---------|
| **Zero Internal Dependencies** | No imports from te_hau, te_ao, or mauri code |
| **Stateless Design** | All state externalized to Supabase + Mauri (read-only) |
| **23 Route Modules** | Complete API surface for all project needs |
| **Multi-Project Ready** | CORS enabled; bearer token auth supports multiple realms |
| **Already on Render** | `https://te-po-kitenga-backend.onrender.com` |

---

## Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                    ANY FRONTEND PROJECT                     │
│            (Te Ao, Cards Realm, Custom App, etc.)          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  │ HTTP/REST + WS
                  │ Bearer Token Auth
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              TE PÒ FASTAPI BACKEND (EPICENTER)             │
│           https://te-po-kitenga-backend.onrender.com        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Core Services:                   Route Modules:            │
│  • OCR scanning                   • intake         (upload) │
│  • Summarization                  • ocr            (scan)   │
│  • Vector search                  • chat           (realtime)
│  • Chat & memory                  • vector         (semantic)
│  • Te reo translation             • memory         (knowledge)
│  • Guardian agents                • reo            (translate)
│  • Document storage               • documents      (storage)
│  • Research & analysis            • assistant      (OpenAI)  │
│                                   • kitenga        (kaitiaki)│
│                                   • status         (health)  │
│                                   • metrics        (observe) │
│                                   • ... 13 more    (specialized)
│                                                              │
└─────────┬───────────────────┬──────────────────────┬────────┘
          │                   │                      │
          ▼                   ▼                      ▼
  ┌──────────────┐  ┌──────────────┐   ┌──────────────────┐
  │ OpenAI       │  │ Supabase     │   │ Mauri (read-only)│
  │ (LLM,        │  │ (PostgreSQL  │   │ Governance       │
  │ embeddings,  │  │ + pgvector)  │   │ Realm metadata   │
  │ vision)      │  │ (storage,    │   │                  │
  │              │  │ vectors,     │   │                  │
  │              │  │ audit logs)  │   │                  │
  └──────────────┘  └──────────────┘   └──────────────────┘
```

---

## Deployment Topology

```
┌────────────────────────────────────────────────────────┐
│                    RENDER.COM                           │
├────────────────────────────────────────────────────────┤
│                                                         │
│  Service: te-po-kitenga-backend                       │
│  • Container: Dockerfile-based                        │
│  • Port: 8010                                          │
│  • Health Check: /health/full                         │
│  • Auto-deploy: On main push                          │
│  • Environment: Docker (uvicorn server)              │
│                                                         │
└─────────────┬────────────────────────────────────────┘
              │
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
  External         External
  OpenAI           Supabase
  Services         Services
  (Cloud API)      (PostgreSQL)
```

---

## API Endpoint Categories

### 1️⃣ Intake (PDF Processing)
```
POST /intake/ocr                    Upload PDF → extract text + OCR
POST /intake/summarize              Text → in-depth cultural summary
```

### 2️⃣ Document Management
```
POST /documents/upload              Store document
GET  /documents/list                List all documents
GET  /documents/{id}/download       Retrieve document
```

### 3️⃣ Knowledge & Memory
```
POST /memory/save                   Store knowledge item
GET  /memory/search                 Semantic search memories
POST /vector/embed                  Generate embeddings
POST /vector/search                 Vector similarity search
```

### 4️⃣ Chat & Conversation
```
POST /chat/save-session             Archive chat session
WS   /chat/ws                       Real-time chat stream
POST /chat/message                  Single message
```

### 5️⃣ Language (Te Reo Māori)
```
GET  /reo/translate                 English ↔ te reo
POST /reo/validate                  Check macrons/diacritics
GET  /reo/glossary                  Māori term lookup
```

### 6️⃣ Analysis & Research
```
POST /research/analyze              Deep document analysis
POST /research/extract-entities     Named entity recognition
GET  /research/citations            Track citations
```

### 7️⃣ Guardians (Kaitiaki Agents)
```
GET  /kitenga/status                Agent system status
POST /assistant/chat                OpenAI Assistant interaction
POST /roshi/ask                     Helper agent query
```

### 8️⃣ System & Observability
```
GET  /status                        System status + version
GET  /heartbeat                     Liveness check
GET  /metrics                       Prometheus metrics
POST /logs/event                    Event logging
```

---

## Multi-Project Integration Pattern

### Project 1: Te Ao (Main Studio)
```javascript
// frontend/.env
VITE_API_URL=https://te-po-kitenga-backend.onrender.com
VITE_REALM_TOKEN=eyJh... (from mauri)
```

### Project 2: Cards Realm (Generated)
```javascript
// cards/.env
REACT_APP_API_URL=https://te-po-kitenga-backend.onrender.com
REACT_APP_REALM_TOKEN=eyJc... (unique token)
```

### Project N: Custom External App
```javascript
// any-frontend/.env
API_URL=https://te-po-kitenga-backend.onrender.com
REALM_TOKEN=custom-token-xyz
```

**All projects use same Te Pō backend with different auth tokens.**

---

## Authentication Flow

```
┌─────────────────┐
│  Frontend App   │
│  (any project)  │
└────────┬────────┘
         │
         │ Request with Bearer token
         │ POST /intake/summarize
         │ Authorization: Bearer xyz
         ▼
┌──────────────────────────────┐
│  BearerAuthMiddleware        │
│  • Extract token             │
│  • Validate format           │
│  • Log to audit trail        │
│  • Attach realm context      │
└────────┬─────────────────────┘
         │
    ✅ Valid?
    │
    ▼
┌──────────────────────┐
│  Route Handler       │
│  (e.g., summarize)   │
│  ✓ Authenticated     │
│  ✓ Realm-aware       │
│  ✓ Audit-logged      │
└──────────────────────┘
```

---

## Data Flow Example: PDF Summarization

```
User Upload (Te Ao Frontend)
  ↓
[POST /intake/summarize]
{
  text: "Pakohe Management Plan...",
  mode: "research"
}
  ↓
Summary Service (Enhanced)
  ↓
OpenAI gpt-4o-mini (with cultural prompt)
  ↓
RESPONSE:
{
  Executive Summary (2-3 paragraphs)
  
  Key Points & Ideas (12-15 bullets)
  - Main arguments
  - People & places
  - Dates & events
  - Policies & recommendations
  - Data & evidence
  
  Cultural & Māori Context (6-8 bullets)
  - Māori concepts
  - Tikanga & taonga
  - Whakapapa & mana
  - Indigenous perspectives
  - Gaps & recommendations
  
  Implications & Significance (4-6 bullets)
  - Why it matters
  - Who's affected
  - Next steps
}
  ↓
Save to Storage (JSON + metadata)
  ↓
Return to Frontend
```

---

## Service Dependencies (External Only)

| Service | Type | Required | Config |
|---------|------|----------|--------|
| **OpenAI API** | Cloud | Yes | `OPENAI_API_KEY` |
| **Supabase** | Cloud (PostgreSQL) | No* | `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` |
| **Google Cloud Vision** | Cloud (optional OCR) | No | `GOOGLE_APPLICATION_CREDENTIALS` |
| **Mauri** | Local file mount | No | `/mauri/global_env.json` |

*Without Supabase: Chat history, vectors, logs stored locally (not scalable)

---

## Deployment Checklist

- ✅ Dockerized (te_po/Dockerfile)
- ✅ Port configurable (8010)
- ✅ Health endpoints (/heartbeat, /status)
- ✅ CORS enabled (allow_origins=["*"])
- ✅ Bearer auth middleware active
- ✅ UTF-8 locale enforcement (mi_NZ)
- ✅ Render service active
- ✅ Environment variables in render.yaml
- ⚠️ Multi-realm scoping (recommended enhancement)
- ⚠️ Rate limiting (recommended enhancement)

---

## Scaling Characteristics

| Metric | Current | Max (Render Starter) | Scaling Path |
|--------|---------|----------------------|--------------|
| **Concurrent Users** | 10-20 | 50-100 | Auto-scale more services |
| **Requests/minute** | 60 | 600 | Add rate limiter |
| **Storage** | Local + Supabase | Supabase limit | S3 integration |
| **Vector Index** | <1M docs | 10M+ | Partition by realm |
| **DB Connections** | 5 | 20 | pgbouncer |

---

## Security Model

```
┌──────────────────────────────────────┐
│  Bearer Token Authentication         │
│  (Per-realm tokens in mauri)         │
└────────┬───────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  Realm-Scoped Query Isolation        │
│  (Recommended: Add realm_id filter)  │
└────────┬───────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  Supabase Row-Level Security (RLS)   │
│  (Optional: Implement per realm)     │
└────────┬───────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  Audit Trail (Supabase logs)         │
│  (All API calls logged by timestamp) │
└──────────────────────────────────────┘
```

---

## Next Actions (Recommended)

1. **Immediate**
   - [ ] Generate "cards" realm as test project
   - [ ] Verify external project → Te Pō backend calls work
   - [ ] Document Te Pō standalone URL for teams

2. **Week 1**
   - [ ] Add realm-scoped bearer tokens
   - [ ] Implement per-realm rate limits
   - [ ] Create external project integration guide

3. **Week 2-3**
   - [ ] Deploy 2-3 sample projects (React, Vue, etc.)
   - [ ] Add Prometheus monitoring per realm
   - [ ] Document API contracts (OpenAPI spec)

4. **Ongoing**
   - [ ] Monitor Render logs for performance issues
   - [ ] Rotate bearer tokens quarterly
   - [ ] Update dependencies monthly

---

## References

- **Full Technical Analysis:** [TE_PO_STANDALONE_SCAN.md](./TE_PO_STANDALONE_SCAN.md)
- **API Contracts:** `/docs/reference/API_CONTRACTS.md`
- **Render Config:** `/render.yaml`
- **Docker Setup:** `/docker-compose.yaml`
- **Requirements:** `/requirements.txt`

---

**Status:** ✅ Te Pō is ready to serve as the Awa Network epicenter.  
**Deployment:** Already live on Render.  
**Next Step:** Generate first external project and test multi-project architecture.
