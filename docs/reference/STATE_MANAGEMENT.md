# State Management Architecture

## Overview
The Awa Network uses immutable, append-only state for reliability and auditability. Each realm maintains its own state file + carving logs.

## State Files

### Te Pō State
**Path:** `mauri/state/te_po_state.json`
**Guardian:** Kitenga Whiro
**Frequency:** Updated after major operations
**Format:** JSON (versioned)

Structure:
```json
{
  "version": "1.0",
  "realm": "te_po",
  "timestamp": "2025-01-13T10:30:00Z",
  "status": "healthy|degraded|error",
  "assistants": {
    "asst_qa": { "status": "active", "model": "gpt-4", "last_sync": "..." },
    "asst_ops": { "status": "active", "model": "gpt-4", "last_sync": "..." }
  },
  "pipelines": {
    "ocr_pipeline": { "status": "idle", "last_run": "...", "next_run": "..." },
    "vector_sync": { "status": "running", "progress": 0.65, "started": "..." }
  },
  "vector_store": {
    "id": "vs_...",
    "document_count": 1234,
    "last_sync": "2025-01-13T09:00:00Z"
  },
  "database": {
    "status": "connected",
    "pool_size": 10,
    "active_connections": 3
  }
}
```

### Te Hau State
**Path:** `mauri/state/te_hau_state.json`
**Guardian:** Kitenga Whiro (CLI automation)
**Frequency:** Updated per CLI execution

Structure:
```json
{
  "version": "1.0",
  "realm": "te_hau",
  "timestamp": "2025-01-13T10:30:00Z",
  "status": "healthy",
  "cli_status": "ready",
  "workers": {
    "worker_1": { "status": "idle", "last_task": "...", "next_scheduled": "..." }
  },
  "scheduled_tasks": [
    { "name": "daily_sync", "next_run": "2025-01-14T00:00:00Z", "status": "scheduled" }
  ]
}
```

### Te Ao State
**Path:** `mauri/state/te_ao_state.json`
**Guardian:** Te Kitenga Nui
**Frequency:** Updated on major UI events

Structure:
```json
{
  "version": "1.0",
  "realm": "te_ao",
  "timestamp": "2025-01-13T10:30:00Z",
  "status": "healthy",
  "ui": {
    "panels_loaded": ["chat", "search", "files"],
    "active_panel": "chat",
    "user_session": "sess_..."
  },
  "api_connection": {
    "status": "connected",
    "latency_ms": 45,
    "last_sync": "2025-01-13T10:29:50Z"
  }
}
```

---

## Carving Logs (Append-Only)

### Te Pō Carving Log
**Path:** `mauri/state/te_po_carving_log.jsonl`
**Format:** JSON Lines (one entry per line, immutable)
**Purpose:** Audit trail of all backend operations

Each line:
```json
{
  "timestamp": "2025-01-13T10:30:00Z",
  "event_type": "assistant_update|pipeline_start|vector_sync|file_upload|error",
  "guardian": "kitenga_whiro",
  "realm": "te_po",
  "operation": "create_assistant",
  "details": {
    "assistant_id": "asst_...",
    "name": "QA Assistant",
    "model": "gpt-4"
  },
  "status": "success|failure",
  "error": null,
  "duration_ms": 234
}
```

### Te Hau Carving Log
**Path:** `mauri/state/te_hau_carving_log.jsonl`
**Format:** JSON Lines
**Purpose:** Audit trail of CLI commands, workers, automation

### Te Ao Carving Log
**Path:** `mauri/state/te_ao_carving_log.jsonl`
**Format:** JSON Lines
**Purpose:** Audit trail of UI events, user interactions

---

## Realm Lock

**Path:** `mauri/realms/realm_lock.json`
**Purpose:** Prevent concurrent state mutations

Structure:
```json
{
  "locked_realm": "te_po",
  "locked_by": "kitenga_whiro_process_123",
  "locked_at": "2025-01-13T10:30:00Z",
  "expires_at": "2025-01-13T10:35:00Z",
  "operation": "vector_sync"
}
```

**Rules:**
- Max lock duration: 5 minutes
- Auto-release on timeout
- Prevent deadlocks via lock manager
- Request → Acquire → Operate → Release

---

## State Sync Workflow

### Writing State (Kitenga Whiro)
```
1. Acquire realm_lock for te_po
2. Read current te_po_state.json
3. Modify state object
4. Write updated te_po_state.json (atomic)
5. Append carving log entry
6. Release realm_lock
```

### Reading State (Any Guardian/Agent)
```
1. Read te_po_state.json (no lock needed)
2. Check timestamp for staleness
3. If stale (>5 min), fetch fresh from source (API/DB)
4. Cache locally for 30 seconds
```

### Syncing Between Realms
**Example:** Te Ao needs Te Pō status
```
1. Te Ao reads te_po_state.json
2. If status changed, update te_ao_state.json
3. Optionally call GET /env/health on Te Pō for live status
4. Log sync event in both carving logs
```

---

## Data Consistency

### Guarantees
- ✅ Append-only logs → No data loss
- ✅ Atomic state writes → No partial states
- ✅ Single guardian per realm → No conflicts
- ✅ Carving logs → Full audit trail
- ❌ Cross-realm transactions → Use async patterns

### Handling Failures

**Lost connection:**
- Te Ao → Te Pō: Use cached state + retry with backoff
- Carving log write fails: Queue locally, retry on next sync

**State divergence:**
- Automatic: Re-sync from source of truth (Kitenga Whiro)
- Manual: `tehau state reconcile <realm>`

---

## Monitoring State Health

### Checks
```bash
# View state file
cat mauri/state/te_po_state.json | jq .

# Tail carving log
tail -f mauri/state/te_po_carving_log.jsonl | jq .

# Check for stale state
jq '.timestamp' mauri/state/te_po_state.json | xargs -I {} \
  echo "$(date -d {} +%s) vs $(date +%s)" | awk '{print ($2 - $1) / 60 " minutes old"}'

# Monitor lock timeouts
jq 'select(.locked_realm) | .expires_at' mauri/realms/realm_lock.json
```

---

## Best Practices

1. **Always use Kitenga Whiro for writes** — Don't directly edit state files
2. **Carving logs are immutable** — Never delete/modify old entries
3. **Check locks before operating** — Avoid race conditions
4. **Validate state schema** — Use Pydantic models in code
5. **Cache responsibly** — Respect 30-second local cache window
6. **Handle stale data gracefully** — Offer "refresh" to users
7. **Log everything** — Append to carving logs for audits
