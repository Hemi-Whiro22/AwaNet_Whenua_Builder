# Te Pō Standalone FastAPI Backend - Render Deployment Guide

## 🎯 Overview

Te Pō is now configured to deploy as a **standalone FastAPI backend** on Render. This enables:

- ✅ **Monorepo with selective deployment** - Push entire codebase, only te_po deploys
- ✅ **All frontend projects call the same backend** - Centralized intelligence engine
- ✅ **Awa Network becomes the epicenter** - Single source of truth for all services
- ✅ **Production-ready scaling** - Load balanced, health checked, auto-healing

---

## 🏗️ Architecture: How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub Repository                              │
│  (Push includes everything: te_po, te_ao, te_hau, docs, etc)   │
└─────────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────────────┐
                    │  Render.yaml  │ ← NEW: Specifies rootDir: te_po
                    └───────────────┘
                            ↓
    ┌───────────────────────────────────────────────────────────┐
    │ Render reads rootDir: te_po                                │
    │ Only builds & deploys te_po/ directory                     │
    │ Ignores te_ao, te_hau, docs, scripts, etc                  │
    └───────────────────────────────────────────────────────────┘
                            ↓
         ┌──────────────────────────────────────────┐
         │  Te Pō FastAPI Backend on Render         │
         │  https://te-po-kitenga-backend.onrender.com │
         │  ✓ All 23 routes active                  │
         │  ✓ Health checks running                 │
         │  ✓ Auto-scaling enabled                  │
         └──────────────────────────────────────────┘
                            ↓
    ┌───────────────────────────────────────────────────────────┐
    │          Frontend Projects (Any Tech Stack)                 │
    │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
    │  │   Te Ao      │  │   React App  │  │   Vue App    │    │
    │  │  (Studio)    │  │  (Portfolio) │  │  (Iwi Site)  │    │
    │  └──────────────┘  └──────────────┘  └──────────────┘    │
    │         ↓                ↓                   ↓             │
    │    VITE_API_URL      API_URL            API_ENDPOINT      │
    │    All point to: te-po-kitenga-backend.onrender.com       │
    └───────────────────────────────────────────────────────────┘
```

---

## 📋 What Changed

### 1. **Root-Level `render.yaml` (Updated)**
```yaml
rootDir: te_po           # ← KEY CHANGE: Only deploy te_po
dockerfilePath: Dockerfile
startCommand: uvicorn te_po.core.main:app --host 0.0.0.0 --port 10000
```

### 2. **Te Pō `Dockerfile` (New)**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 10000
CMD ["uvicorn", "te_po.core.main:app", "--host", "0.0.0.0", "--port", "10000"]
```

### 3. **No changes needed to te_po code**
- Existing FastAPI app works as-is
- All 23 routes active: `/intake`, `/ocr`, `/chat`, `/reo`, `/vector`, etc.

---

## 🚀 Deployment Steps

### Step 1: Ensure Git is Clean
```bash
cd /workspaces/The_Awa_Network
git status
git add .
git commit -m "Configure te_po as standalone Render backend"
```

### Step 2: Push to GitHub
```bash
git push origin main
```

### Step 3: Configure Render Service

1. **Go to Render Dashboard** → https://dashboard.render.com
2. **Create New Web Service**
3. **Connect GitHub Repository**
   - Select your repo (The_Awa_Network)
   - Branch: `main`
4. **Configure Service Settings**
   - **Name:** `te-po-kitenga-backend`
   - **Environment:** `Docker`
   - **Root Directory:** `te_po` ← IMPORTANT
   - **Dockerfile Path:** `Dockerfile`
   - **Plan:** `Starter` or `Pro` depending on load
   - **Port:** `10000`

5. **Add Environment Variables**
   ```
   OPENAI_API_KEY=sk-...
   SUPABASE_URL=https://...
   SUPABASE_SERVICE_ROLE_KEY=eyJ...
   DATABASE_URL=postgresql://...
   REDIS_URL=redis://... (optional)
   LANG=mi_NZ.UTF-8
   LC_ALL=mi_NZ.UTF-8
   ```

6. **Deploy!**
   - Render will only build te_po/
   - Other directories ignored
   - Service starts at: `https://te-po-kitenga-backend.onrender.com`

---

## 📍 Expected Endpoints

Once deployed, these endpoints will be live:

```
Root Status
GET https://te-po-kitenga-backend.onrender.com/
GET https://te-po-kitenga-backend.onrender.com/heartbeat

OCR & Intake
POST /intake/ocr
POST /intake/summarize

Translation & Language
POST /reo/translate
POST /reo/pronunciation

Vector & Memory
POST /vector/embed
GET /memory/search
POST /memory/store

Chat & Assistants
POST /chat/save-session
POST /assistant/create-thread

...and 17 more routes (see te_po/core/main.py)
```

Test endpoint health:
```bash
curl https://te-po-kitenga-backend.onrender.com/heartbeat
```

---

## 🔌 Connecting Frontend Projects

