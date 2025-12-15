# Render Configuration for Pipeline Job Tracking

**Goal:** Deploy te_po backend with PostgreSQL job tracking + RQ workers to Render

---

## Architecture on Render

```
┌─────────────────┐
│  Git Push main  │
└────────┬────────┘
         │
         ▼
    ┌─────────────────────────────────────────┐
    │        Render Services                  │
    ├─────────────────────────────────────────┤
    │                                         │
    │  Web (te-po-backend)                   │
    │    - uvicorn --workers 4                │
    │    - port 10000                         │
    │    - reads: DATABASE_URL, REDIS_URL     │
    │                                         │
    │  Background Workers (RQ)                │
    │    - rq worker urgent --concurrency 2   │
    │    - rq worker default --concurrency 4  │
    │    - rq worker slow --concurrency 1     │
    │    - reads: DATABASE_URL, REDIS_URL     │
    │                                         │
    │  Add-ons:                               │
    │    - PostgreSQL (database)              │
    │    - Redis (queue backend)              │
    │                                         │
    └─────────────────────────────────────────┘
         ▲              ▲              ▲
         │              │              │
    DATABASE_URL   REDIS_URL     (both env vars)
```

---

## Step 1: Create Database

**Option A: Render PostgreSQL Add-on (Easiest)**

In Render dashboard:
1. Create new service → PostgreSQL
2. Instance: Starter (free)
3. Name: `kitenga-postgres`
4. Database: `tepo_db`
5. Copy connection string: `DATABASE_URL`

**Option B: External Database (Supabase, Railway, etc.)**

Use existing PostgreSQL with connection string.

---

## Step 2: Create Redis Database

**Option A: Render Redis Add-on**

1. Create new service → Redis
2. Instance: Starter (free)
3. Name: `kitenga-redis`
4. Copy connection string: `REDIS_URL`

**Option B: Use existing Redis**

Upstash, Railway, or local container — any standard Redis.

---

## Step 3: Update `render.yaml`

Replace entire render.yaml with:

