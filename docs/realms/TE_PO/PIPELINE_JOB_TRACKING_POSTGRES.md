# Pipeline Job Tracking — PostgreSQL Integration

**Date:** 15 Tīhema 2025  
**Status:** Implementation Complete  
**Architecture:** Dual-track — RQ (Redis) for queuing + PostgreSQL for durable job state

---

## Overview

This implementation adds **durable job tracking in PostgreSQL** while keeping **RQ + Redis** as the queue backend. Jobs are:

1. **Inserted into PostgreSQL** when enqueued (status='queued', payload)
2. **Updated to status='running'** when worker starts (wrapped via decorator)
3. **Updated to status='finished' or 'failed'** when complete (with result or error)

The **Redis/RQ queue** remains unchanged — it handles job distribution, retries, and dead-letter queueing. **PostgreSQL** provides durable audit trail and queryable dashboard.

---

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /pipeline/enqueue
       │
       ▼
┌──────────────────┐         ┌─────────────────┐
│  FastAPI Route   │────────▶│  PostgreSQL     │
│  (enqueue_       │ INSERT  │  pipeline_jobs  │
│   pipeline)      │ (queued │  (id, queue,    │
└──────┬───────────┘         │   realm, ...)   │
       │                     └─────────────────┘
       │ .enqueue()
       ▼
┌────────────────────────┐  ┌──────────────────┐
│  Redis Queue (RQ)      │  │  RQ Job Metadata │
│  urgent/default/slow   │  │  (rq_job_id)     │
└────────┬───────────────┘  └──────────────────┘
         │
         │ Worker picks up
         ▼
┌────────────────────────┐
│  RQ Worker Process     │
│ @track_pipeline_job    │
│ process_document()     │
└────────┬───────────────┘
         │
         │ UPDATE status='running' + started_at
         ▼
┌─────────────────────────┐
│  Execute Pipeline       │
│  (clean/chunk/embed)    │
└────────┬────────────────┘
         │
         ├─ SUCCESS ──────▶ UPDATE status='finished' + result
         │
         └─ FAILURE ──────▶ UPDATE status='failed' + error + re-raise
                           (RQ handles retry/dead-letter)
         ▼
┌──────────────────┐
│  PostgreSQL      │
│  pipeline_jobs   │
│  (audit trail)   │
└──────────────────┘
```

---

## File Changes

### 1. **New: `te_po/db/postgres.py`**

Global connection pool + helper functions:

```python
from te_po.db import db_execute, db_fetchone, db_fetchall

# Execute INSERT/UPDATE/DELETE
db_execute(
    "INSERT INTO pipeline_jobs (id, status, queue) VALUES (%s, %s, %s)",
    (job_id, "queued", "default")
)

# Fetch single row
job = db_fetchone(
    "SELECT * FROM pipeline_jobs WHERE id = %s",
    (job_id,)
)

# Fetch multiple rows
jobs = db_fetchall(
    "SELECT * FROM pipeline_jobs WHERE status = %s ORDER BY created_at DESC LIMIT %s",
    ("running", 10)
)
```

**Features:**
- Lazy initialization from `DATABASE_URL` env var
- Auto-adds `?sslmode=require` for cloud databases (Supabase, Railway, etc.)
- Connection pooling (min=2, max=10)
- Safe parameter binding (prevents SQL injection)
- Graceful fallback if PostgreSQL unavailable

### 2. **New: `te_po/pipeline/job_tracking.py`**

Job tracking decorator + query helpers:

```python
@track_pipeline_job  # ← Wrap job functions
def process_document(file_path: str, job_id: str) -> dict:
    # On entry: UPDATE status='running' + started_at=now()
    # On success: UPDATE status='finished' + result
    # On failure: UPDATE status='failed' + error (then re-raise)
    ...
```

**Functions:**
- `@track_pipeline_job` — Decorator for job functions
- `get_job_status(job_id)` — Fetch single job from DB
- `get_recent_jobs(limit, realm, queue, status)` — Dashboard queries

### 3. **Updated: `te_po/routes/pipeline.py`**

**`POST /pipeline/enqueue` changes:**

```python
# Before: Returns {"job_id": uuid}
# After: Returns {
#   "job_id": uuid,      # PostgreSQL ID
#   "queue": "default",  # Queue name (urgent/default/slow)
#   "realm": "...",      # From X-Realm header (optional)
#   "status": "queued"
# }

# Usage:
curl -X POST http://localhost:10000/pipeline/enqueue \
  -F "file=@document.pdf" \
  -H "X-Realm: my-project"
```

**New endpoints:**

- **`GET /pipeline/status/{job_id}`** — Get job status (PostgreSQL-backed)
- **`GET /pipeline/jobs/recent?limit=50&realm=...&queue=...&status=...`** — Dashboard query

### 4. **New: `te_po/db/migrations_001_pipeline_jobs.sql`**

SQL schema:

```sql
CREATE TABLE pipeline_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rq_job_id TEXT UNIQUE,
    realm TEXT,
    queue TEXT NOT NULL DEFAULT 'default',
    status TEXT NOT NULL DEFAULT 'queued',
    payload JSONB,
    result JSONB,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ
);

