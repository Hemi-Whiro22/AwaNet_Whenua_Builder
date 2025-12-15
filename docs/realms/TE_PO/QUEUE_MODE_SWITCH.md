# Queue Mode Switch: Inline vs RQ

## Overview

The pipeline job processing system now supports two queue modes:

1. **Inline Mode** (default) — Run pipeline jobs immediately in-process, no Redis required
2. **RQ Mode** — Use Redis Queue for distributed job processing

This allows solo development without Redis while keeping the full distributed queue system for production.

## Environment Configuration

Set the `QUEUE_MODE` environment variable:

```bash
# Inline mode (default, no Redis needed)
export QUEUE_MODE=inline

# RQ mode (requires Redis)
export QUEUE_MODE=rq
```

If not set, defaults to `inline` for solo development.

## Mode Behavior

### Inline Mode (`QUEUE_MODE=inline`)

**When to use:**
- Solo development (no Redis needed)
- Testing pipeline logic
- Running on limited resources

**Behavior:**
- POST /pipeline/enqueue runs the pipeline immediately (blocking)
- Job status transitions happen synchronously: `queued → running → finished|failed`
- Response includes result or error immediately
- GET /pipeline/health/queue returns `"mode": "inline", "status": "healthy"`

**Example:**
```bash
# Start server with inline mode (default)
uvicorn te_po.core.main:app --host 0.0.0.0 --port 8000

# Or explicitly:
export QUEUE_MODE=inline
uvicorn te_po.core.main:app --host 0.0.0.0 --port 8000
```

**Enqueue Request:**
```bash
curl -X POST http://localhost:8000/pipeline/enqueue \
  -F "file=@document.pdf"
```

**Enqueue Response (inline mode):**
```json
{
  "job_id": "abc123...",
  "status": "finished",
  "result": {
    "cleaned_text": "...",
    "embeddings": [...],
    "summary": "..."
  }
}
```

### RQ Mode (`QUEUE_MODE=rq`)

**When to use:**
- Production deployment
- Distributed processing with workers
- Long-running pipelines (need timeout protection)

**Behavior:**
- POST /pipeline/enqueue adds job to Redis queue and returns immediately
- Separate worker processes pull jobs from queue and execute them
- Job status transitions: `queued → running → finished|failed` (asynchronous)
- Queue routing by file size (urgent/default/slow)
- Automatic retries (3 attempts with exponential backoff)

**Example:**
```bash
# Terminal 1: Start server with RQ mode
export QUEUE_MODE=rq
export REDIS_URL=redis://localhost:6379
uvicorn te_po.core.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start RQ worker
export REDIS_URL=redis://localhost:6379
rq worker --with-scheduler
```

**Enqueue Request:**
```bash
curl -X POST http://localhost:8000/pipeline/enqueue \
  -F "file=@document.pdf"
```

**Enqueue Response (RQ mode):**
```json
{
  "job_id": "abc123...",
  "rq_job_id": "def456...",
  "queue": "default",
  "realm": null,
  "status": "queued"
}
```

Then poll status:
```bash
curl http://localhost:8000/pipeline/status/abc123
```

## API Endpoints Behavior

### POST /pipeline/enqueue

**Inline Mode:**
- Synchronous processing
- Returns immediately with result or error
- Status: `finished` or `failed`

**RQ Mode:**
- Asynchronous queueing
- Returns immediately with queued status
- Must poll `/pipeline/status/{job_id}` to track progress

### GET /pipeline/status/{job_id}

Works identically in both modes:
```bash
curl http://localhost:8000/pipeline/status/abc123
```

Response includes current status, result (if finished), error (if failed).

### GET /pipeline/jobs/recent?limit=50&status=finished

List recent pipeline jobs. Works in both modes.

### GET /pipeline/health/queue

