# Project Template - Complete Three-Realm Structure

The `te_hau/project_template/` is now a **complete three-realm blueprint** that new realms are generated from.

## Updated Template Structure

```
project_template/
├── te_po_proxy/          ← Backend (proxy to main Te Pō)
│   ├── main.py
│   ├── bootstrap.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── te_ao/                ← Frontend (React + Vite)
│   ├── index.html
│   ├── src/
│   │   ├── main.jsx
│   │   ├── App.jsx
│   │   ├── App.css
│   │   └── index.css
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── te_hau/               ← CLI / Command layer
│   ├── __init__.py
│   └── cli.py
│
├── kaitiaki/             ← Kaitiaki agents
│
├── mauri/                ← State & knowledge
│   ├── kaitiaki_templates/
│   ├── state/
│   ├── documents/
│   └── archived/
│
├── config/               ← Configuration
│   ├── realm.json
│   ├── proxy.toml
│   └── tools.json
│
├── .github/              ← Workflows
│   └── workflows/
│
├── scripts/              ← Helpers
│
├── docs/                 ← Documentation
│
├── STRUCTURE.md          ← Directory guide
├── .env.template
└── README.md
```

## What Changed

### ✅ Renamed: `mini_te_po` → `te_po_proxy`

**Why:**
- Clarifies purpose: **proxy to main Te Pō**, not a standalone backend
- Consistent naming: `te_` prefix aligns with three-realm system
- Better intent: Shows it's a read-only proxy, not a full Te Pō instance

**Updated:**
- `/te_hau/project_template/te_po_proxy/` ← New name
- `main.py` title: "Te Pō Proxy - Read Backend Proxy"
- `realm_generator.py` clones this new structure

### ✅ Added: `te_ao/` (Frontend)

**Includes:**
- `index.html` — Main HTML entry
- `src/main.jsx` — React entry point
- `src/App.jsx` — App component
- `src/App.css` + `src/index.css` — Styles
- `package.json` — Frontend dependencies
- `vite.config.js` — Vite configuration

**Purpose:** Gives new realms a complete frontend to customize

### ✅ Added: `te_hau/` (CLI Layer)

**Includes:**
- `cli.py` — Command-line interface
  - `tehaus status` — Show realm status
  - `tehaus kaitiaki spawn` — Initialize agents
  - `tehaus kaitiaki list` — List available agents
- `__init__.py` — Module initialization

**Purpose:** Provides CLI for realm operations and automation

## Why This Structure Makes Sense

Each realm you generate with the Realm Generator now has:

| Layer | Purpose | Port | Technology |
|-------|---------|------|-------------|
| **te_po_proxy** | Read backend (talks to main Te Pō) | 8000 | FastAPI (Python) |
| **te_ao** | User-facing frontend | 5173 | React + Vite (JavaScript) |
| **te_hau** | CLI & automation | CLI | Python Click |

All backed by:
- **mauri/** — State & knowledge layer
- **kaitiaki/** — Realm-specific AI agents
- **config/** — Realm configuration

This is exactly like The Awa Network's main system:
- `te_po/` = main backend
- `te_ao/` = main frontend
- `te_hau/` = main CLI

But scaled down and customizable for specialized realms.

## How to Use

### Generate a New Realm

```bash
python te_hau/scripts/generate_realm.py \
  --name "Cards Realm" \
  --slug cards_realm \
  --kaitiaki-name "katu" \
  --kaitiaki-role "cards_oracle" \
  --description "Oracle for card cataloging"
```

### Result

```
cards_realm/
├── te_po_proxy/              ← Your local backend proxy
├── te_ao/                    ← Your frontend
├── te_hau/                   ← Your CLI
├── mauri/
│   └── kaitiaki_templates/
│       └── katu.yaml         ← Your Kaitiaki (YAML source)
├── kaitiaki/
│   └── katu/
│       └── katu_manifest.json ← Compiled manifest
└── [configs, docs, etc.]
```

### Develop Locally

```bash
# Terminal 1: Backend proxy
cd cards_realm/te_po_proxy
python main.py

# Terminal 2: Frontend
cd cards_realm/te_ao
npm install && npm run dev

# Terminal 3: CLI
cd cards_realm/te_hau
python cli.py status
```

### Customize

1. **Edit Kaitiaki:** `cards_realm/mauri/kaitiaki_templates/katu.yaml`
2. **Customize Frontend:** `cards_realm/te_ao/src/`
3. **Add Routes:** `cards_realm/te_po_proxy/main.py`
4. **Compile:** `python compile_kaitiaki.py --agent katu`

## Examples Already Generated

### Cards Realm
```
cards_realm/
├── te_po_proxy/          ← Card data proxy
├── te_ao/                ← Card UI
├── kaitiaki/katu/        ← Card oracle Kaitiaki
└── [configuration]
```

### Translator Realm
```
translator_realm/
├── te_po_proxy/          ← Translation proxy
├── te_ao/                ← Translator UI
├── kaitiaki/whare-whakamaori/ ← Translator Kaitiaki
└── [configuration]
```

## File Changes Summary

| File | Change | Reason |
|------|--------|--------|
| `te_hau/project_template/mini_te_po/` | → `te_po_proxy/` | Clarify purpose |
| `te_hau/project_template/te_po_proxy/main.py` | Updated title | Reflect new name |
| `te_hau/project_template/te_ao/` | **New** | Complete frontend |
| `te_hau/project_template/te_hau/` | **New** | Complete CLI |
| `te_hau/project_template/STRUCTURE.md` | Updated | Document new layout |
| `te_hau/scripts/generate_realm.py` | Auto-uses new structure | Works automatically |

## Next Steps

1. **Use realm generator** to spin up new realms
2. **Customize each realm** for your use case (cards, translator, UTF-8, etc.)
3. **Each realm is independent** but connected to main Te Pō
4. **Deploy separately** or together as needed

See `docs/REALM_GENERATOR.md` and `docs/COMPLETE_WORKFLOW.md` for full guides.
