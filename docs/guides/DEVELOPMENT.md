# Development Guide

## Local Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.9+, Node.js 18+
- Git

### Environment Setup
```bash
# Copy template env files
cp te_po/core/.env.example te_po/core/.env
cp te_hau/.env.example te_hau/.env

# Fill in secrets
# - SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
# - OPENAI_API_KEY, OPENAI_VECTOR_STORE_ID
```

### Running Locally

**Docker Compose (All services)**
```bash
docker-compose up --build
```

**Individual Services**
```bash
# Te Pō (FastAPI backend)
cd te_po && python -m uvicorn core.main:app --reload --host 0.0.0.0 --port 8010

# Te Hau (CLI)
cd te_hau && python -m cli.hau --help

# Te Ao (Frontend)
cd te_ao && npm install && npm run dev
```

### UTF-8 Locale (Critical)
All services enforce UTF-8 for Māori text support:
```bash
export LANG=mi_NZ.UTF-8
export LC_ALL=mi_NZ.UTF-8
```

This is auto-set in Docker and Render deployments.

## Common Workflows

### Adding a Te Pō Endpoint
1. Create route file in `te_po/routes/<name>.py`
2. Import in `te_po/core/main.py` and register with FastAPI app
3. Add auth/validation middleware as needed
4. Test with `curl` or Postman
5. Document in API_CONTRACTS.md

### Running a Te Hau Command
```bash
cd te_hau
python -m cli.hau <command> [options]
```

Common commands:
- `tehau kaitiaki info <guardian>` — Get guardian status
- `tehau kaitiaki chat <guardian>` — Chat with a guardian
- `tehau pipeline run <name>` — Execute a pipeline

### Frontend Development
```bash
cd te_ao
npm run dev  # Watch mode
npm run build  # Production build
npm run preview  # Test production build locally
```

### Database Queries
Supabase console: https://supabase.com (login with service role)

Common query tasks:
- Check pgvector embeddings: `SELECT id, embedding FROM documents LIMIT 5;`
- View state: `SELECT * FROM realm_state WHERE realm = 'te_po';`
- Audit logs: Check `mauri/state/te_po_carving_log.jsonl`

## Debugging

### Te Pō Logs
```bash
# Docker container
docker logs te_po -f

# Local run
tail -f te_po/core/logs/*.log
```

### Te Hau Debug
```bash
LOGLEVEL=DEBUG python -m cli.hau <command>
```

### Frontend DevTools
- Browser console: `F12`
- Vite HMR: Check browser console for hot reload errors
- State inspection: DevUI panels in app

## Testing

### Run All Tests
```bash
./test_intake.sh
```

### Specific Tests
```bash
cd te_po && python run_tests.sh
cd te_hau && pytest tests/
cd te_ao && npm run test
```

## Deployment

### Render (Production)
- Push to `master` branch
- Render auto-deploys via `render.yaml`
- Check logs: Render dashboard
- Verify secrets: Dashboard → Settings → Environment

### Local Render Simulation
```bash
docker-compose -f docker-compose.yaml up
```

## Git Workflow
```bash
# Create feature branch
git checkout -b feature/my-feature

# Commit with clear messages
git commit -m "feat: add new endpoint to te_po"

# Push and create PR
git push origin feature/my-feature
# Then open PR on GitHub
```

## Critical Notes
- **Mauri is source of truth** — Check `mauri/architecture/` before making structural changes
- **State sync** — Write changes to `mauri/state/` via carving logs
- **Guardian ownership** — Respect kaitiaki domain boundaries (see GUARDIANS.md)
- **Locale enforcement** — Never skip UTF-8 setup
