# PostgreSQL Job Tracking — Quick Start

**TL;DR:** RQ + Redis (unchanged) + PostgreSQL (durable audit trail)

---

## 1-Minute Setup

```bash
# 1. Ensure psycopg[binary] in requirements.txt ✓ (already there)

# 2. Set DATABASE_URL in .env
export DATABASE_URL="postgresql://user:pass@localhost:5432/tepo"
export REDIS_URL="redis://localhost:6379"

# 3. Run migration
psql $DATABASE_URL < te_po/db/migrations_001_pipeline_jobs.sql

# 4. Start dev server
./run_dev.sh
```

---

## What Changed

| File | Change | Lines |
|------|--------|-------|
| `te_po/db/postgres.py` | NEW | Connection pool + helpers |
| `te_po/db/migrations_001_pipeline_jobs.sql` | NEW | Schema creation |
| `te_po/pipeline/job_tracking.py` | NEW | Tracking decorator |
| `te_po/pipeline/jobs.py` | UPDATED | Added `@track_pipeline_job` |
| `te_po/routes/pipeline.py` | UPDATED | Enqueue writes to both, new endpoints |

**Total code changes:** ~150 lines (decorator pattern = minimal)

---

## Key Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/pipeline/enqueue` | Submit job + write to PostgreSQL |
| GET | `/pipeline/status/{job_id}` | Fetch job from PostgreSQL |
| GET | `/pipeline/jobs/recent?limit=50&status=running` | Dashboard query |

---

## Environment Variables

| Variable | Example | Where Used |
|----------|---------|-----------|
| `DATABASE_URL` | `postgresql://...` | Web + Worker processes |
| `REDIS_URL` | `redis://localhost:6379` | Web + Worker processes |
| `X-Realm` header | (optional) | Multi-tenant tracking |

---

## Testing Locally

```bash
# Terminal 1: Start server
./run_dev.sh

# Terminal 2: Test
# Enqueue
JOB=$(curl -s -X POST http://localhost:8000/pipeline/enqueue \
  -F "file=@sample.pdf" \
  -H "X-Realm: test" | jq -r .job_id)

echo "Job ID: $JOB"

# Poll status
for i in {1..30}; do
  STATUS=$(curl -s http://localhost:8000/pipeline/status/$JOB | jq -r .status)
  echo "[$i] Status: $STATUS"
  [ "$STATUS" = "finished" ] && break
  sleep 1
done

# View result
curl http://localhost:8000/pipeline/status/$JOB | jq .
```

---

## Render Deployment Checklist

- [ ] Add PostgreSQL database (via Render Add-on)
- [ ] Set `DATABASE_URL` env var on web service
- [ ] Set `DATABASE_URL` env var on **all** background worker services
- [ ] Run migration: `python -c "from te_po.db import db_execute; exec(open('te_po/db/migrations_001_pipeline_jobs.sql').read())"`
- [ ] Test `/pipeline/enqueue` returns job_id
- [ ] Test `/pipeline/status/{job_id}` shows "queued"
- [ ] Wait for worker to process, status → "running" → "finished"

---

## Architecture Summary

```
POST /pipeline/enqueue
  ├─ INSERT into PostgreSQL (status='queued')
  ├─ INSERT into Supabase (legacy, backward compat)
  └─ Enqueue to RQ (Redis)
     └─ Worker picks up
        ├─ UPDATE status='running' (PostgreSQL)
        ├─ Process file
        ├─ UPDATE status='finished' (PostgreSQL) [or 'failed']
        └─ Return result
```

Both databases can be read, but **PostgreSQL is primary** for new code.

---

## Backward Compatibility

✅ Old code using Supabase still works  
✅ New code prefers PostgreSQL  
✅ Can migrate Supabase → PostgreSQL queries over time  
✅ No breaking changes to API

---

## Common Issues

| Issue | Fix |
|-------|-----|
| `RuntimeError: PostgreSQL pool not initialized` | Set `DATABASE_URL` env var |
| Migration fails with "already exists" | Normal on re-deploy; safe to ignore |
| Workers can't connect to Postgres | Add `DATABASE_URL` env var to worker services in render.yaml |
| No jobs showing in dashboard | Wait for workers to process (status changes take ~1 sec) |

---

## Useful Queries

```bash
# Active jobs
curl "http://localhost:10000/pipeline/jobs/recent?status=running&limit=10"

# Failed jobs
curl "http://localhost:10000/pipeline/jobs/recent?status=failed&limit=5"

# By realm
curl "http://localhost:10000/pipeline/jobs/recent?realm=finance&limit=20"

# By queue
curl "http://localhost:10000/pipeline/jobs/recent?queue=urgent&limit=10"
```

---

## Next Steps

1. ✅ Deploy to Render
2. ✅ Build dashboard UI using `/pipeline/jobs/recent` endpoint
3. ✅ Add job cancellation: `POST /pipeline/cancel/{job_id}`
4. ✅ Add metrics view: aggregate by status/queue/realm
5. ✅ Archive old jobs (>30 days) to separate table

---

**Questions?** See [PIPELINE_JOB_TRACKING_POSTGRES.md](PIPELINE_JOB_TRACKING_POSTGRES.md) for full documentation.

