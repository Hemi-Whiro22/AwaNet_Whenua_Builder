# MCP Services Architecture

Clean, modular MCP server setup with persistent context per service. Each service has its own schema and tools to prevent context drops.

```
mcp_services/
├── README.md (this file)
├── tepo/              # Te Pō backend service
│   ├── server.py
│   ├── schema.json
│   └── tools.json
├── git/               # GitHub integration
│   ├── server.py
│   ├── schema.json
│   └── tools.json
├── render/            # Render deployment service
│   ├── server.py
│   ├── schema.json
│   └── tools.json
├── supabase/          # Supabase database service
│   ├── server.py
│   ├── schema.json
│   └── tools.json
├── cloudflare/        # Cloudflare edge service
│   ├── server.py
│   ├── schema.json
│   └── tools.json
├── shared/            # Shared utilities
│   ├── __init__.py
│   ├── auth.py
│   ├── context.py
│   └── utils.py
└── config.yaml        # Main MCP config for Continue IDE
```

## Each Service Has:

1. **server.py** - MCP server implementation
2. **schema.json** - Input/output schema for tools (NO CONTEXT LOSS)
3. **tools.json** - Tool definitions with descriptions and examples

## Why This Works

- **Isolated Contexts**: Each service keeps its own schema in memory
- **No Loop Tunnels**: Schema is permanent per service, can't drop
- **Fast Recovery**: If context splits, each service has enough context to recover
- **Clean Execution**: Tools know exactly what they accept/return

## Running Locally

```bash
# Each server runs independently
python mcp_services/tepo/server.py
python mcp_services/git/server.py
python mcp_services/render/server.py
python mcp_services/supabase/server.py
python mcp_services/cloudflare/server.py
```

## Deploying to Production

All servers can run on Render as separate services, or bundled. Configuration in `config.yaml`.

## Continue IDE Integration

Add to `~/.continue/config.yaml`:

```yaml
mcpServers:
  tepo:
    command: python
    args: ["mcp_services/tepo/server.py"]
    env:
      TE_PO_BASE_URL: "https://your-render-url.onrender.com"

  git:
    command: python
    args: ["mcp_services/git/server.py"]
    env:
      GITHUB_TOKEN: ${GITHUB_TOKEN}

  render:
    command: python
    args: ["mcp_services/render/server.py"]
    env:
      RENDER_API_KEY: ${RENDER_API_KEY}

  supabase:
    command: python
    args: ["mcp_services/supabase/server.py"]
    env:
      SUPABASE_URL: ${SUPABASE_URL}
      SUPABASE_KEY: ${SUPABASE_KEY}

  cloudflare:
    command: python
    args: ["mcp_services/cloudflare/server.py"]
    env:
      CLOUDFLARE_API_KEY: ${CLOUDFLARE_API_KEY}
```

---

Each service is a self-contained carving - solid mauri fueled context that can't be dropped. 🤙
