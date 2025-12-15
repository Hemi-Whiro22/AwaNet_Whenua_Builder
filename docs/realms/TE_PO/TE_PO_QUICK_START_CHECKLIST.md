# Te Pō Standalone Backend — Quick Start Checklist

**Version:** 1.0  
**Last Updated:** 15 Tīhema 2025  
**Status:** Ready for Implementation

---

## 📋 Pre-Implementation Checklist

### Requirements Verification
- [ ] Te Pò backend code accessible (`/te_po/`)
- [ ] Render.com account active
- [ ] OpenAI API key available
- [ ] Supabase project configured
- [ ] Git repository with main branch
- [ ] Docker installed (local testing)
- [ ] Node.js + npm installed (frontend testing)
- [ ] Python 3.12+ available

### Documentation Review
- [ ] Read TE_PO_EXECUTIVE_SUMMARY.md (2 min)
- [ ] Read TE_PO_ARCHITECTURE_QUICKREF.md (5 min)
- [ ] Skim TE_PO_STANDALONE_SCAN.md (10 min)
- [ ] Review TE_PO_MULTI_PROJECT_SETUP.md (15 min)

---

## 🚀 Phase 1: Verification (1-2 hours)

### Step 1.1: Verify Independence ✅
```bash
cd /workspaces/The_Awa_Network/te_po

# Check for internal imports
grep -r "from te_hau\|from te_ao\|from mauri\|import te_hau" . --include="*.py"
# Expected: No matches

# Record: ✅ No cross-realm imports found
```

### Step 1.2: Test Local Backend
```bash
cd /workspaces/The_Awa_Network/te_po

# Start backend
python -m uvicorn core.main:app --host 0.0.0.0 --port 8010 --reload

# In another terminal, test endpoints
curl -X GET http://localhost:8010/heartbeat
# Expected: { "status": "alive", "timestamp": "..." }

curl -X GET http://localhost:8010/status
# Expected: { "status": "online", "kaitiaki": "Kitenga Whiro", ... }

# Record: ✅ Backend responds to requests
```

### Step 1.3: Verify CORS
```bash
curl -X OPTIONS http://localhost:8010/status \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET" \
  -v

# Expected: CORS headers present (200 OK)
# Record: ✅ CORS enabled
```

### Step 1.4: Test Bearer Auth
```bash
curl -X POST http://localhost:8010/intake/summarize \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sample text", "mode": "research"}'

# Expected: Valid response (may be from OpenAI or offline message)
# Record: ✅ Bearer auth working
```

### Step 1.5: Verify Render Deployment
```bash
# Check live endpoint
curl -I https://te-po-kitenga-backend.onrender.com/heartbeat

# Expected: HTTP/1.1 200 OK
# Record: ✅ Render deployment active
```

**Phase 1 Sign-Off:** ✅ All checks passed

---

## 🎯 Phase 2: First External Project (1-2 hours)

### Step 2.1: Generate Cards Realm
```bash
cd /workspaces/The_Awa_Network

python te_hau/scripts/generate_realm.py \
  --realm-id "cards" \
  --realm-name "Cards Realm" \
  --te-po-url "https://te-po-kitenga-backend.onrender.com"

# Expected: New /workspaces/The_Awa_Network/cards/ directory
# Record: ✅ Realm generated
```

### Step 2.2: Verify Generated Structure
```bash
cd /workspaces/The_Awa_Network/cards

# Check key files exist
ls -la .env mauri/realm_lock.json te_ao/ te_hau/

# Verify .env contents
cat .env
# Expected: REALM_ID=cards, REALM_NAME="Cards Realm", TE_PO_URL=https://..., BEARER_KEY=...

# Record: ✅ Realm structure valid
```

### Step 2.3: Start Cards Frontend
```bash
cd /workspaces/The_Awa_Network/cards/te_ao

npm install
npm run dev

# Expected: Vite dev server starting on http://localhost:5174
# Record: ✅ Frontend accessible
```

### Step 2.4: Test Frontend → Backend Call
```bash
# From browser console (http://localhost:5174) or via curl:

curl -X POST https://te-po-kitenga-backend.onrender.com/intake/summarize \
  -H "Authorization: Bearer $(cat /workspaces/The_Awa_Network/cards/.env | grep BEARER_KEY | cut -d= -f2)" \
  -H "Content-Type: application/json" \
  -d '{"text": "Sample card for testing", "mode": "research"}'

# Expected: Valid summary response with id, summary text, saved: true
# Record: ✅ Cards realm → Te Pò backend working
```

### Step 2.5: Verify Token Isolation
```bash
# Check token is unique from main realm
CARDS_TOKEN=$(grep BEARER_KEY /workspaces/The_Awa_Network/cards/.env | cut -d= -f2)
MAIN_TOKEN=$(grep BEARER_KEY /workspaces/The_Awa_Network/mauri/global_env.json | cut -d= -f2 || echo "none")

# Tokens should be different
# Record: ✅ Each realm has unique token
```

**Phase 2 Sign-Off:** ✅ Multi-project architecture verified

