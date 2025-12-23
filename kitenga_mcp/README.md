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

## Live Tooling Checklist

- **Manifest readiness** – Run `./scripts/check_kitenga_manifest.sh` from the repo root to export `PIPELINE_TOKEN`, call `https://kitenga-main.onrender.com/tools/list`, and pipe the JSON through `jq`. If that succeeds, the manifest is available for GPT Builder / the Kitenga Whiro app.
- **Trigger a tool call** – Use `./scripts/run_kitenga_tool_call.sh` with a JSON body (via STDIN or `-f`) to POST to `/tools/call`. The helper logs the bearer header for you, so you can test GET/POST operations (e.g. `{"domain":"kitenga","command":"kitenga_gpt_whisper","input":{"whisper":"Test"}}`).
- **Grab the trimmed schema** – Fetch `https://kitenga-main.onrender.com/openapi-core.json` (or `/.well-known/openapi-core.json`) to expose the 30-path schema with the `servers` metadata that GPT Builder expects.
- **Point GPT at kitenga-main** – Update GPT Builder/OpenAI apps to import `https://kitenga-main.onrender.com/openai_tools.json` (with `Authorization: Bearer $PIPELINE_TOKEN`) and use the `/openapi-core.json` schema so the same tool set is shared between the builder, the app, and your automation.

This keeps every live test running through `kitenga-main`, so the bearer token, stealth metadata, and vector logging stay centralized while you prep GPT to hit those endpoints.
