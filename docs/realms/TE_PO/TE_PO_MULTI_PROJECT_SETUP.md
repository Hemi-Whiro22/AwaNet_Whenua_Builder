# Te Pō Multi-Project Setup Guide

**Status:** Ready to implement  
**Target:** Use te_po as standalone FastAPI backend for multiple frontend projects

---

## Phase 1: Verification (Today)

### Step 1: Confirm Te Pō Standalone Status
```bash
cd /workspaces/The_Awa_Network/te_po

# Verify no internal realm imports
grep -r "from te_hau\|from te_ao\|from mauri\|import te_hau" . --include="*.py"
# Expected: No matches ✅

# Check CORS is enabled
grep -A 5 "CORSMiddleware" core/main.py
# Expected: allow_origins=["*"] ✅
```

### Step 2: Test Current Te Pō Running Locally
```bash
# Terminal 1: Start Te Pò
cd te_po
python -m uvicorn core.main:app --host 0.0.0.0 --port 8010 --reload

# Terminal 2: Test endpoints
curl -X GET http://localhost:8010/heartbeat
# Expected: { "status": "alive", "timestamp": "..." } ✅

curl -X POST http://localhost:8010/intake/summarize \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{"text": "Sample text", "mode": "research"}'
# Expected: { "id": "summary_...", "summary": "...", "saved": true } ✅
```

### Step 3: Verify Render Deployment
```bash
# Check current Render service status
curl -I https://te-po-kitenga-backend.onrender.com/heartbeat
# Expected: HTTP/1.1 200 OK ✅
```

---

## Phase 2: Create First External Project ("Cards Realm")

### Step 1: Generate Realm Using Template
```bash
cd /workspaces/The_Awa_Network

python te_hau/scripts/generate_realm.py \
  --realm-id "cards" \
  --realm-name "Cards Realm" \
  --te-po-url "https://te-po-kitenga-backend.onrender.com"

# Output:
# ✅ Created: /workspaces/The_Awa_Network/cards/
# ✅ Structure:
#    ├── .env                 (realm config with unique token)
#    ├── te_ao/               (React frontend)
#    ├── te_hau/              (mini proxy layer)
#    ├── mauri/               (realm metadata)
#    └── requirements.txt
```

### Step 2: Examine Generated Realm Structure
```bash
cd cards
ls -la

# Key files:
cat .env
# Expected output:
# REALM_ID=cards
# REALM_NAME=Cards Realm
# TE_PO_URL=https://te-po-kitenga-backend.onrender.com
# BEARER_KEY=eyJh... (auto-generated unique token)

cat mauri/realm_lock.json
# Expected: Realm metadata, timestamp, seal hash
```

### Step 3: Start Cards Realm Frontend
```bash
cd cards/te_ao
npm install
npm run dev

# Expected: Vite dev server on http://localhost:5174
#          (note: different port than main te_ao)
```

### Step 4: Test Cards Realm → Te Pō Backend Calls

**From Cards Frontend (localhost:5174):**

```javascript
// cards/te_ao/src/hooks/useApi.js (or create new file)
const API_URL = process.env.VITE_API_URL || 
                "https://te-po-kitenga-backend.onrender.com";
const REALM_TOKEN = import.meta.env.VITE_REALM_TOKEN;

export async function testSummarize() {
  const response = await fetch(`${API_URL}/intake/summarize`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${REALM_TOKEN}`
    },
    body: JSON.stringify({
      text: "Sample card content for summarization",
      mode: "research"
    })
  });
  
  console.log('Cards Realm → Te Pō Response:', await response.json());
  return response.json();
}
```

**Verify in browser console:**
```
✅ Cards Realm calls main Te Pō backend
✅ Uses unique realm token
✅ Gets summarized response
```

---

## Phase 3: Enhanced Authentication

### Step 1: Update Render Environment Variables
```bash
# render.yaml updates:
envVars:
  # ... existing vars ...
  - key: ALLOW_MULTIPLE_REALMS
    value: "true"
  - key: REALM_BEARER_KEYS
    value: "cards:eyJc...,whai_tika:eyJw..."
  - key: RATE_LIMIT_ENABLED
    value: "true"
  - key: RATE_LIMIT_REQUESTS_PER_MINUTE
    value: "60"