```yaml
# Render Deployment Configuration for Te Pō Backend + RQ Workers
# Date: 15 Tīhema 2025

services:
  # ─────────────────────────────────────────────────────
  # WEB SERVICE: FastAPI Backend
  # ─────────────────────────────────────────────────────
  - type: "web"
    name: "te-po-kitenga-backend"
    runtime: "python"
    pythonVersion: "3.12"
    
    region: "nzeast"  # New Zealand (change if needed)
    plan: "standard"
    
    rootDir: "te_po"
    dockerfilePath: "Dockerfile"
    
    buildCommand: |
      pip install --upgrade pip setuptools wheel && \
      pip install -r requirements.txt && \
      python -c "
        from te_po.db import db_execute
        try:
          with open('te_po/db/migrations_001_pipeline_jobs.sql') as f:
            sql = f.read()
            for stmt in sql.split(';'):
              if stmt.strip():
                db_execute(stmt)
          print('✓ Database schema initialized')
        except Exception as e:
          print(f'Warning: {e}')
      "
    
    startCommand: |
      uvicorn te_po.core.main:app \
        --host 0.0.0.0 \
        --port 10000 \
        --workers 4
    
    healthCheckPath: "/heartbeat"
    healthCheckTimeout: 10
    
    envVars:
      # ─── Database & Queue ───
      - key: "DATABASE_URL"
        fromDatabase:
          name: "kitenga-postgres"
          property: "connectionString"
      
      - key: "REDIS_URL"
        fromService:
          name: "kitenga-redis"
          type: "redis"
          property: "connectionString"
      
      # ─── OpenAI ───
      - key: "OPENAI_API_KEY"
        sync: false  # Set manually in dashboard
      
      # ─── Supabase (optional, for backward compat) ───
      - key: "SUPABASE_URL"
        sync: false
      
      - key: "SUPABASE_SERVICE_ROLE_KEY"
        sync: false
      
      # ─── Locale (critical for Māori text) ───
      - key: "LANG"
        value: "mi_NZ.UTF-8"
      
      - key: "LC_ALL"
        value: "mi_NZ.UTF-8"
      
      - key: "PYTHONIOENCODING"
        value: "utf-8"
      
      # ─── Application ───
      - key: "TE_PO_PORT"
        value: "10000"
      
      - key: "TE_PO_HOST"
        value: "0.0.0.0"

  # ─────────────────────────────────────────────────────
  # BACKGROUND WORKER: RQ Urgent Queue
  # ─────────────────────────────────────────────────────
  - type: "background"
    name: "rq-worker-urgent"
    runtime: "python"
    pythonVersion: "3.12"
    
    rootDir: "te_po"
    
    buildCommand: |
      pip install --upgrade pip setuptools wheel && \
      pip install -r requirements.txt
    
    startCommand: |
      rq worker urgent \
        --concurrency 2 \
        --log-level INFO
    
    envVars:
      - key: "DATABASE_URL"
        fromDatabase:
          name: "kitenga-postgres"
          property: "connectionString"
      
      - key: "REDIS_URL"
        fromService:
          name: "kitenga-redis"
          type: "redis"
          property: "connectionString"
      
      - key: "OPENAI_API_KEY"
        sync: false
      
      - key: "LANG"
        value: "mi_NZ.UTF-8"
      
      - key: "LC_ALL"
        value: "mi_NZ.UTF-8"
      
      - key: "PYTHONIOENCODING"
        value: "utf-8"

  # ─────────────────────────────────────────────────────
  # BACKGROUND WORKER: RQ Default Queue
  # ─────────────────────────────────────────────────────
  - type: "background"
    name: "rq-worker-default"
    runtime: "python"
    pythonVersion: "3.12"
    
    rootDir: "te_po"
    
    buildCommand: |
      pip install --upgrade pip setuptools wheel && \
      pip install -r requirements.txt
    
    startCommand: |
      rq worker default \
        --concurrency 4 \
        --log-level INFO
    
    envVars:
      - key: "DATABASE_URL"
        fromDatabase:
          name: "kitenga-postgres"
          property: "connectionString"
      
      - key: "REDIS_URL"
        fromService:
          name: "kitenga-redis"
          type: "redis"
          property: "connectionString"
      
      - key: "OPENAI_API_KEY"
        sync: false
      
      - key: "LANG"
        value: "mi_NZ.UTF-8"
      
      - key: "LC_ALL"
        value: "mi_NZ.UTF-8"
      
      - key: "PYTHONIOENCODING"
        value: "utf-8"

  # ─────────────────────────────────────────────────────
  # BACKGROUND WORKER: RQ Slow Queue
  # ─────────────────────────────────────────────────────
  - type: "background"
    name: "rq-worker-slow"
    runtime: "python"
    pythonVersion: "3.12"
    
    rootDir: "te_po"
    
    buildCommand: |
      pip install --upgrade pip setuptools wheel && \
      pip install -r requirements.txt
    
    startCommand: |
      rq worker slow \
        --concurrency 1 \
        --log-level INFO
    
    envVars:
      - key: "DATABASE_URL"
        fromDatabase:
          name: "kitenga-postgres"
          property: "connectionString"
      
      - key: "REDIS_URL"
        fromService:
          name: "kitenga-redis"
          type: "redis"
          property: "connectionString"
      
      - key: "OPENAI_API_KEY"
        sync: false
      
      - key: "LANG"
        value: "mi_NZ.UTF-8"
      
      - key: "LC_ALL"
        value: "mi_NZ.UTF-8"
      
      - key: "PYTHONIOENCODING"
        value: "utf-8"

  # ─────────────────────────────────────────────────────
  # PostgreSQL Database Add-on
  # ─────────────────────────────────────────────────────
  - type: "pserv"  # PostgreSQL service
    name: "kitenga-postgres"
    ipAllowList: []  # Allow all (internal only)

  # ─────────────────────────────────────────────────────
  # Redis Database Add-on
  # ─────────────────────────────────────────────────────
  - type: "redis"
    name: "kitenga-redis"
    ipAllowList: []  # Allow all (internal only)

```

---

## Step 4: Commit and Push