-- Indexes for efficient queries
CREATE INDEX idx_pipeline_jobs_status ON pipeline_jobs(status);
CREATE INDEX idx_pipeline_jobs_realm_status ON pipeline_jobs(realm, status);
CREATE INDEX idx_pipeline_jobs_created_at ON pipeline_jobs(created_at DESC);
```

---

## Deployment

### Local Development

**1. Initialize PostgreSQL table:**

```bash
# Using psql directly
psql $DATABASE_URL < te_po/db/migrations_001_pipeline_jobs.sql

# OR using Python
python -c "
from te_po.db import db_execute
with open('te_po/db/migrations_001_pipeline_jobs.sql') as f:
    sql = f.read()
    for stmt in sql.split(';'):
        if stmt.strip():
            db_execute(stmt)
"
```

**2. Ensure `.env` has `DATABASE_URL`:**

```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/tepo_db
REDIS_URL=redis://localhost:6379
```

**3. Start everything:**

```bash
./run_dev.sh  # Starts Redis + RQ workers + Uvicorn
```

**4. Test enqueue + status:**

```bash
# Enqueue
curl -X POST http://localhost:8000/pipeline/enqueue \
  -F "file=@test.pdf" \
  -H "X-Realm: test-realm" \
  | jq .

# Check status
curl http://localhost:8000/pipeline/status/{job_id} | jq .

# Get recent jobs
curl "http://localhost:8000/pipeline/jobs/recent?limit=10&status=running" | jq .
```

---

### Render Deployment

**1. Create PostgreSQL database** (using Render Add-on or external Supabase/Railway):

```yaml
# Option A: Render PostgreSQL Add-on
databases:
  - name: "kitenga-postgres"
    version: "15"
    plan: "starter"
```

**2. Get connection string from database, set as environment variable:**

```bash
DATABASE_URL = postgresql://user:pass@kitenga-postgres.render.internal:5432/tepo_db
```

**3. Update `render.yaml` with `DATABASE_URL` for web and worker services:**

```yaml
services:
  - type: "web"
    name: "te-po-backend"
    runtime: "python"
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn te_po.core.main:app --host 0.0.0.0 --port 10000 --workers 4"
    envVars:
      - key: "DATABASE_URL"
        fromDatabase:
          name: "kitenga-postgres"
      - key: "REDIS_URL"
        sync: false
      - key: "OPENAI_API_KEY"
        sync: false
      # ... other env vars
  
  - type: "background"
    name: "rq-worker-default"
    runtime: "python"
    startCommand: "rq worker default --concurrency 4"
    envVars:
      - key: "DATABASE_URL"
        fromDatabase:
          name: "kitenga-postgres"
      - key: "REDIS_URL"
        sync: false
      # ... other env vars
```

**4. On first deploy, run migration:**

```bash
# Via Render shell or one-off job
python -c "
from te_po.db import db_execute
import sys
with open('te_po/db/migrations_001_pipeline_jobs.sql') as f:
    sql = f.read()
    for stmt in sql.split(';'):
        if stmt.strip():
            try:
                db_execute(stmt)
            except Exception as e:
                print(f'Error: {e}', file=sys.stderr)
                pass  # Table may already exist
"
```

---

## API Examples

### Enqueue a job

```bash
curl -X POST http://localhost:10000/pipeline/enqueue \
  -F "file=@document.pdf" \
  -H "X-Realm: finance-team"