---

## 🔐 Phase 3: Auth Enhancement (2-3 hours)

### Step 3.1: Update Render Environment Variables
```bash
# In Render dashboard, update render.yaml or service settings
# Add these environment variables:

ALLOW_MULTIPLE_REALMS=true
REALM_BEARER_KEYS=cards:$(grep BEARER_KEY /workspaces/The_Awa_Network/cards/.env | cut -d= -f2)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Record: ✅ Environment variables updated in Render
```

### Step 3.2: (Optional) Enhance BearerAuthMiddleware
```bash
# File: te_po/utils/middleware/auth_middleware.py
# Add realm_id extraction from token (if using JWT)
# Update logging to include realm context

# Test locally:
python -m uvicorn core.main:app --port 8010

# Verify middleware logs include realm info
# Record: ✅ Middleware enhanced
```

### Step 3.3: (Optional) Implement Rate Limiting
```bash
# File: te_po/utils/middleware/rate_limit.py
# Add per-realm rate limiting

# Test:
# Make 61 requests within 1 minute
# Verify 61st request returns 429 Too Many Requests

# Record: ✅ Rate limiting functional
```

**Phase 3 Sign-Off:** ✅ Authentication enhanced

---

## 📊 Phase 4: Monitoring (1-2 hours)

### Step 4.1: Enable Metrics Endpoint
```bash
# Verify metrics are accessible
curl http://localhost:8010/metrics

# Expected: Prometheus format output
# Record: ✅ Metrics endpoint active
```

### Step 4.2: Check Audit Logging
```bash
# Make a test request
curl -X POST http://localhost:8010/intake/summarize \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"text": "test", "mode": "research"}'

# Verify logged to:
# - Supabase kitenga_audit_logs (if configured)
# - Local storage (if offline)

# Record: ✅ Audit logging functional
```

### Step 4.3: (Optional) Create Monitoring Dashboard
```bash
# If using Prometheus + Grafana:
# 1. Add scrape config: https://te-po-kitenga-backend.onrender.com/metrics
# 2. Create dashboard with:
#    - Request rate (total & per realm)
#    - Error rate by endpoint
#    - Response latency p50/p95/p99
#    - Vector search performance

# Record: ✅ Monitoring dashboard created
```

**Phase 4 Sign-Off:** ✅ Monitoring operational

---

## 📚 Phase 5: Documentation (2-3 hours)

### Step 5.1: Create Integration Guide
```bash
# Create: docs/EXTERNAL_PROJECT_INTEGRATION.md
# Include:
# - Quick start (3 steps)
# - Available endpoints (organized by category)
# - Authentication example
# - Error handling
# - Support contact

# Record: ✅ Integration guide created
```

### Step 5.2: Create cURL Examples
```bash
# Create: docs/CURL_EXAMPLES.md
# Include examples for:
# - GET /status
# - POST /intake/summarize
# - POST /intake/ocr
# - GET /memory/search
# - POST /chat/save-session
# - GET /reo/translate

# Record: ✅ cURL examples documented
```

### Step 5.3: Create API Reference
```bash
# Create: docs/API_REFERENCE.md
# Include for each endpoint:
# - HTTP method
# - Path
# - Required headers
# - Request body schema
# - Response schema
# - Status codes
# - Example

# Record: ✅ API reference complete
```

**Phase 5 Sign-Off:** ✅ Documentation complete

---

## 🚀 Phase 6: Deploy More Projects (2-3 hours)

### Step 6.1: Generate Translator Realm
```bash
cd /workspaces/The_Awa_Network

python te_hau/scripts/generate_realm.py \
  --realm-id "translator" \
  --realm-name "Te Reo Translator" \
  --te-po-url "https://te-po-kitenga-backend.onrender.com"

# Record: ✅ Translator realm generated
```

### Step 6.2: Test Translator Realm
```bash
cd /workspaces/The_Awa_Network/translator/te_ao
npm install
npm run dev

# Test API call to Te Pō
curl -X GET "https://te-po-kitenga-backend.onrender.com/reo/translate?text=hello&target=mi" \
  -H "Authorization: Bearer $(grep BEARER_KEY /workspaces/The_Awa_Network/translator/.env | cut -d= -f2)"

# Expected: Valid translation response
# Record: ✅ Translator realm working
```

### Step 6.3: Generate Research Realm
```bash
cd /workspaces/The_Awa_Network

python te_hau/scripts/generate_realm.py \
  --realm-id "research" \
  --realm-name "Research Assistant" \
  --te-po-url "https://te-po-kitenga-backend.onrender.com"

# Record: ✅ Research realm generated
```

### Step 6.4: Test Research Realm
```bash
cd /workspaces/The_Awa_Network/research/te_ao
npm install
npm run dev

# Test API call
curl -X POST "https://te-po-kitenga-backend.onrender.com/research/analyze" \
  -H "Authorization: Bearer $(grep BEARER_KEY /workspaces/The_Awa_Network/research/.env | cut -d= -f2)" \
  -H "Content-Type: application/json" \
  -d '{"document": "Sample research content", "analysis_type": "comprehensive"}'

# Expected: Valid analysis response
# Record: ✅ Research realm working
```

