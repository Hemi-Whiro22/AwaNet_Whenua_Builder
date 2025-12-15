# Realm System

**Last Updated:** 2025-01-13 | **Version:** 1.0.0

Complete guide to creating, managing, and working with specialized realms in Awa Network.

## Overview

Realms are independent, isolated projects that live at the root of The Awa Network. Each realm:

- ✅ Has its own devcontainer (isolated Python environment)
- ✅ Has its own Kaitiaki agent (realm-specific)
- ✅ Cannot access parent or sibling realm files
- ✅ Proxies to main Te Pō for backend data
- ✅ Runs complete three-layer stack (te_po_proxy, te_ao, te_hau)

**Example:**
```
The_Awa_Network/
├── cards_realm/         ← Specialized realm for cards
├── translator_realm/    ← Specialized realm for translation
├── audio_realm/         ← Specialized realm for audio
└── (main Awa Network services)
```

---

## Creating Realms

### Web UI Method (Recommended)

1. **Start the generator:**
   ```bash
   cd /workspaces/The_Awa_Network/te_hau/scripts
   python3 realm_ui.py
   ```

2. **Open browser:**
   Navigate to `http://localhost:8888`

3. **Fill the form:**
   - **Name:** Human-readable (e.g., "Cards Realm")
   - **Slug:** Folder name (auto-generated, e.g., "cards_realm")
   - **Agent Name:** Codex name (e.g., "katu")
   - **Agent Role:** System role (e.g., "card_oracle")
   - **Description:** What the realm does
   - **Git Repository:** (optional) GitHub URL

4. **Click Generate**
   Realm appears at `/workspaces/The_Awa_Network/[slug]/`

### CLI Method

```bash
python te_hau/scripts/generate_realm.py \
  --name "Cards Realm" \
  --slug cards_realm \
  --kaitiaki-name "katu" \
  --kaitiaki-role "card_oracle" \
  --description "Specialized realm for card collections"
```

### Programmatic Method

```python
from te_hau.scripts.generate_realm import RealmGenerator
from pathlib import Path

gen = RealmGenerator(project_root=Path("/workspaces/The_Awa_Network"))
gen.generate(
    name="Cards Realm",
    slug="cards_realm",
    kaitiaki_name="katu",
    kaitiaki_role="card_oracle",
    description="Specialized realm for card collections"
)
```

---

## Realm Structure

Every generated realm has this structure:

```
cards_realm/
├── .devcontainer/              ← Isolated container
│   ├── devcontainer.json
│   ├── Dockerfile              ← Python 3.12 + realm deps
│   └── post_create.sh
│
├── .vscode/                    ← Realm-specific IDE config
│   ├── settings.json
│   └── launch.json
│
├── kaitiaki/                   ← Agent home
│   └── katu/
│       ├── katu_codex.json
│       └── codex.md
│
├── mauri/                      ← Knowledge/state (realm-local)
│   ├── context.md
│   ├── global_env.json
│   └── kaitiaki_templates/
│       └── katu.yaml           ← Agent config (isolation rules)
│
├── te_po_proxy/                ← Local backend
│   ├── main.py                 ← FastAPI server
│   ├── requirements.txt
│   └── routes/
│
├── te_ao/                      ← Frontend (if included)
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── te_hau/                     ← CLI layer
│   ├── cli.py
│   └── commands/
│
├── config/                     ← Realm configuration
│   └── realm.yaml
│
├── .env                        ← Realm secrets (realm-local)
├── requirements.txt            ← Realm dependencies
├── README.md                   ← Realm documentation
└── STRUCTURE.md                ← This template structure
```

---

## Isolation

### What Gets Isolated

