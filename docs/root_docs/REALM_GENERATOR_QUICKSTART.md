# 🏔️ Realm Generator Quick Start

## What Just Got Created

Two new tools for managing multiple specialized realms:

1. **`realm_ui.py`** — Web interface (browser-based)
2. **Updated `generate_realm.py`** — Now outputs realms as siblings (not subfolders)
3. **Updated `.devcontainer/devcontainer.json`** — Mounts workspace parent for visibility

## Quick Start (30 seconds)

### 1. Start the Web UI

```bash
cd /workspaces/The_Awa_Network/te_hau/scripts
python3 realm_ui.py
```

You'll see:
```
============================================================
🏔️  Realm Generator UI
============================================================
Project Root: /workspaces/The_Awa_Network
Output Root:  /workspace/..
Access at:    http://localhost:8888
============================================================
```

### 2. Open Browser

Navigate to: **http://localhost:8888**

You'll see a beautiful form with:
- Realm Name (e.g., "Cards Realm")
- Slug (auto-filled from name)
- Agent Name (e.g., "katu")
- Agent Role (e.g., "card_oracle")
- Description (optional)

### 3. Generate a Realm

Fill in the form and click "Generate Realm"

Example:
```
Name: Cards Realm
Slug: cards_realm
Agent Name: katu
Agent Role: card_oracle
Description: Oracle for card collections
```

Result: A new folder appears at `~/Titirauwakawa/cards_realm/` with complete structure.

### 4. See it in VS Code

Because devcontainer mounts `~/Titirauwakawa/`, the new realm appears **instantly** in VS Code sidebar!

```
📁 The_Awa_Network/
📁 cards_realm/  ← NEW (just appeared!)
```

## Key Changes

### `generate_realm.py` Updated

**Old behavior:** Output realms inside The_Awa_Network
```
The_Awa_Network/
├── cards_realm/  ← Subfolder (cluttered)
└── translator_realm/
```

**New behavior:** Output realms as siblings
```
~/Titirauwakawa/
├── The_Awa_Network/
├── cards_realm/  ← Sibling folder (clean!)
└── translator_realm/
```

**How it works:**
```python
# Old
realm_dir = self.project_root / slug

# New
realm_dir = self.output_root / slug
# where output_root defaults to project_root.parent
```

### `.devcontainer/devcontainer.json` Updated

Added workspace mount:
```json
"mounts": ["source=${localEnv:HOME}/Titirauwakawa,target=/workspace,type=bind"],
"workspaceFolder": "/workspace/The_Awa_Network"
```

This means:
- Devcontainer sees `~/Titirauwakawa/` as `/workspace/`
- The_Awa_Network is the main workspace folder
- All sibling realms are visible in the sidebar

## Use Cases

### Generate Multiple Realms Fast

1. Open web UI
2. Create realm 1 → appears in sidebar
3. Create realm 2 → appears in sidebar
4. Create realm 3 → appears in sidebar
5. Edit all three in same VS Code window

### Command Line (Still Works)

```bash
python te_hau/scripts/generate_realm.py \
  --name "Translator Realm" \
  --slug translator_realm \
  --kaitiaki-name "whare-whakamaori" \
  --kaitiaki-role "translator_oracle"
```

This also outputs to sibling folder (thanks to updated output_root logic).

## What Realms Look Like

Each generated realm has:

```
cards_realm/
├── kaitiaki/                      ← Agent home
│   └── katu/
│       ├── katu_codex.json
│       └── codex.md
├── mauri/                         ← Knowledge/state
│   ├── context.md
│   ├── global_env.json
│   └── kaitiaki_templates/
│       └── katu.yaml              ← Edit this!
├── te_po_proxy/                   ← Backend proxy
│   ├── main.py
│   └── requirements.txt
├── te_hau/                        ← CLI layer
│   └── cli.py
├── te_ao_proxy/                   ← Frontend (if included)
│   ├── index.html
│   └── src/
├── config/                        ← Config files
│   └── realm.yaml
├── README.md                      ← Auto-generated docs
└── .env                           ← Environment
```

## Workflow: Web UI + VS Code

```
1. Browser: http://localhost:8888
   Fill form + Click "Generate"
              ↓
2. New realm created at ~/Titirauwakawa/cards_realm/
              ↓
3. VS Code: Realm appears in sidebar
   (because devcontainer mounts ~/Titirauwakawa/)
              ↓
4. VS Code: Open file → Edit code
              ↓
5. Terminal: cd cards_realm && python te_hau/cli.py status
```

## Combining Both Approaches

The system now supports **both** for maximum flexibility:

| Tool | Role | When to Use |
|------|------|------------|
| **Web UI (realm_ui.py)** | Visual generation interface | Creating realms quickly, team members who prefer GUI |
| **Devcontainer mount** | Automatic folder visibility | Seamless sidebar integration, no extra steps |
| **CLI (generate_realm.py)** | Programmatic generation | Automation, scripts, CI/CD |

They don't conflict—they complement each other!

## Files Modified/Created

✅ **Created:** `/te_hau/scripts/realm_ui.py` (447 lines)
- FastAPI web server
- Beautiful HTML form
- Real-time generation with status
- Auto-slug generation from name

✅ **Updated:** `/te_hau/scripts/generate_realm.py`
- Added `output_root` parameter to __init__
- Changed `realm_dir = self.output_root / slug`
- Defaults to `project_root.parent` (sibling output)

✅ **Updated:** `/.devcontainer/devcontainer.json`
- Added mounts for workspace parent
- Set workspaceFolder to The_Awa_Network

## Next (Optional)

Create `.code-workspace` file for one-click multi-folder opening:

```json
// ~/Titirauwakawa.code-workspace
{
  "folders": [
    { "name": "🏔️ The Awa Network", "path": "The_Awa_Network" },
    { "name": "🃏 Cards Realm", "path": "cards_realm" },
    { "name": "🌐 Translator Realm", "path": "translator_realm" }
  ]
}
```

Then in VS Code: `File → Open Workspace from File → Titirauwakawa.code-workspace`

---

**Ready to create your first realm?** Start the web UI and open localhost:8888! 🚀
