# The Awa Network — Māori Intelligence Engine
Ka taea te huri te mīhini; ko te mahara te pou.

**Personal IDE & Knowledge System**
Built with FastAPI (Te Pō), React (Te Ao), Python CLI (Te Hau)

---

## Documentation

All project documentation lives in `/docs`:

### Getting Started
- **[CONTEXT](docs/CONTEXT.md)** — Project overview & quick reference
- **[DEVELOPMENT](docs/guides/DEVELOPMENT.md)** — Local setup & workflows

### For Developers
- **[API Contracts](docs/reference/API_CONTRACTS.md)** — Te Pō integration specs
- **[Llama3 Integration](docs/guides/LLAMA3.md)** — Local code analysis (free)
- **[MCP Setup](docs/guides/MCP_SETUP.md)** — Tool integration guide

### Architecture & Reference
- **[Guardians](docs/guides/GUARDIANS.md)** — Kaitiaki agent system
- **[State Management](docs/reference/STATE_MANAGEMENT.md)** — Immutable state & logs
- **[MCP Alignment](docs/architecture/MCP_ALIGNMENT.md)** — Tool ecosystem
- **[Glossary](docs/reference/GLOSSARY.md)** — 40+ terms (Māori + technical)

---

## Project Structure

```
The Awa Network
├── te_ao/          Frontend (React + Vite)
├── te_hau/         CLI & automation (Python)
├── te_po/          Backend (FastAPI)
├── kaitiaki/       Guardian agents (Haiku, Kitenga, etc.)
├── mauri/          Source of truth (governance)
├── docs/           Documentation (organized)
└── mcp/            Tool integrations
```

---

## Quick Start

### Backend (Te Pō)
```bash
cd te_po
pip install -r ../requirements.txt
python -m te_po.core.main
# http://localhost:8000
```

### Frontend (Te Ao)
```bash
cd te_ao
npm install
npm run dev
# http://localhost:5173
```

---

## Key Features

- 3-Realm Architecture (Processing, Automation, Presentation)
- Māori naming & te reo support (UTF-8 mi_NZ enforced)
- Guardian Agents (Haiku, Kitenga, Te Kitenga Nui)
- Free Local Inference (Llama3 for code analysis)
- Vector Memory (Supabase + pgvector)
- Immutable carving logs for audit trails

---

## Cost Strategy

Budget: $90 OpenAI

Optimization:
- Llama3 local (FREE) — Code review, docs, error analysis
- Vector search ($0.001/call) — Memory queries
- Complex synthesis ($0.01–0.02/call) — OpenAI when needed

Target: 81% cost reduction

---

**Last updated:** 13 Tīhema 2025
**Maintained by:** Haiku (Whakataukī)
