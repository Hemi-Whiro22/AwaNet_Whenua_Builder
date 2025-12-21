# MCP Services → Continue IDE → GPT Build Integration

Complete setup guide for connecting your carved MCP services to Continue IDE and GPT Build with **persistent context that can't be dropped**.

## 🎯 Overview

```
Your Services (Te Pō, Git, Render, Supabase)
    ↓
MCP Servers (persistent schema in memory)
    ↓
Continue IDE (IDE tools via MCP)
    ↓
GPT Build App (external API calls + IDE context)
```

## 1️⃣ Continue IDE Setup

### Add to `~/.continue/config.yaml`

```yaml
mcpServers:
  tepo:
    command: python
    args: ["${WORKSPACE_DIR}/mcp_services/tepo/server.py"]
    env:
      TE_PO_BASE_URL: "https://your-render-url.onrender.com"
      TE_PO_AUTH_TOKEN: "${TE_PO_AUTH_TOKEN}"

  git:
    command: python
    args: ["${WORKSPACE_DIR}/mcp_services/git/server.py"]
    env:
      GITHUB_TOKEN: "${GITHUB_TOKEN}"

  render:
    command: python
    args: ["${WORKSPACE_DIR}/mcp_services/render/server.py"]
    env:
      RENDER_API_KEY: "${RENDER_API_KEY}"

  supabase:
    command: python
    args: ["${WORKSPACE_DIR}/mcp_services/supabase/server.py"]
    env:
      SUPABASE_URL: "${SUPABASE_URL}"
      SUPABASE_KEY: "${SUPABASE_KEY}"

# Keep schemas in permanent context
documents:
  - path: "mcp_services/tepo/schema.json"
    description: "Te Pō Backend Schema"
  - path: "mcp_services/git/schema.json"
    description: "Git API Schema"
  - path: "mcp_services/render/schema.json"
    description: "Render Deployment Schema"
  - path: "mcp_services/supabase/schema.json"
    description: "Supabase Database Schema"
```

### Set Environment Variables

```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc, etc)
export TE_PO_BASE_URL="https://your-render-url.onrender.com"
export TE_PO_AUTH_TOKEN="optional_token"
export GITHUB_TOKEN="your_github_personal_token"
export RENDER_API_KEY="your_render_api_key"
export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_KEY="your_supabase_anon_key"
```

### Restart Continue IDE

Close and reopen Continue to load all MCP servers.

## 2️⃣ GPT Build App Configuration

### Create GPT Build Custom Connector

In your GPT Build app, add a **Custom API Connector**:

```json
{
  "name": "Awa Network Connector",
  "baseUrl": "https://your-render-url.onrender.com",
  "authentication": {
    "type": "bearer",
    "tokenEnv": "TE_PO_AUTH_TOKEN"
  },
  "actions": [
    {
      "id": "kitenga_whisper",
      "name": "Chat with Kitenga",
      "description": "Send a message to Kitenga AI",
      "method": "POST",
      "path": "/kitenga/gpt-whisper",
      "parameters": {
        "prompt": { "type": "string", "description": "Your message" },
        "session_id": { "type": "string", "description": "Session ID" },
        "use_retrieval": { "type": "boolean", "description": "Use knowledge base" }
      }
    },
    {
      "id": "vector_search",
      "name": "Search Knowledge Base",
      "method": "POST",
      "path": "/vector/search",
      "parameters": {
        "query": { "type": "string" },
        "top_k": { "type": "integer", "default": 5 }
      }
    },
    {
      "id": "ocr_scan",
      "name": "Scan Document",
      "method": "POST",
      "path": "/ocr/scan",
      "parameters": {
        "file_url": { "type": "string" },
        "taonga_mode": { "type": "boolean" }
      }
    },
    {
      "id": "pipeline_run",
      "name": "Run Pipeline",
      "method": "POST",
      "path": "/awa/pipeline",
      "parameters": {
        "name": { "type": "string", "enum": ["ocr", "summarise", "translate", "embed"] },
        "input": { "type": "object" }
      }
    }
  ]
}
```

### Alternative: Use Pre-configured Tools

If your GPT Build supports OpenAI tool definitions, import the tools directly:

