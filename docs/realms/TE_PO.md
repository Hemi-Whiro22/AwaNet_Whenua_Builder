# TE_PO Realm

Backend pipeline and processing engine.

## Overview

Te Pō (The Night) is the processing layer - handles document pipeline, OCR, analysis, and intelligent extraction.

## Key Features

- **FastAPI** backend with 60+ endpoints
- **PostgreSQL** job tracking and state
- **RQ (Redis Queue)** for async processing
- **Dual-mode** support: inline (development) and RQ (production)
- **OpenAI Integration** for vision, analysis, and extraction
- **OCR** with Tesseract and vision fallback
- **Queue modes**: Inline (sync) and RQ (async distributed)

## Quick Links

- [TE_PO Architecture Quick Reference](../TE_PO_ARCHITECTURE_QUICKREF.md)
- [TE_PO Quick Start Checklist](../TE_PO_QUICK_START_CHECKLIST.md)
- [TE_PO Render Deployment](../TEPO_RENDER_DEPLOYMENT.md)
- [TE_PO Standalone Setup](../TE_PO_STANDALONE_INDEX.md)
- [Queue Mode Switch](../QUEUE_MODE_SWITCH.md)

## Configuration

See `.env.example` for all environment variables.

Key variables:
- `OPENAI_API_KEY` - OpenAI API access
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis for RQ mode (optional)
- `QUEUE_MODE` - `inline` (default) or `rq`

## Development

```bash
# Inline mode (no Redis needed)
./run_dev.sh

# RQ mode with workers
QUEUE_MODE=rq ./run_dev.sh
```

## Deployment

Deployed to Render with Docker. See [TEPO_RENDER_DEPLOYMENT.md](../TEPO_RENDER_DEPLOYMENT.md).