**Per-Realm (Independent):**
- DevContainer and Python environment
- Kaitiaki agent (unaware of siblings)
- File system access (can't traverse up)
- VS Code settings and launch configs
- Dependencies and packages
- State files and logs
- Configuration (.env, config/)

**Shared (With Safeguards):**
- Main Te Pō backend (read-only via proxy)
- Supabase database (via proxy)
- SDK tools (for compilation only)

### Isolation Rules in Kaitiaki

Every realm's Kaitiaki includes isolation rules:

```yaml
isolation:
  level: "strict"
  aware_of:
    - own_realm_files
    - own_realm_config
    - local_te_po_proxy
  NOT_aware_of:
    - The_Awa_Network_context
    - sibling_realm_data
  access_control:
    allow_parent_traversal: false
    allow_main_awa_network: false
    allow_sibling_realms: false
```

### Backend Proxy Pattern

```
Realm's Kaitiaki
    ↓
Realm's te_po_proxy/ (http://localhost:8001)
    ↓
Main Te Pō (read-only)
    ↓
Supabase
```

Realms **never directly access** main Te Pō - always through local proxy.

---

## Working with Realms

### Open a Realm in VS Code

1. **File → Open Folder**
2. Select: `/workspaces/The_Awa_Network/cards_realm/`
3. VS Code sees `.devcontainer/devcontainer.json`
4. Click: "Reopen in Container"
5. **Isolated devcontainer spins up** ✅

### Start Services

**Backend (from realm root):**
```bash
cd te_po_proxy
python main.py
# Runs on http://localhost:8001
```

**Frontend:**
```bash
cd te_ao
npm run dev
# Runs on http://localhost:5173
```

**CLI:**
```bash
cd te_hau
python cli.py status
python cli.py kaitiaki spawn
```

### Develop

Edit files in realm (they're isolated):
```
./kaitiaki/katu/         ← Agent code
./te_po_proxy/routes/    ← Backend endpoints
./te_ao/src/             ← Frontend components
./mauri/                 ← Knowledge base
```

No risk of affecting parent or siblings. ✅

---

## Best Practices

### 1. Naming Conventions

- **Realm Name:** Title case, space-separated
  - ✅ "Cards Realm", "Translator Realm"
  - ❌ "CardsRealm", "translator_realm"

- **Slug:** lowercase, underscore-separated
  - ✅ "cards_realm", "translator_realm"
  - ❌ "CardsRealm", "cards-realm"

- **Agent Name:** lowercase, hyphen-optional
  - ✅ "katu", "whare-whakamaori"
  - ❌ "Katu", "Whare Whakamaori"

- **Agent Role:** snake_case, descriptive
  - ✅ "card_oracle", "translator_oracle"
  - ❌ "card", "translate"

### 2. Don't Break Isolation

**❌ Bad:**
```python
# In realm's kaitiaki
import sys
sys.path.insert(0, "../../")
from The_Awa_Network.te_po import something  # Context bleed!
```

**✅ Good:**
```python
# In realm's kaitiaki
import httpx
response = await httpx.post(
    "http://localhost:8001/api/query",  # Use local proxy
    json={"query": "..."}
)
```

### 3. Use .env for Secrets

```bash
# .env (realm-local)
KAITIAKI_API_KEY=secret123
TE_PO_PROXY_URL=http://localhost:8001
DATABASE_URL=postgresql://...
```

NOT in code, NOT in git.

### 4. Document Your Realm

Every realm should have:

**README.md:**
```markdown
# [Realm Name]

**Purpose:** What this realm does

**Kaitiaki:** [agent_name] (role: [role])

**Quick Start:**
```bash
cd te_po_proxy && python main.py
cd te_ao && npm run dev
```

**Services:**
- Backend: http://localhost:8001
- Frontend: http://localhost:5173
```

### 5. Version Control

```bash
cd cards_realm
git init
git add .
git commit -m "Initial: Cards Realm with Katu Kaitiaki"
git remote add origin git@github.com:user/cards-realm.git
git push -u origin main
```

---

## Troubleshooting

### Realm doesn't appear in file system

Check devcontainer paths - realms generate at project root.

### Can't see parent files (expected!)

Isolation is working. Use local proxy (`http://localhost:8001`) instead of direct imports.

### DevContainer fails to start

Check `.devcontainer/Dockerfile` for syntax errors.

```bash
docker build -t test .devcontainer/
```

### Git push fails during generation

Realm still created successfully. Push manually:

```bash
cd cards_realm
git remote add origin git@github.com:user/cards.git
git push -u origin main
```

### Agent can't find its own files

Check `.env` paths - should be relative:
```bash
# .env (GOOD)
REALM_ROOT=.
MAURI_PATH=./mauri

# NOT (BAD)
REALM_ROOT=/workspaces/The_Awa_Network/cards_realm
```

---

## Commands Reference

| Task | Command |
|------|---------|
| Generate realm (Web UI) | `python realm_ui.py` → http://localhost:8888 |
| Generate realm (CLI) | `python generate_realm.py --name "..." --slug ...` |
| Verify isolation | `bash verify_realm_isolation.sh [realm_path]` |
| Start backend | `cd te_po_proxy && python main.py` |
| Start frontend | `cd te_ao && npm run dev` |
| CLI status | `cd te_hau && python cli.py status` |
| Spawn agent | `cd te_hau && python cli.py kaitiaki spawn` |

---

## Next Steps

1. **Create your first realm** → Web UI (http://localhost:8888)
2. **Open in VS Code** → Reopen in Container
3. **Start services** → Backend + Frontend
4. **Develop** → Add your domain logic
5. **Deploy** → Push to GitHub + deploy

See [DEVELOPMENT.md](./DEVELOPMENT.md) for detailed setup.