```bash
# Export your te_po/openai_tools.json to GPT Build
cp te_po/openai_tools.json ~/gpt-build-imports/
```

Then in GPT Build:
1. Click "Tools" → "Import from file"
2. Select the tools.json
3. Configure endpoints to point to Render URL

## 3️⃣ How Context Stays Persistent

### Schema is Loaded Once

Each MCP server loads its schema.json when it starts:

```python
# In each service's server.py
with open(schema_path) as f:
    self.schema = json.load(f)  # ← Stays in memory, never dropped
```

### Schema Defines All Tools

The schema tells Continue and GPT Build exactly what's available:

```json
{
  "services": {
    "kitenga": {
      "routes": ["/kitenga/gpt-whisper", "/kitenga/ask", ...],
      "description": "AI processing endpoints"
    }
  },
  "inputSchema": { ... },
  "outputSchema": { ... }
}
```

### Tools Have Fixed Definitions

Each tool knows its inputs and outputs:

```json
{
  "name": "tepo_kitenga_whisper",
  "inputSchema": {
    "properties": {
      "prompt": { "type": "string" }
    }
  }
}
```

**This means:**
- ✅ GPT/Codex can't forget what tools exist
- ✅ Schema is permanent reference
- ✅ No context loops trying to figure out endpoints
- ✅ No "what's the API again?" questions

## 4️⃣ Full Workflow Example

### User asks Continue: "Summarize this document and save to database"

```
1. Continue loads tepo MCP server
   → Loads tepo/schema.json (permanent reference)
   → Sees tepo_ocr_scan tool available

2. Continue loads git MCP server
   → Loads git/schema.json
   → Sees git_create_file tool available

3. Continue loads supabase MCP server
   → Loads supabase/schema.json
   → Sees supabase_insert tool available

4. Continue calls tepo_ocr_scan
   → Sends file to /ocr/scan
   → Gets extracted text

5. Continue calls tepo_pipeline_run
   → Sends text to summarise pipeline
   → Gets summary

6. Continue calls supabase_insert
   → Saves summary to database
   → Returns result

7. Continue displays "Done! Summary saved."
```

**Context never drops** because:
- Each schema stays loaded
- Each tool is predefined
- No guessing about endpoints

## 5️⃣ Running Multiple Services

### Locally (Development)

```bash
# Terminal 1: Te Pō backend
cd /workspaces/The_Awa_Network
python -m te_po.app

# Terminal 2: Continue IDE
code .

# Terminal 3: GPT Build dev server (if needed)
npm run dev
```

### On Render (Production)

Each MCP server can run on Render as a background service:

```yaml
# render.yaml
services:
  - type: web
    name: te_po
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python te_po/app.py
    envVars:
      - key: DATABASE_URL
        value: ${DATABASE_URL}

  - type: background
    name: mcp_tepo_server
    env: python
    buildCommand: pip install mcp httpx
    startCommand: python mcp_services/tepo/server.py
    envVars:
      - key: TE_PO_BASE_URL
        value: https://te-po.onrender.com
```

## 6️⃣ Debugging

### Check if MCP servers are running

```bash
# List loaded servers in Continue
# Open Command Palette → "Continue: Show MCP servers"

# Or test individually:
python mcp_services/tepo/server.py
python mcp_services/git/server.py
python mcp_services/render/server.py
python mcp_services/supabase/server.py
```

### Check environment variables

```bash
env | grep -E "TE_PO|GITHUB|RENDER|SUPABASE"
```

### Verify schema files exist

```bash
ls -la mcp_services/*/schema.json
ls -la mcp_services/*/tools.json
```

## 7️⃣ Integration Checklist

- [ ] MCP service files created (`mcp_services/tepo`, `git`, `render`, `supabase`)
- [ ] Continue config updated with MCP servers
- [ ] Environment variables set
- [ ] Render deployment configured with endpoints
- [ ] Te Pō backend running (local or on Render)
- [ ] GPT Build connector configured
- [ ] Tools tested in Continue IDE
- [ ] Tools tested in GPT Build app

---

**Your system is now carved with solid mauri - context that can't be dropped.** 🤙

Each service has permanent schema, fixed tools, and clear boundaries. No loops, no confusion, just clean execution.
