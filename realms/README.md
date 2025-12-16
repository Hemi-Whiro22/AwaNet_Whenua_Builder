# Spawned Realms

This folder contains dynamically created realms spawned by Kitenga Whiro.

Each realm is a self-contained project with:
- Its own `.devcontainer/` for isolated development
- Its own `te_po_proxy/` for backend connection
- Its own `mauri/` state folder
- Its own OpenAI Assistant + Vector Store

## Structure

```
realms/
├── te_wai/           # Example: Water realm
│   ├── .devcontainer/
│   ├── .env
│   ├── mauri/
│   ├── te_po_proxy/
│   └── README.md
├── te_ahi/           # Example: Fire realm
│   └── ...
└── README.md
```

## Creating a Realm

Use the Kitenga DevHub in te_ao or the CLI:

```bash
# Via te_hau CLI
cd te_hau && python -m cli.main realm create --name te_wai --kaitiaki "Te Taniwha"

# Or via API
curl -X POST https://tiwhanawhana-backend.onrender.com/assistant/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Te Taniwha", "instructions": "Guardian of te_wai realm"}'
```

## Opening a Realm in VS Code

Each realm has its own devcontainer. To develop in isolation:

1. Open VS Code
2. File → Open Folder → Select `realms/te_wai`
3. When prompted, "Reopen in Container"

The realm will spin up with Python 3.12, Node 20, and all dependencies.

## Kitenga Whiro Access

Kitenga Whiro has read access to ALL realm vector stores for cross-realm context.
Each realm's kaitiaki only sees its own data.
