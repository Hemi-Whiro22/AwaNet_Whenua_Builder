# Te Pō Visual Architecture Maps

**Quick reference diagrams and flowcharts**

---

## 1. System-Wide Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          AWA NETWORK EPICENTER                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐            │
│  │  Te Ao (Main)  │  │  Cards Realm   │  │  Custom App    │            │
│  │  Frontend      │  │  Frontend      │  │  Frontend      │            │
│  │  React/Vite    │  │  React/Vite    │  │  (Any tech)    │            │
│  │  :5173         │  │  :5174         │  │  (Anywhere)    │            │
│  └────────┬───────┘  └────────┬───────┘  └────────┬───────┘            │
│           │                    │                    │                    │
│           └────────────────────┼────────────────────┘                    │
│                                │                                         │
│                   HTTP/REST + WebSocket                                 │
│                   Bearer Token Auth                                     │
│                                │                                         │
│                                ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     TE PÒ FASTAPI BACKEND                      │   │
│  │           https://te-po-kitenga-backend.onrender.com            │   │
│  ├─────────────────────────────────────────────────────────────────┤   │
│  │                                                                 │   │
│  │  BearerAuthMiddleware → CORSMiddleware → UTF8Enforcer         │   │
│  │                                                                 │   │
│  │  ┌─────────────────────────────────────────────────────────┐  │   │
│  │  │                    23 Route Modules                      │  │   │
│  │  ├─────────────────────────────────────────────────────────┤  │   │
│  │  │                                                         │  │   │
│  │  │  Intake (OCR, Summarize)                              │  │   │
│  │  │  Chat & Memory (Sessions, Knowledge Base)             │  │   │
│  │  │  Vector Search (Semantic, Embeddings)                 │  │   │
│  │  │  Te Reo (Translation, Glossary)                       │  │   │
│  │  │  Documents (Upload, Retrieve)                         │  │   │
│  │  │  Research & Analysis                                  │  │   │
│  │  │  Guardian Agents (Kaitiaki)                           │  │   │
│  │  │  System Status (Health, Metrics)                      │  │   │
│  │  │  + 15 more specialized routes...                      │  │   │
│  │  │                                                         │  │   │
│  │  └─────────────────────────────────────────────────────────┘  │   │
│  │                                                                 │   │
│  │  ┌────────────────────────────────────────────────────────┐   │   │
│  │  │           Service Layer (Stateless)                   │   │   │
│  │  │  • Summary Service (Enhanced w/ cultural alignment)  │   │   │
│  │  │  • Vector Service (pgvector)                         │   │   │
│  │  │  • Memory Service (Semantic DB)                      │   │   │
│  │  │  • OCR Service (Google + Tesseract)                 │   │   │
│  │  │  • Chat Memory (Session tracking)                    │   │   │
│  │  │  • Local Storage (JSON files)                        │   │   │
│  │  └────────────────────────────────────────────────────────┘   │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
         │                          │                          │
         ▼                          ▼                          ▼
  ┌──────────────┐         ┌──────────────┐       ┌───────────────────┐
  │   OpenAI     │         │  Supabase    │       │ Google Cloud      │
  │   (LLM)      │         │  (PostgreSQL │       │ Vision (optional) │
  │              │         │  + pgvector) │       │ & Tesseract       │
  └──────────────┘         └──────────────┘       └───────────────────┘
         │                          │
         │ API Calls                │ Storage
         │ (Embeddings,             │ (Vectors,
         │  Chat,                   │  Sessions,
         │  Translation)            │  Audit logs)
         │                          │
  Read-only mount to /mauri/ (Governance metadata)
```

---

## 2. Data Flow: PDF Summarization Request

```
USER                     FRONTEND                    TE PÒ BACKEND
──────────               ────────                    ──────────────