```

### Step 2: Enhance BearerAuthMiddleware (Optional)
```python
# te_po/utils/middleware/auth_middleware.py (enhance existing)

class EnhancedBearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization", "")
        
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid scheme")
            
            # Extract realm from token (optional)
            # realm_id = extract_realm_id(token)
            
            # Add to request state for logging
            request.state.realm_token = token
            # request.state.realm_id = realm_id
            
            response = await call_next(request)
            
            # Log to audit trail
            log_request(request, response, token)
            
            return response
            
        except Exception:
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"}
            )
```

### Step 3: Add Per-Realm Rate Limiting (Optional)
```python
# te_po/utils/middleware/rate_limit.py (new file)

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Usage in routes:
# @router.post("/intake/summarize")
# @limiter.limit("60/minute")
# async def intake_summarize(...):
#     ...
```

---

## Phase 4: Monitoring & Observability

### Step 1: Enable Prometheus Metrics
```python
# te_po/utils/metrics.py (already exists, ensure active)

from prometheus_client import Counter, Histogram

request_count = Counter(
    'te_po_requests_total',
    'Total requests',
    ['method', 'endpoint', 'realm']
)

request_duration = Histogram(
    'te_po_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)
```

### Step 2: Access Metrics Endpoint
```bash
curl http://localhost:8010/metrics

# Expected output (Prometheus format):
# # HELP te_po_requests_total Total requests
# # TYPE te_po_requests_total counter
# te_po_requests_total{method="POST",endpoint="/intake/summarize",realm="cards"} 5.0
# te_po_requests_total{method="GET",endpoint="/status",realm="unknown"} 2.0
```

### Step 3: Optional: Set Up Grafana Dashboard
```bash
# If using Prometheus + Grafana (local development):
# 1. Add Prometheus scrape config:
#    targets: ['localhost:8010/metrics']
# 
# 2. Create Grafana dashboard:
#    - Request rate per realm
#    - Error rate by endpoint
#    - Response latency p50/p95/p99
#    - Vector search performance
```

---

## Phase 5: Documentation & Integration Guide

### Step 1: Create External Project Integration Docs
```markdown
# docs/EXTERNAL_PROJECT_INTEGRATION.md

## Quick Start

### 1. Get API Access
- Request realm token from Awa Network team
- Token format: `eyJ...` (JWT)
- Store in `.env` as `REACT_APP_REALM_TOKEN`

### 2. Base URL
```
https://te-po-kitenga-backend.onrender.com
```

### 3. Example: React Integration
[See Phase 2, Step 4 example]

### 4. Available Endpoints
[Copy from TE_PO_ARCHITECTURE_QUICKREF.md]

### 5. Error Handling
[Document common errors + solutions]
```

### Step 2: Create OpenAPI/Swagger Spec (Optional)
```python
# te_po/core/main.py (enhance existing)

app = FastAPI(
    title="Kitenga Whiro — Māori Intelligence Engine",
    version="1.0.0",
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc",         # ReDoc
    openapi_url="/openapi.json" # OpenAPI spec
)

# Access at: http://localhost:8010/docs
```

### Step 3: Create cURL Examples
```bash
# Get in docs/CURL_EXAMPLES.md

# 1. Authenticate & get status
curl -X GET https://te-po-kitenga-backend.onrender.com/status \
  -H "Authorization: Bearer YOUR_REALM_TOKEN"

# 2. Summarize text
curl -X POST https://te-po-kitenga-backend.onrender.com/intake/summarize \
  -H "Authorization: Bearer YOUR_REALM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your document text here...",
    "mode": "research"
  }'

# 3. Search memory
curl -X GET "https://te-po-kitenga-backend.onrender.com/memory/search?query=pakohe" \
  -H "Authorization: Bearer YOUR_REALM_TOKEN"
```

---

## Phase 6: Deploy Additional Projects

### Template: Generate "Translator" Realm
```bash
python te_hau/scripts/generate_realm.py \
  --realm-id "translator" \
  --realm-name "Te Reo Translator" \
  --te-po-url "https://te-po-kitenga-backend.onrender.com"

cd translator/te_ao
npm install
npm run dev
# Now at http://localhost:5175
```

### Template: Generate "Research" Realm
```bash
python te_hau/scripts/generate_realm.py \
  --realm-id "research" \
  --realm-name "Research Assistant" \
  --te-po-url "https://te-po-kitenga-backend.onrender.com"