```bash
cd /workspaces/The_Awa_Network

git add render.yaml te_po/db/ te_po/pipeline/ te_po/routes/pipeline.py docs/

git commit -m "Add PostgreSQL job tracking + RQ workers to Render deployment

- New: te_po/db/postgres.py (connection pooling)
- New: te_po/pipeline/job_tracking.py (tracking decorator)
- New: te_po/db/migrations_001_pipeline_jobs.sql (schema)
- Updated: te_po/routes/pipeline.py (enqueue writes to PostgreSQL)
- Updated: render.yaml (web + 3 background workers + databases)
- Docs: PIPELINE_JOB_TRACKING_POSTGRES.md, QUICK_START.md

RQ (Redis) queue unchanged; PostgreSQL provides durable audit trail."

git push origin main
```

---

## Step 5: Deploy to Render

1. **Go to Render dashboard:** https://dashboard.render.com
2. **Click "New +"** → "Blueprint from Git"
3. **Connect your GitHub repo** (The_Awa_Network)
4. **Render reads render.yaml automatically**
5. **Review services:**
   - te-po-kitenga-backend (Web)
   - rq-worker-urgent (Background)
   - rq-worker-default (Background)
   - rq-worker-slow (Background)
   - kitenga-postgres (Database)
   - kitenga-redis (Redis)
6. **Click "Deploy" and wait**

**First deploy takes 5-10 minutes.**

---

## Step 6: Manual Environment Variables

In Render dashboard, for **each service** (web + 3 workers), add secret variables:

| Variable | Value |
|----------|-------|
| `OPENAI_API_KEY` | Your OpenAI key |
| `SUPABASE_URL` | (optional) |
| `SUPABASE_SERVICE_ROLE_KEY` | (optional) |
| `PIPELINE_TOKEN` | (if using token auth) |

---

## Step 7: Verify Deployment

### Check backend is online

```bash
curl https://te-po-kitenga-backend.onrender.com/heartbeat
```

Expected: `{"status":"alive","timestamp":"..."}`

### Enqueue a test job

```bash
curl -X POST https://te-po-kitenga-backend.onrender.com/pipeline/enqueue \
  -F "file=@test.pdf" \
  -H "X-Realm: test"
```

Expected: `{"job_id":"uuid","queue":"default","realm":"test","status":"queued"}`

### Check job status

```bash
JOB_ID="..."  # From enqueue response
curl https://te-po-kitenga-backend.onrender.com/pipeline/status/$JOB_ID
```

Watch it progress: queued → running → finished

### View dashboard

```bash
curl "https://te-po-kitenga-backend.onrender.com/pipeline/jobs/recent?limit=10"
```

---

## Troubleshooting Render Deployment

### Web service fails to start

**Check logs:** Render dashboard → te-po-kitenga-backend → Logs

Common issues:
- `ModuleNotFoundError: No module named 'psycopg'` — Ensure `psycopg[binary]` in requirements.txt
- `DATABASE_URL not set` — Check env vars linked to PostgreSQL service
- `REDIS_URL not set` — Check env vars linked to Redis service

### Workers can't process jobs

**Check logs:** Render dashboard → rq-worker-default → Logs

Common issues:
- `DATABASE_URL not set` — **Workers also need this!** Add env var to each background service
- `REDIS_URL not set` — **Workers also need this!**
- `ImportError: cannot import name 'db_execute'` — Restart worker after updating code

### Database migration fails

**Safe to ignore** — Table probably already exists from previous deployment.

Or manually run:
```bash
# Via Render PostgreSQL Shell
CREATE TABLE IF NOT EXISTS pipeline_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ...
);
```

---

## Costs

| Service | Pricing |
|---------|---------|
| Web (standard) | ~$12/month |
| Background workers (3×) | ~$12/month each = $36 |
| PostgreSQL (starter) | Free tier (suitable for dev) |
| Redis (starter) | Free tier (suitable for dev) |
| **Total** | ~$48/month |

**Optimize:**
- Use smaller web plan (free tier, slow)
- Reduce worker count if backlog permits
- Use shared Redis instead of Render managed

---

## Next Steps After Deploy

1. ✅ Frontend projects point to: `https://te-po-kitenga-backend.onrender.com`
2. ✅ Build dashboard UI using `/pipeline/jobs/recent` endpoint
3. ✅ Monitor job metrics in Render dashboard
4. ✅ Set up alerts for failed jobs
5. ✅ Archive old completed jobs periodically

---

**Questions?** See [PIPELINE_JOB_TRACKING_POSTGRES.md](PIPELINE_JOB_TRACKING_POSTGRES.md).

