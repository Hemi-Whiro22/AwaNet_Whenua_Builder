# Complete SDK + Realm Generator Workflow

This document ties together everything: **SDK**, **Realm Generator**, **Kaitiaki Templates**, and how they work together to create your multi-realm Awa Network ecosystem.

## Architecture Overview

```
The Awa Network (Main System)
├── Te Pō Backend (primary)
├── Te Ao Frontend (primary)
└── Kaitiaki Agents:
    ├── Haiku (development assistant)
    ├── Kitenga Whiro (oracle, taonga watcher)
    └── Te Kitenga Nui (vision keeper)

    ↑
    └─ All can spawn realm-specific Kaitiaki

Specialized Realms (spun up with generator)
├── Cards Realm
│   ├── mini_te_po (local)
│   ├── te_ao (local frontend)
│   └── katu Kaitiaki → talks to main Te Pō
│
├── Translator Realm
│   ├── mini_te_po (local)
│   ├── te_ao (local frontend)
│   └── whare-whakamaori Kaitiaki → talks to main Te Pō
│
└── UTF-8 Realm
    ├── mini_te_po (local)
    ├── te_ao (local frontend)
    └── taku-kupu Kaitiaki → talks to main Te Pō
```

## The Three Tools

### 1. **SDK Compiler** (`te_hau/sdk/`)

**What it does:** Compiles YAML templates → JSON manifests

**Files:**
- `te_hau/sdk/compiler.py` — Main compiler logic
- `te_hau/sdk/types.py` — Type definitions
- `te_hau/sdk/loader.py` — YAML loader
- `mauri/scripts/compile_kaitiaki.py` — CLI tool

**Usage:**
```bash
python mauri/scripts/compile_kaitiaki.py --agent kitenga_whiro
# Generates:
# - kaitiaki/kitenga_codex/kitenga_manifest.json
# - te_po/openai_assistants.json
# - te_po/openai_tools.json (all from one YAML!)
```

### 2. **Realm Generator** (`te_hau/scripts/generate_realm.py`)

**What it does:** Scaffolds new specialized realms with Kaitiaki

**Usage:**
```bash
python te_hau/scripts/generate_realm.py \
  --name "Cards Realm" \
  --slug cards_realm \
  --kaitiaki-name "katu" \
  --kaitiaki-role "cards_oracle" \
  --description "Oracle for card cataloging"
```

**Creates:**
- `cards_realm/` directory (copy of template)
- `cards_realm/mauri/kaitiaki_templates/katu.yaml`
- `cards_realm/kaitiaki/katu/` (manifest + docs)

### 3. **Project Template** (`te_hau/project_template/`)

**What it is:** Blueprint for new realms

**Structure:**
```
project_template/
├── mini_te_po/         ← Local FastAPI backend
├── te_ao/              ← Frontend template
├── mauri/              ← State/knowledge layer
├── config/             ← Realm configs
└── scripts/            ← Setup helpers (new_realm.sh)
```

## Complete Workflow

### Step 1: Generate Realm

```bash
cd /path/to/The_Awa_Network

python te_hau/scripts/generate_realm.py \
  --name "Cards Realm" \
  --slug cards_realm \
  --kaitiaki-name "katu" \
  --kaitiaki-role "cards_oracle" \
  --description "Oracle for card cataloging and search"
```

**Output:**
```
cards_realm/
├── mauri/kaitiaki_templates/katu.yaml  ← YAML source (editable)
├── kaitiaki/katu/
│   ├── katu_manifest.json              ← JSON output (generated)
│   └── docs/
│       ├── README.md
│       └── CONTEXT.md
├── mini_te_po/                         ← Local backend
├── te_ao/                              ← Local frontend
└── .env                                ← Configuration
```

### Step 2: Customize Kaitiaki (Optional)

Edit `cards_realm/mauri/kaitiaki_templates/katu.yaml`:

```yaml
metadata:
  name: katu
  role: cards_oracle
  purpose: "Oracle for card cataloging and search"
  version: "1.0.0"

identity:
  glyph: "🃏"
  korowai: te_po

assistants:
  search:
    description: "Search cards by title, artist, rarity"
    allowed_tools: [vector_search, card_catalog_query]
  curator:
    description: "Categorize and tag new cards"
    allowed_tools: [tag_cards, update_metadata]

# ... more config
```