1. Clicks                
   "Summarize"  ──→  React Component
   PDF                 useApi.summarize()
                            │
                            │ Reads:
                            │ - API_URL (env)
                            │ - REALM_TOKEN (env)
                            │
                       2. POST /intake/summarize
                          {
                            text: "...",
                            mode: "research"
                          }
                          Header: Authorization: Bearer xyz
                                                        │
                                                        ▼
                                        3. BearerAuthMiddleware
                                           ✓ Extract token
                                           ✓ Validate format
                                           ✓ Log to audit trail
                                                        │
                                                        ▼
                                        4. intake.py route handler
                                           summarize_text()
                                                        │
                                                        ▼
                                        5. summary_service.py
                                           • Build prompt (cultural)
                                           • Call OpenAI gpt-4o-mini
                                           • Format response:
                                             - Executive Summary
                                             - Key Points (12-15)
                                             - Cultural Context (6-8)
                                             - Implications (4-6)
                                           • Save to /storage/
                                                        │
                                                        ▼
                                        6. Response (JSON)
                                           {
                                             id: "summary_abc123",
                                             summary: "Executive...
                                                      \nKey Points:
                                                      \n• ...",
                                             mode: "research",
                                             saved: true
                                           }
                                                        │
                            ◀──────────────────────────┘
                            │
                       7. Display summary
                          in React UI
                            │