**Inline Mode Response:**
```json
{
  "mode": "inline",
  "redis": "disabled",
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**RQ Mode Response:**
```json
{
  "mode": "rq",
  "redis": "up",
  "queues": {
    "urgent": 2,
    "default": 5,
    "slow": 0,
    "dead": 0
  },
  "status": "healthy",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Database Tracking

Both modes always:
- Create a `pipeline_jobs` record in PostgreSQL
- Track job metadata (file, pages, realm)
- Record start/finish times
- Store results and errors

This ensures durability and audit trail regardless of queue mode.

## Local Development Workflow

### Simple Solo Development (No Redis)

```bash
# Set up PostgreSQL (required for all modes)
# See RENDER_POSTGRES_DEPLOYMENT.md for setup

# Use inline mode (default)
export DATABASE_URL=postgresql://user:pass@localhost:5432/tepo_local
# QUEUE_MODE=inline is default, no need to set

# Start the server
./run_dev.sh

# Enqueue a test file
curl -X POST http://localhost:8000/pipeline/enqueue \
  -F "file=@test.pdf" \
  -H "X-Realm: dev"

# Check status immediately (should be finished)
curl http://localhost:8000/pipeline/status/<job_id>
```

### Full Development (With Workers)

```bash
# Terminal 1: Set up environment
export QUEUE_MODE=rq
export DATABASE_URL=postgresql://user:pass@localhost:5432/tepo_local
export REDIS_URL=redis://localhost:6379

# Start server
./run_dev.sh

# Terminal 2: Start RQ worker
export QUEUE_MODE=rq
export REDIS_URL=redis://localhost:6379
rq worker

# Terminal 3: Enqueue test file
curl -X POST http://localhost:8000/pipeline/enqueue \
  -F "file=@test.pdf"

# Check status (will be queued initially, then running, then finished)
curl http://localhost:8000/pipeline/status/<job_id>

# Check queue health
curl http://localhost:8000/pipeline/health/queue
```

## Production Deployment

For Render deployment:

```yaml
# render.yaml
envVars:
  - key: QUEUE_MODE
    value: "rq"
  - key: DATABASE_URL
    sync: false  # From PostgreSQL Add-on
  - key: REDIS_URL
    sync: false  # From Redis Add-on
```

See [RENDER_POSTGRES_DEPLOYMENT.md](RENDER_POSTGRES_DEPLOYMENT.md) for full setup.

## Migration Between Modes

You can switch modes without losing data:

1. All job records persist in PostgreSQL
2. Switching to inline mode: Existing queued jobs in Redis won't be processed
3. Switching to RQ mode: Previous inline results are preserved in DB

To clear RQ queues:
```bash
rq empty
```

## Troubleshooting

### "QUEUE_MODE must be 'inline' or 'rq'"

Invalid QUEUE_MODE value. Check environment variable:
```bash
echo $QUEUE_MODE
# Should be 'inline' or 'rq'
```

### "Pipeline queue unavailable (Redis not configured)" in RQ mode

Redis is not running or REDIS_URL is not set:
```bash
# Start Redis
redis-server

# Set REDIS_URL
export REDIS_URL=redis://localhost:6379
```

### Jobs stuck in queued status (RQ mode)

No worker process is running. Start an RQ worker:
```bash
rq worker
```

### Database connection errors in both modes

PostgreSQL is required for both modes. Check DATABASE_URL:
```bash
export DATABASE_URL=postgresql://user:pass@host:5432/dbname
psql "$DATABASE_URL" -c "SELECT 1"  # Test connection
```

## Summary

| Feature | Inline | RQ |
|---------|--------|-----|
| **Requires Redis** | No | Yes |
| **Job Processing** | Synchronous | Asynchronous |
| **Worker Needed** | No | Yes |
| **Queue Routing** | N/A | Yes (urgent/default/slow) |
| **Timeout Protection** | N/A | Yes (10m/30m/60m) |
| **Retries** | Manual | Automatic (3×) |
| **Best For** | Solo dev | Production |
| **Default** | Yes | No |

Choose your mode based on your development or deployment scenario!
