# API Contracts — Te Pō ↔ Te Ao Integration

## Overview
Te Ao (frontend) consumes Te Pō (backend) APIs exclusively. No direct pipeline/storage access from frontend.

## Base URL
```
http://localhost:8010  (dev)
https://tepo.example.com  (prod via Render)
```

Auth: Bearer token (PIPELINE_TOKEN) in headers for protected routes.

---

## Core Endpoints

### Health & Status
```
GET /env/health
```
Response:
```json
{
  "status": "healthy",
  "utf8_verified": true,
  "timestamp": "2025-01-13T10:30:00Z",
  "secrets_loaded": ["OPENAI_API_KEY", "SUPABASE_URL", ...]
}
```

### Chat / Assistant Interface
```
POST /chat
Headers: Authorization: Bearer {token}
Body:
{
  "message": "string",
  "assistant_id": "asst_...",
  "thread_id": "thread_..." (optional)
}
```
Response:
```json
{
  "response": "string",
  "thread_id": "thread_...",
  "timestamp": "2025-01-13T10:30:00Z"
}
```

### Vector Search / RAG
```
POST /search/vectors
Headers: Authorization: Bearer {token}
Body:
{
  "query": "string",
  "top_k": 5,
  "threshold": 0.7
}
```
Response:
```json
{
  "results": [
    {
      "id": "uuid",
      "content": "string",
      "similarity": 0.95,
      "metadata": { "source": "...", "date": "..." }
    }
  ]
}
```

### File Upload & Processing
```
POST /files/upload
Headers: Authorization: Bearer {token}, Content-Type: multipart/form-data
Body: FormData { file, metadata }
```
Response:
```json
{
  "file_id": "file_...",
  "status": "processing|complete",
  "url": "/files/file_...",
  "processed_at": "2025-01-13T10:30:00Z"
}
```

### Pipeline Status
```
GET /pipelines/{pipeline_id}
Headers: Authorization: Bearer {token}
```
Response:
```json
{
  "id": "pipeline_...",
  "name": "string",
  "status": "running|completed|failed",
  "progress": 0.75,
  "started_at": "2025-01-13T10:00:00Z",
  "estimated_completion": "2025-01-13T10:30:00Z",
  "result": { ... } (when complete)
}
```

---

## Error Responses

All errors follow standard format:
```json
{
  "error": "ErrorType",
  "message": "Human-readable message",
  "code": "ERR_CODE",
  "timestamp": "2025-01-13T10:30:00Z"
}
```

Common codes:
- `401` — Unauthorized (invalid token)
- `403` — Forbidden (insufficient permissions)
- `404` — Not found
- `422` — Validation error
- `500` — Server error

---

## Frontend Integration Checklist

- [ ] Set `TE_PO_BASE_URL` env var in `te_ao/.env`
- [ ] Set `PIPELINE_TOKEN` env var in `te_ao/.env`
- [ ] Add base URL + auth to all fetch requests
- [ ] Implement retry logic for network failures
- [ ] Cache responses where appropriate (search, static data)
- [ ] Handle streaming responses (for long-running operations)
- [ ] Display UTF-8 content correctly (ensure charset=utf-8 headers)

---

## Rate Limiting
- Default: 100 req/min per token
- Burst: 500 req/min (5-second window)
- Backoff: Exponential retry with `Retry-After` header

---

## Versioning
Current API version: `v1`

Breaking changes → `v2` endpoint. Old version supported for 6 months.

### Schema Evolution Rules
- New fields: Always backward-compatible (optional, with defaults)
- Renamed fields: Deprecated old name, support both for 2 releases
- Removed fields: Deprecated for 1 release, then removed in next major
- Endpoint moves: Old path redirects to new with 301/302

---

## Examples

### Chat Example (Frontend code)
```javascript
const response = await fetch(`${process.env.TE_PO_BASE_URL}/chat`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${process.env.PIPELINE_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    message: 'What is in the knowledge base?',
    assistant_id: 'asst_kitenga'
  })
});

const data = await response.json();
console.log(data.response);
```

### Vector Search Example
```javascript
const results = await fetch(`${process.env.TE_PO_BASE_URL}/search/vectors`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${process.env.PIPELINE_TOKEN}` },
  body: JSON.stringify({
    query: 'kaitiaki responsibilities',
    top_k: 3
  })
});

const { results: documents } = await results.json();
documents.forEach(doc => console.log(doc.content));
```

---

## Monitoring & Metrics
- Log all API calls to `mauri/state/te_po_carving_log.jsonl`
- Track latency, error rates, token usage
- Daily sync report: `mauri/state/api_sync_report.json`