### Step 6.5: Verify All Projects Running
```bash
# Terminal 1: Main Te Ao
cd /workspaces/The_Awa_Network/te_ao && npm run dev
# http://localhost:5173

# Terminal 2: Cards Realm
cd /workspaces/The_Awa_Network/cards/te_ao && npm run dev
# http://localhost:5174

# Terminal 3: Translator Realm
cd /workspaces/The_Awa_Network/translator/te_ao && npm run dev
# http://localhost:5175

# Terminal 4: Research Realm
cd /workspaces/The_Awa_Network/research/te_ao && npm run dev
# http://localhost:5176

# Terminal 5: Te Pò Backend
cd /workspaces/The_Awa_Network/te_po
python -m uvicorn core.main:app --port 8010

# Verify all 4 frontends load without CORS errors
# Record: ✅ All 4 realms running, 1 backend
```

**Phase 6 Sign-Off:** ✅ Multiple projects deployed

---

## ✅ Testing Checklist

### Functionality Tests
- [ ] Te Pò starts without errors
- [ ] `/status` endpoint returns 200
- [ ] `/heartbeat` endpoint responds
- [ ] Bearer token validation works
- [ ] CORS allows cross-origin requests
- [ ] Realms can call Te Pò backend
- [ ] Each realm gets unique response
- [ ] Summary includes cultural alignment
- [ ] Memory search returns results
- [ ] Chat sessions save correctly

### Multi-Project Tests
- [ ] 3+ realms can call same Te Pò
- [ ] Each realm uses unique token
- [ ] No data leakage between realms
- [ ] Audit logs track requests per realm
- [ ] Rate limiting works (if enabled)
- [ ] Metrics show request distribution

### Production Tests
- [ ] Render endpoint is accessible
- [ ] All environment variables are set
- [ ] Supabase connection is active
- [ ] OpenAI API calls succeed
- [ ] Health checks passing
- [ ] No CORS errors from frontend
- [ ] Bearer token properly validated

---

## 🐛 Troubleshooting Reference

### Issue: Backend won't start
```
Solution:
1. Check Python version: python --version (need 3.12+)
2. Install requirements: pip install -r requirements.txt
3. Check .env file exists: ls te_po/.env
4. Check port 8010 is available: lsof -i :8010
```

### Issue: 401 Unauthorized
```
Solution:
1. Check Authorization header format: "Bearer <token>"
2. Verify token in .env file
3. Ensure token is not expired
4. Check token matches in mauri/realm_lock.json
```

### Issue: CORS error
```
Solution:
1. Verify CORSMiddleware in core/main.py
2. Check allow_origins=["*"]
3. Clear browser cache
4. Test with curl (ignores CORS)
```

### Issue: OpenAI API fails
```
Solution:
1. Check OPENAI_API_KEY is set
2. Verify key has proper permissions
3. Check key quota isn't exceeded
4. Try with gpt-4o-mini (lower cost)
```

---

## 📈 Rollout Timeline

| Phase | Estimated Time | Actual Time | Status |
|-------|-----------------|------------|--------|
| 1. Verification | 1-2 hours | [ ] | [ ] |
| 2. First Project | 1-2 hours | [ ] | [ ] |
| 3. Auth Enhancement | 2-3 hours | [ ] | [ ] |
| 4. Monitoring | 1-2 hours | [ ] | [ ] |
| 5. Documentation | 2-3 hours | [ ] | [ ] |
| 6. Deploy More | 2-3 hours | [ ] | [ ] |
| **Total** | **9-15 hours** | [ ] | [ ] |

---

## 🎯 Success Criteria

Mark as complete when:

- [ ] Phase 1: Verification complete, all endpoints responding
- [ ] Phase 2: Cards realm created, calling Te Pò backend successfully
- [ ] Phase 3: Auth enhanced, rate limiting active
- [ ] Phase 4: Monitoring dashboard accessible, audit logs working
- [ ] Phase 5: Documentation complete and comprehensive
- [ ] Phase 6: 3+ realms deployed and tested
- [ ] All tests passing (functionality, multi-project, production)
- [ ] Zero critical issues in Render logs

**Final Status:** ✅ Ready for External Team Onboarding

---

## 📞 Support

- **Questions about architecture?** → See TE_PO_STANDALONE_SCAN.md
- **How to set up?** → See TE_PO_MULTI_PROJECT_SETUP.md
- **Need endpoint docs?** → See TE_PO_ARCHITECTURE_QUICKREF.md
- **Visual diagrams?** → See TE_PO_VISUAL_ARCHITECTURE.md
- **Executive overview?** → See TE_PO_EXECUTIVE_SUMMARY.md

---

**Next Step:** Start Phase 1 and check off items as completed!

**When Complete:** Report results to engineering team  
**After Approval:** Begin Phase 2

---

**Prepared by:** GitHub Copilot  
**Date:** 15 Tīhema 2025  
**Status:** ✅ Ready to Begin
