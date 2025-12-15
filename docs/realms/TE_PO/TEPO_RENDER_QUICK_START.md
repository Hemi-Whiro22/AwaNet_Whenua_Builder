# Te Pō Render Deployment - Quick Reference

## ✅ Files Updated

| File | Change | Purpose |
|------|--------|---------|
| `/render.yaml` | `rootDir: te_po` | Only deploy te_po, ignore other realms |
| `/te_po/Dockerfile` | Created | Build te_po as standalone Docker image |

---

## 🎯 How It Works (Simple Version)

```
You: git push origin main
     ↓
GitHub notifies Render
     ↓
Render reads render.yaml
     ↓
Sees rootDir: te_po
     ↓
Builds ONLY te_po/
     ↓
Deploys FastAPI backend
     ↓
Frontend projects call: https://te-po-kitenga-backend.onrender.com
```

**Key:** The entire monorepo is pushed, but only te_po is deployed. 🎯

---

## 🚀 Quick Start

### 1. Commit Changes
```bash
cd /workspaces/The_Awa_Network
git add render.yaml te_po/Dockerfile
git commit -m "Configure te_po as standalone Render backend"
git push origin main
```

### 2. Set Up on Render
1. Go to https://dashboard.render.com
2. New Web Service → GitHub repository
3. **Name:** `te-po-kitenga-backend`
4. **Root Directory:** `te_po`
5. **Dockerfile:** `Dockerfile`
6. Add environment variables (see below)
7. Deploy!

### 3. Environment Variables on Render
```
OPENAI_API_KEY            sk-...
SUPABASE_URL              https://...
SUPABASE_SERVICE_ROLE_KEY eyJ...
DATABASE_URL              postgresql://...
REDIS_URL                 redis://... (optional)
LANG                      mi_NZ.UTF-8
LC_ALL                    mi_NZ.UTF-8
```

### 4. Test It
```bash
# Should return status
curl https://te-po-kitenga-backend.onrender.com/heartbeat

# Should show available routes
curl https://te-po-kitenga-backend.onrender.com/docs
```

---

## 🔌 Use in Frontend Projects

```javascript
// Replace this:
const API_URL = "http://localhost:10000"

// With this:
const API_URL = "https://te-po-kitenga-backend.onrender.com"

// Or use environment variable:
const API_URL = process.env.VITE_API_URL || "https://te-po-kitenga-backend.onrender.com"
```

---

## 📊 Deployment Architecture

```
┌─────────────────────────────────────────┐
│    GitHub (Full Monorepo)                │
│  - te_po/                                │
│  - te_ao/                                │
│  - te_hau/                               │
│  - docs/                                 │
│  - render.yaml ← specifies te_po only    │
└─────────────────────────────────────────┘
           ↓
      [Render Webhook]
           ↓
┌─────────────────────────────────────────┐
│    Render Build Process                  │
│  1. Clone repo                           │
│  2. Read render.yaml                     │
│  3. See: rootDir: te_po                  │
│  4. cd te_po/                            │
│  5. Build Dockerfile                     │
│  6. Start uvicorn                        │
└─────────────────────────────────────────┘
           ↓
┌──────────────────────────────────────────────────┐
│  Production Backend (Render)                      │
│  https://te-po-kitenga-backend.onrender.com      │
│  ✓ 23 API routes                                 │
│  ✓ Health checks every 30s                       │
│  ✓ Auto-restart on failure                       │
│  ✓ Logs available in Render Dashboard            │
└──────────────────────────────────────────────────┘
           ↓
┌──────────────────────────────────────────────────┐
│  All Frontend Projects Call Same Backend          │
│  ┌──────────────┐  ┌──────────────┐              │
│  │   Te Ao      │  │  Other Apps  │              │
│  │  (Studio)    │  │  (External)  │              │
│  └──────────────┘  └──────────────┘              │
│         ↓                 ↓                       │
│  All use same API_URL = te-po backend ✓          │
└──────────────────────────────────────────────────┘
```

---

## 🛡️ Key Features

✅ **Selective Deployment**
- Entire monorepo in GitHub
- Only te_po deployed to Render
- Other directories ignored

✅ **Centralized Backend**
- Single source of truth
- All frontends use same URL
- Easy to update (one deploy)

✅ **Production Ready**
- Health checks
- Auto-restart
- Load balancing (Pro plan)
- HTTPS by default

✅ **Continuous Deployment**
- Push → Render builds → Deploy
- Zero downtime
- Automatic for every commit

✅ **Easy Scaling**
- Upgrade plan for more instances
- Render handles load balancing
- Horizontal scaling built-in

---

## 🔍 Verification

After Render deployment:

```bash
# Check if online
curl https://te-po-kitenga-backend.onrender.com/heartbeat
# Response: {"status": "alive", "timestamp": "2025-01-15T...Z"}

# View available API docs
open https://te-po-kitenga-backend.onrender.com/docs

# Check root status
curl https://te-po-kitenga-backend.onrender.com/
# Response: {"status": "online", "kaitiaki": "Kitenga Whiro", "message": "Kia ora..."}
```

---

## 📚 What's Deployed

The following routes are now live on your Render backend:

```
POST /intake/ocr               - Extract text from PDFs/images
POST /intake/summarize         - Create AI summaries
POST /reo/translate            - Translate to/from te reo Māori
POST /reo/pronunciation        - Get pronunciation audio
POST /vector/embed             - Create embeddings
GET  /vector/search            - Search vectors
POST /memory/store             - Save to long-term memory
GET  /memory/search            - Retrieve from memory
POST /chat/save-session        - Save chat conversations
POST /assistant/create-thread  - Create AI assistant thread
GET  /documents/list           - List documents
POST /pipeline/run             - Execute processing pipelines
... and 11 more routes
```

See full list at: `https://te-po-kitenga-backend.onrender.com/docs`

---

## ⚠️ Common Issues

| Issue | Solution |
|-------|----------|
| Build fails | Check Render logs for missing deps |
| 404 on `/heartbeat` | Ensure Dockerfile is correct |
| Frontend can't connect | Check CORS (should be `*` for now) |
| Auth errors | Set `HUMAN_BEARER_KEY` in env vars |
| Locale errors | Ensure `LANG=mi_NZ.UTF-8` is set |

---

## 🎯 Next Steps

1. ✅ Commit the changes above
2. ✅ Push to GitHub
3. ✅ Create Render service with `rootDir: te_po`
4. ✅ Set environment variables
5. ✅ Deploy
6. ✅ Update frontend projects to use new URL
7. ✅ Monitor logs in Render Dashboard

---

**You're ready to deploy!** 🚀

Kia ora! 🌿