### Step 3: Compile Kaitiaki

**Option A: Using realm's local SDK**
```bash
cd cards_realm
# If SDK is installed locally
python mauri/scripts/compile_kaitiaki.py --agent katu
```

**Option B: Using main SDK**
```bash
# From The_Awa_Network
python te_hau/scripts/compile_kaitiaki.py \
  --project-dir ../cards_realm \
  --agent katu
```

**Generates:**
```
cards_realm/kaitiaki/katu/katu_manifest.json
```

### Step 4: Deploy Realm

```bash
cd cards_realm

# Start local backend
cd mini_te_po && python app.py &

# Start frontend
cd .. && npm run dev

# In production, use the deploy scripts in ./scripts/
```

### Step 5: Connect to Main Te Pō

**In `cards_realm/.env`:**
```
TE_PO_BASE_URL=https://main-te-po.example.com
HUMAN_BEARER_KEY=<token>
REALM_NAME=cards
```

**Kaitiaki communicates via:**
```python
# In cards_realm's mini_te_po
response = await client.post(
    f"{TE_PO_BASE_URL}/kaitiaki/execute",
    json={"agent": "katu", "task": "search_cards"}
)
```

### Step 6: Version Control

```bash
cd cards_realm
git init
git add .
git commit -m "Initial: Cards Realm with Katu Kaitiaki"
git remote add origin https://github.com/org/cards-realm.git
git push -u origin main
```

## Key Concepts

### Source of Truth: YAML Templates

```
mauri/kaitiaki_templates/katu.yaml  ← Edit here
        ↓ (compile)
kaitiaki/katu/katu_manifest.json    ← Use here at runtime
```

- YAML is **version-controlled** ✅
- JSON is **generated** ✅
- Changes flow one direction (YAML → JSON) ✅
- Reproducible (recompile anytime) ✅

### Realm Independence

Each realm:
- ✅ Has its own frontend (te_ao)
- ✅ Has its own local backend (mini_te_po)
- ✅ Has its own Kaitiaki (katu, whare-whakamaori, etc.)
- ✅ Shares main Te Pō for vectors/state
- ✅ Can be deployed separately

### Kaitiaki Communication

```
Realm Kaitiaki (katu)
    ↓ HTTP/REST
Realm's mini_te_po (local)
    ↓ (registers tasks)
Main Te Pō Backend
    ↓
Supabase + Vector Store
```

## File Locations Reference

| Purpose | Location | Type | Editable? |
|---------|----------|------|-----------|
| Main Kaitiaki templates | `mauri/kaitiaki_templates/` | YAML | ✅ |
| SDK compiler | `te_hau/sdk/` | Python | ✅ |
| Realm generator | `te_hau/scripts/generate_realm.py` | Python | ✅ |
| Project template | `te_hau/project_template/` | Blueprint | ✅ |
| Generated manifests | `kaitiaki/*/[name]_manifest.json` | JSON | ❌ |
| Realm YAML templates | `[realm]/mauri/kaitiaki_templates/` | YAML | ✅ |
| Realm manifests | `[realm]/kaitiaki/*/[name]_manifest.json` | JSON | ❌ |

## Benefits

✅ **Single source of truth** — YAML templates define everything
✅ **Reproducible** — Regenerate JSON anytime
✅ **Scalable** — Spin up realms easily
✅ **Organized** — Clear separation of concerns
✅ **Documented** — Auto-generated context docs
✅ **Deployable** — Each realm is independent
✅ **Integrated** — All realms talk to main backend

## Quick Commands

```bash
# Generate new realm
python te_hau/scripts/generate_realm.py \
  --name "Realm Name" --slug realm_slug \
  --kaitiaki-name "name" --kaitiaki-role "role" \
  --description "description"

# Compile main system Kaitiaki
python mauri/scripts/compile_kaitiaki.py --agent all

# Compile specific realm Kaitiaki
cd realm_name
python mauri/scripts/compile_kaitiaki.py --agent kaitiaki_name

# Test realm locally
cd realm_name && npm run dev

# Deploy realm
./scripts/deploy.sh
```

## Next Steps

1. **Run realm generator** for your first specialized realm
2. **Customize YAML** with your domain-specific tools
3. **Test locally** with mini_te_po
4. **Deploy** to Cloudflare/Render
5. **Monitor** using Kaitiaki state logs