### For Te Ao (Studio)
```javascript
// te_ao/src/App.jsx or .env
const API_URL = "https://te-po-kitenga-backend.onrender.com"

// Or via environment variable
const API_URL = import.meta.env.VITE_API_URL || "https://te-po-kitenga-backend.onrender.com"
```

### For Other React/Vue/Next Projects
```javascript
// .env.production
REACT_APP_API_URL=https://te-po-kitenga-backend.onrender.com
VITE_API_URL=https://te-po-kitenga-backend.onrender.com
NEXT_PUBLIC_API_URL=https://te-po-kitenga-backend.onrender.com
```

### For Python Projects
```python
import os
TE_PO_URL = os.getenv("TE_PO_URL", "https://te-po-kitenga-backend.onrender.com")

# Use in requests
response = requests.post(f"{TE_PO_URL}/intake/summarize", json=payload)
```

---

## ✅ Verification Checklist

After deployment to Render:

- [ ] Service builds successfully (check Render build logs)
- [ ] Health check endpoint returns 200
  ```bash
  curl https://te-po-kitenga-backend.onrender.com/heartbeat
  ```
- [ ] Root endpoint responds with Kitenga status
  ```bash
  curl https://te-po-kitenga-backend.onrender.com/
  ```
- [ ] OCR route is accessible
  ```bash
  curl https://te-po-kitenga-backend.onrender.com/docs
  ```
- [ ] OpenAI integration works (test with a small request)
- [ ] Database connections are healthy
- [ ] Frontend projects can reach the API

---

## 🛡️ Production Considerations

### Auto-Healing
Render automatically restarts services if health checks fail. The health check is:
```
GET /heartbeat every 30 seconds
```

### Scaling
- **Starter Plan:** 1 instance (sufficient for dev/testing)
- **Pro Plan:** Auto-scaling (recommended for production)
  - Add more instances as traffic increases
  - Load balanced automatically

### Monitoring
Render provides:
- Build logs
- Runtime logs
- CPU/Memory usage
- Deployment history

Check logs in Render Dashboard → Service → Logs

### Security
- Bearer token middleware active (all routes)
- CORS configured to allow frontend requests
- Environment variables stored securely in Render
- Render provides HTTPS by default

---

## 🔄 Continuous Deployment

**How updates work:**

1. **Developer pushes to GitHub**
   ```bash
   git push origin main
   ```

2. **GitHub webhook triggers Render**
   - Render detects new commit
   - Reads `render.yaml`
   - Sees `rootDir: te_po`
   - Builds only te_po Dockerfile
   - Deploys updated backend

3. **Zero downtime deployment**
   - Old instance continues serving
   - New instance spins up
   - Health checks pass
   - Requests switch to new instance
   - Old instance terminates

4. **Frontends automatically use new version**
   - All frontend projects call the same URL
   - No need to redeploy frontends
   - All use latest backend code

---

## 🎯 Multi-Service Deployment (Optional)

To deploy both te_po AND te_ao from the same git push:

**In render.yaml:**
```yaml
version: 1
services:
  # Backend
  - type: web
    name: te-po-kitenga-backend
    rootDir: te_po
    dockerfilePath: Dockerfile
    # ... rest of config
  
  # Frontend
  - type: web
    name: te-ao-studio-frontend
    rootDir: te_ao
    dockerfilePath: Dockerfile
    # ... rest of config
```

Then:
- `git push` → Render builds both
- `https://te-po-kitenga-backend.onrender.com` (backend)
- `https://te-ao-studio-frontend.onrender.com` (frontend)
- Frontend's VITE_API_URL points to backend URL

---

## 🐛 Troubleshooting

### Build Fails
**Check:** Render build logs
- Missing dependencies in requirements.txt?
- Python version mismatch?
- Docker build context wrong?

### Service crashes on startup
**Check:** Runtime logs
- OpenAI API key missing?
- Database URL invalid?
- Locale issues?

### Health check fails
**Check:** 
- Is port 10000 exposed?
- Is `/heartbeat` route working?
  ```bash
  curl https://te-po-kitenga-backend.onrender.com/heartbeat
  ```

### Frontends can't reach backend
**Check:**
- CORS is configured correctly (should be `allow_origins=["*"]`)
- Frontend using correct API URL
- Backend is actually deployed and running

---

## 📚 References

- [Render Documentation: Services](https://render.com/docs/deploy-an-api)
- [render.yaml Specification](https://render.com/docs/infrastructure-as-code)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Uvicorn Configuration](https://www.uvicorn.org/settings/)

---

## 🎉 You're All Set!

Your te_po backend is now configured for production deployment. All frontend projects can call it as the centralized intelligence engine for the Awa Network.

**Next Steps:**
1. Push this commit to GitHub
2. Create Render service (or auto-triggers if webhook configured)
3. Set environment variables in Render
4. Deploy!

Questions? Check the logs in Render Dashboard or review the Dockerfile and render.yaml above.

Kia ora! 🌿