```

**Response:**
```json
{
  "job_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "queue": "default",
  "realm": "finance-team",
  "status": "queued"
}
```

### Check job status

```bash
curl http://localhost:10000/pipeline/status/3fa85f64-5717-4562-b3fc-2c963f66afa6
```

**Response (while running):**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "running",
  "queue": "default",
  "realm": "finance-team",
  "started_at": "2025-01-15T10:23:45.123456Z",
  "created_at": "2025-01-15T10:23:42.456789Z",
  "payload": {"filename": "document.pdf", "pages": 12, ...}
}
```

**Response (after completion):**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "finished",
  "queue": "default",
  "realm": "finance-team",
  "started_at": "2025-01-15T10:23:45.123456Z",
  "finished_at": "2025-01-15T10:24:32.987654Z",
  "result": {
    "chunks": 42,
    "embeddings": 42,
    "summary": "...",
    "duration_sec": 47.5
  },
  "created_at": "2025-01-15T10:23:42.456789Z"
}
```

### Dashboard: Recent jobs

```bash
curl "http://localhost:10000/pipeline/jobs/recent?limit=20&status=finished&realm=finance-team"
```

**Response:**
```json
{
  "jobs": [
    { "id": "...", "status": "finished", "queue": "default", ... },
    { "id": "...", "status": "finished", "queue": "urgent", ... }
  ],
  "count": 2,
  "filters": {
    "realm": "finance-team",
    "queue": null,
    "status": "finished"
  }
}
```

---

## Troubleshooting

### PostgreSQL not configured

**Error:** `RuntimeError: PostgreSQL pool not initialized (DATABASE_URL not set)`

**Solution:**
```bash
# Check .env or environment
echo $DATABASE_URL

# Format: postgresql://user:pass@host:port/db
# For Supabase: postgresql://postgres:pass@db.supabase.co:5432/postgres
```

### Migration fails on first deploy

**Error:** `relation "pipeline_jobs" already exists`

**Solution:** Safe to ignore—table already created. Or use `CREATE TABLE IF NOT EXISTS`.

### Workers can't connect to PostgreSQL

**Ensure both web + worker services have `DATABASE_URL`** in Render environment variables.

```yaml
web:
  envVars:
    - key: "DATABASE_URL"
      fromDatabase: "kitenga-postgres"

background:
  envVars:
    - key: "DATABASE_URL"
      fromDatabase: "kitenga-postgres"  # ← Required!
```

### Queries returning empty

**Check that table exists:**
```bash
# Via Render PostgreSQL client or psql
SELECT COUNT(*) FROM pipeline_jobs;
```

**If missing, run migration again** (safe idempotent).

---

## Performance Considerations

### Indexes
- `status` — For filtering running/finished/failed jobs
- `realm, status` — For multi-tenant dashboards
- `created_at DESC` — For reverse-time queries (recent jobs)
- `queue, status` — For queue-specific monitoring

### Connection Pool
- `min_size=2` — Minimum connections kept warm
- `max_size=10` — Reasonable for 4 web workers + 3 RQ workers
- Adjust for larger deployments:
  ```python
  # In te_po/db/postgres.py
  ConnectionPool(..., min_size=5, max_size=20)
  ```

### Query Best Practices
- Always use `LIMIT` (e.g., `LIMIT 100`) to prevent large scans
- Use `created_at DESC` index for dashboard queries
- For archived jobs, consider partitioning by month (optional)

---

## Migration Path

**Existing projects using Supabase:**

1. Run PostgreSQL migration (creates new `pipeline_jobs` table)
2. Both Supabase and PostgreSQL will be written to (during transition)
3. Gradually deprecate Supabase table
4. Remove Supabase writes once confident

**Code remains backward-compatible** — Supabase still works as fallback.

---

## Summary

✅ **RQ + Redis** — Unchanged (queue, distribute, retry, dead-letter)  
✅ **PostgreSQL** — Durable job tracking, full audit trail  
✅ **Decorator-based** — Minimal code changes (`@track_pipeline_job`)  
✅ **Dual-track** — Workers and API can read from either database  
✅ **Production-ready** — Connection pooling, index strategy, error handling  
✅ **Render-compatible** — Just set `DATABASE_URL` env var