cd research/te_ao
npm install
npm run dev
# Now at http://localhost:5176
```

### Verify All Projects Work
```bash
# Terminal 1: Main Te Ao
cd te_ao && npm run dev
# http://localhost:5173

# Terminal 2: Cards Realm
cd cards/te_ao && npm run dev
# http://localhost:5174

# Terminal 3: Translator Realm
cd translator/te_ao && npm run dev
# http://localhost:5175

# Terminal 4: Research Realm
cd research/te_ao && npm run dev
# http://localhost:5176

# Terminal 5: Te Pò Backend
cd te_po
python -m uvicorn core.main:app --host 0.0.0.0 --port 8010 --reload

# All 4 frontends → 1 Te Pò backend ✅
```

---

## Testing Checklist

### Local Testing
- [ ] Te Pò starts without errors
- [ ] `/status` endpoint returns 200
- [ ] `/heartbeat` endpoint is alive
- [ ] Bearer token validation works
- [ ] Cards realm frontend loads
- [ ] Cards realm → Te Pò API call succeeds
- [ ] Summary returns cultural alignment
- [ ] Memory search returns results
- [ ] Chat session saves correctly

### Render Testing (Production)
- [ ] `https://te-po-kitenga-backend.onrender.com/status` → 200
- [ ] All environment variables are set
- [ ] Supabase connection is active
- [ ] OpenAI API calls succeed
- [ ] External project can call Render deployment

### Multi-Project Testing
- [ ] 3+ realms can call same Te Pō backend
- [ ] Each realm gets unique response
- [ ] Audit logs track requests per realm
- [ ] Rate limiting works (if enabled)
- [ ] No data leakage between realms

---

## Troubleshooting

### Issue: Bearer token rejected
```
Error: 401 Unauthorized
Solution:
1. Check Authorization header format: "Bearer <token>"
2. Verify token in .env matches mauri/realm_lock.json
3. Check token isn't expired (if using JWT)
```

### Issue: CORS error from frontend
```
Error: Access-Control-Allow-Origin missing
Solution:
1. Verify CORSMiddleware is in core/main.py
2. Check allow_origins=["*"]
3. Clear browser cache
4. Test with curl first (curl ignores CORS)
```

### Issue: OpenAI API key invalid
```
Error: Invalid API key
Solution:
1. Check OPENAI_API_KEY in render.yaml
2. Verify key is current (rotate quarterly)
3. Check key has permissions (Assistants, Vision, Embeddings)
```

### Issue: Supabase connection failed
```
Error: Could not connect to PostgreSQL
Solution:
1. Verify SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY
2. Check Supabase project is active (not paused)
3. Check IP allowlist (if applicable)
4. Test connection with psql or web console
```

---

## Production Checklist

- [ ] All realms use production Te Pō URL (Render)
- [ ] Bearer tokens stored in secure .env files
- [ ] Rate limiting enabled per realm
- [ ] Monitoring/metrics accessible
- [ ] Supabase backups configured
- [ ] OpenAI API key rotated recently
- [ ] Audit logs accessible
- [ ] Health checks passing
- [ ] CORS policy reviewed (consider restricting)
- [ ] Token rotation policy documented

---

## Success Criteria

✅ **Te Pò as Epicenter is achieved when:**

1. Multiple frontend projects call same Te Pò backend
2. Each project uses unique realm token
3. All API endpoints function correctly
4. Monitoring shows request distribution
5. Documentation is complete
6. Production deployment is stable
7. New projects can onboard in <30 minutes

---

## Timeline Estimate

| Phase | Tasks | Duration |
|-------|-------|----------|
| 1. Verification | Confirm te_po independence, test endpoints | 1-2 hours |
| 2. First Project | Generate cards realm, test API calls | 1-2 hours |
| 3. Auth Enhancement | Add realm scoping, rate limiting | 2-3 hours |
| 4. Monitoring | Set up metrics, logging | 1-2 hours |
| 5. Documentation | Write guides, curl examples | 2-3 hours |
| 6. Deploy More | Generate 2-3 additional realms | 2-3 hours |

**Total: 9-15 hours** (can be parallelized)

---

**Next Step:** Start Phase 1 (verification) and report back with results!