USER SEES:      ◀───────────┘
Formatted summary
with bullets
and cultural 
context
```

---

## 3. Multi-Project Architecture

```
                    ┌─────────────────────────────────┐
                    │   TE PÒ BACKEND (Render.com)    │
                    │   https://te-po-kitenga...      │
                    │                                 │
                    │   Port 8010 (backend)           │
                    │   Uvicorn + FastAPI             │
                    └──────────────┬──────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
          ▼                        ▼                        ▼
    ┌─────────────┐         ┌──────────────┐       ┌──────────────┐
    │  Te Ao      │         │ Cards Realm  │       │ Translator   │
    │  (Main)     │         │              │       │ Realm        │
    │             │         │              │       │              │
    │ localhost   │         │ localhost    │       │ localhost    │
    │ :5173       │         │ :5174        │       │ :5175        │
    │             │         │              │       │              │
    │ Token A     │         │ Token B      │       │ Token C      │
    │ (global)    │         │ (unique)     │       │ (unique)     │
    │             │         │              │       │              │
    │ Calls:      │         │ Calls:       │       │ Calls:       │
    │ • /intake/* │         │ • /cards/*   │       │ • /reo/*     │
    │ • /chat/*   │         │ • /vector/*  │       │ • /memory/*  │
    │ • /memory/* │         │ • /memory/*  │       │ • /chat/*    │
    └─────────────┘         └──────────────┘       └──────────────┘
          │                        │                        │
          │ Authorization:         │ Authorization:         │ Authorization:
          │ Bearer Token A         │ Bearer Token B         │ Bearer Token C
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
                                   ▼
                    ┌─────────────────────────────────┐
                    │  AUDIT LOG (per-realm tracking) │
                    │  • User: [realm_id]             │
                    │  • Action: [endpoint]           │
                    │  • Timestamp: [iso]             │
                    │  • Status: [200|400|500]        │
                    └─────────────────────────────────┘

                    All projects → 1 Te Pò backend
                    Different tokens → Different realms
```

---

## 4. Authentication Flow (Detailed)

```
┌──────────────────┐
│  Frontend App    │  const token = process.env.VITE_REALM_TOKEN
│  (Any Project)   │         ↓
│                  │  Stored in .env or secure storage
└────────┬─────────┘
         │
         │ POST /intake/summarize
         │ Header: Authorization: Bearer eyJh...
         │         Content-Type: application/json
         │         Body: { text: "...", mode: "research" }
         │
         ▼
┌──────────────────────────────────────────┐
│  BearerAuthMiddleware (Verify)           │
├──────────────────────────────────────────┤
│  1. Extract Authorization header        │
│     ✓ Check format: "Bearer <token>"    │
│  2. Validate token                      │
│     ✓ Format check                      │
│     ✓ JWT decode (if applicable)        │
│  3. Extract realm info (if using JWT)   │
│     ✓ realm_id from token payload       │
│  4. Add to request state                │
│     request.state.realm_token = token   │
│     request.state.realm_id = realm_id   │
│  5. Log to audit trail                  │
│     ✓ Save: { token, endpoint, realm }  │
└────────┬─────────────────────────────────┘
         │
    ✓ Valid?
    │
    ├─ YES ──→ ✓ Attach realm context
    │          ✓ Continue to route handler
    │          ▼
    │      [Route executes]
    │      [Returns response]
    │          │
    │          ▼
    │      ┌──────────────────┐
    │      │ Response (200)   │
    │      └──────────────────┘
    │
    └─ NO ──→ ✗ Log failed auth attempt
               ✗ Return 401 Unauthorized
               │
               ▼
           ┌──────────────────┐
           │ Error Response   │
           │ { detail:        │
           │   "Unauthorized" │
           │ }                │
           └──────────────────┘
```

---

## 5. Request Path: Route Selection

```
POST /intake/summarize
       │
       ▼
app.include_router(intake.router, prefix="/intake", tags=["Intake"])
       │
       ▼
┌──────────────────────────────────┐
│  te_po/routes/intake.py          │
├──────────────────────────────────┤
│                                  │
│  @router.post("/summarize")      │
│  async def intake_summarize(...) │
│                                  │
│  1. Receive Pydantic model       │
│     SummarizeRequest {           │
│       text: str,                 │
│       mode: str = "research"     │
│     }                            │
│                                  │
│  2. Call service function        │
│     summarize_text(text, mode)   │
│                                  │
│  3. Return response              │
│     {                            │
│       id: "summary_...",         │
│       summary: "...",            │
│       saved: true                │
│     }                            │
└──────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  te_po/services/summary_service │
├──────────────────────────────────┤
│  summarize_text(text, mode)      │
│  • Build OpenAI prompt           │
│  • Call OpenAI API               │
│  • Parse response sections       │
│  • Save to local storage         │
│  • Return summary dict           │
└──────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  OpenAI API (gpt-4o-mini)        │
│  • Input: Enhanced prompt        │
│  • Output: 4-section summary     │
└──────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│  te_po/storage/openai/           │
│  summary_<uuid>.json             │
│  (Persistent storage)            │
└──────────────────────────────────┘
```

---

## 6. Dependency Graph (External Only)

```
Te Pò Backend
    │
    ├─→ OpenAI
    │   ├─ gpt-4o-mini (summarization)
    │   ├─ gpt-4o (complex reasoning)
    │   ├─ text-embedding-3-large (vectors)
    │   └─ Vision API (image OCR)
    │
    ├─→ Supabase
    │   ├─ PostgreSQL (chat logs, cards)
    │   ├─ pgvector (semantic vectors)
    │   └─ Storage (large files, optional)
    │
    ├─→ Google Cloud Vision
    │   └─ Advanced image text extraction
    │
    └─→ Mauri (Local)
        ├─ Realm metadata (read-only)
        ├─ Governance configs
        └─ Seals & locks

Note: NO imports from te_hau, te_ao, or mauri code
```

---

## 7. Render Deployment Topology

```
┌──────────────────────────────────────────────┐
│            RENDER.COM Infrastructure         │
├──────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────────┐ │
│  │ Te Pò Service (Web Container)          │ │
│  ├────────────────────────────────────────┤ │
│  │                                        │ │
│  │ Docker Image: te_po.Dockerfile        │ │
│  │ Base: Python 3.12 + Ubuntu            │ │
│  │                                        │ │
│  │ ┌──────────────────────────────────┐  │ │
│  │ │  Uvicorn ASGI Server             │  │ │
│  │ │  • Host: 0.0.0.0                │  │ │
│  │ │  • Port: 10000 (internal)        │  │ │
│  │ │  • Workers: Auto (Render managed)│  │ │
│  │ │  • Reload: Off (production)      │  │ │
│  │ └──────────────────────────────────┘  │ │
│  │                                        │ │
│  │ Environment Variables:                 │ │
│  │ • OPENAI_API_KEY                      │ │
│  │ • SUPABASE_URL                        │ │
│  │ • SUPABASE_SERVICE_ROLE_KEY           │ │
│  │ • DATABASE_URL                        │ │
│  │ • LANG=mi_NZ.UTF-8 (Māori)            │ │
│  │ • LC_ALL=mi_NZ.UTF-8 (Māori)          │ │
│  │                                        │ │
│  │ Health Check:                          │ │
│  │ GET /health/full (every 10s)          │ │
│  │ Auto-restart if unhealthy             │ │
│  │                                        │ │
│  │ Auto-deploy: On main branch push      │ │
│  │                                        │ │
│  └────────────────────────────────────────┘ │
│                                              │
│  Public URL:                                 │
│  https://te-po-kitenga-backend.onrender.com │
│                                              │
└──────────────────────────────────────────────┘
         │
         ├─→ Internet
         │   ├─→ OpenAI (API calls)
         │   ├─→ Supabase (DB calls)
         │   └─→ Google Cloud (Vision API)
         │
         └─→ File Storage
             ├─→ /te_po/storage/ (local)
             └─→ Supabase Storage (optional)
```

---

## 8. State Architecture (Stateless Backend)

```
HTTP Request
    │
    ▼
┌─────────────────────────────────────┐
│  Te Pò (Stateless)                  │
│  • No persisted state in process    │
│  • All state externalized           │
│  • Request-scoped operations        │
│  • Horizontal scaling-friendly      │
└────────────────────┬────────────────┘
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
┌──────────────┐ ┌───────────┐ ┌──────────────┐
│ Supabase     │ │ Mauri     │ │ Local        │
│ (Primary)    │ │ (Read-    │ │ Storage      │
│              │ │  only)    │ │ (Fallback)   │
│ • Chat       │ │ • Realm   │ │ • Summaries  │
│   sessions   │ │   locks   │ │ • Documents  │
│ • Vectors    │ │ • Seals   │ │ • Logs       │
│ • Cards      │ │ • Tokens  │ │ • Metadata   │
│ • Audit logs │ │ • Config  │ │              │
└──────────────┘ └───────────┘ └──────────────┘
      │              │              │
      │ Persistent   │ Immutable    │ Semi-
      │              │              │ persistent
      └──────────────┴──────────────┘
              │
         HTTP Response
```

---

## 9. Route Module Organization

```
Routes (23 modules):

├─ Core APIs
│  ├─ intake.py              [OCR, summarize]
│  ├─ chat.py                [Sessions, realtime]
│  ├─ vector.py              [Embeddings, search]
│  ├─ memory.py              [Knowledge base]
│  └─ documents.py           [File storage]
│
├─ Language & Analysis
│  ├─ reo.py                 [Te reo translation]
│  ├─ research.py            [Document analysis]
│  └─ ocr.py                 [Text extraction]
│
├─ AI Agents
│  ├─ assistant.py           [OpenAI Assistants]
│  ├─ kitenga_backend.py     [Kaitiaki agents]
│  └─ roshi.py               [Helper agent]
│
├─ System
│  ├─ status.py              [Health checks]
│  ├─ metrics.py             [Prometheus]
│  ├─ logs.py                [Event logging]
│  ├─ state.py               [State queries]
│  └─ dev.py                 [Debug tools]
│
├─ Integration
│  ├─ awa_protocol.py        [Inter-realm]
│  ├─ llama3.py              [Local inference]
│  ├─ pipeline.py            [Orchestration]
│  ├─ assistants_meta.py     [Agent metadata]
│  ├─ cards.py               [Knowledge cards]
│  └─ sell.py                [Commerce]
│
└─ Specialized
   ├─ kitenga_tool_router.py [Tool routing]
   └─ [custom routes...]

Each module is independent and stateless
```

---

## 10. Scaling Scenario

```
BEFORE:
┌──────────────────────────┐
│ Single Te Pò Instance    │
│ (Render Starter)         │
│ • 1 dyno                 │
│ • Max ~50 req/min        │
│ • Single failure point    │
└──────────────────────────┘

AFTER (Scaled):
┌──────────────────────────────────────────┐
│ Render Auto-Scaling                      │
├──────────────────────────────────────────┤
│                                          │
│ ┌──────────────┐ ┌──────────────┐      │
│ │ Te Pò Inst 1 │ │ Te Pò Inst 2 │      │
│ │ (Dyno A)     │ │ (Dyno B)     │      │
│ └──────────────┘ └──────────────┘      │
│        │                │                │
│        └────────┬───────┘                │
│                 │                        │
│         Load Balancer (Render)           │
│         • Auto-scale on demand           │
│         • Horizontal scaling             │
│         • No code changes                │
│                 │                        │
│ ┌────────────────────────────────────┐  │
│ │ Shared State (Supabase)            │  │
│ │ • One PostgreSQL + pgvector        │  │
│ │ • Persistent across instances      │  │
│ │ • Connection pooling               │  │
│ └────────────────────────────────────┘  │
│                                          │
└──────────────────────────────────────────┘

Result:
• 10 → 100 concurrent users (auto-scale)
• Horizontal scaling: Add more instances
• No downtime: Rolling updates
• Stateless: Each instance is identical
```

---

## Summary

Te Pò is:
- ✅ **Stateless** → scales horizontally
- ✅ **Independent** → no code dependencies
- ✅ **Multi-Project Ready** → CORS + bearer auth
- ✅ **Production Ready** → Render deployed
- ✅ **Well-Structured** → 23 independent route modules
- ✅ **Monitored** → Prometheus + audit logs

**Suitable as Awa Network epicenter for unlimited frontend projects.**
