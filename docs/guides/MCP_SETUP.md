# MCP Setup & Configuration

## Overview

The Awa Network MCP servers are ready to enhance Haiku (Copilot) with direct access to:
- Te Pō backend operations (pipelines, vector memory, kaitiaki tasks)
- Supabase database (schema inspection, SQL queries)
- Git/GitHub workflow automation
- Cloudflare deployment
- Render deployment

This document covers setup, activation, and usage.

---

## Quick Start

### 1. Prerequisites

```bash
# Install MCP SDK (Python)
pip install mcp

# Install MCP SDK (TypeScript/Node)
npm install -g @modelcontextprotocol/sdk

# Verify Python servers
python mcp/tepo_server/server.py --help
python mcp/supabase_server/server.py --help

# Verify TypeScript servers
npm run build -C mcp
npm run start -C mcp
```

### 2. Environment Setup

```bash
# Copy to .env or export
export TE_PO_BASE_URL=http://localhost:8010
export PIPELINE_TOKEN=your_pipeline_token_here
export SUPABASE_URL=https://your-project.supabase.co
export SUPABASE_SERVICE_ROLE_KEY=your_service_key_here
export CLOUDFLARE_API_TOKEN=your_cf_token
export CLOUDFLARE_ACCOUNT_ID=your_account_id
export RENDER_API_KEY=your_render_key
export GITHUB_TOKEN=your_github_token
```

### 3. Activate MCP in Your IDE

#### VS Code (with Copilot)
Create/edit `.vscode/settings.json`:
```json
{
  "[mcp]": {
    "tools": [
      {
        "name": "tepo-mcp",
        "server": "python",
        "args": ["-m", "mcp.tepo_server.server"]
      },
      {
        "name": "supabase-mcp",
        "server": "python",
        "args": ["-m", "mcp.supabase_server.server"]
      },
      {
        "name": "git-mcp",
        "server": "node",
        "args": ["mcp/git_server/server.js"]
      }
    ]
  }
}
```

#### Claude Desktop (with desktop app)
Edit `~/.claude/config.json`:
```json
{
  "mcpServers": {
    "tepo": {
      "command": "python",
      "args": ["/path/to/mcp/tepo_server/server.py"]
    },
    "supabase": {
      "command": "python",
      "args": ["/path/to/mcp/supabase_server/server.py"]
    },
    "git": {
      "command": "node",
      "args": ["/path/to/mcp/git_server/server.js"]
    }
  }
}
```

#### Cline (VS Code extension)
In Cline settings, enable:
```
✓ Model Context Protocol (MCP)
✓ Load from workspace config
```

---

## Server Details

### Te Pō MCP Server

**File:** `mcp/tepo_server/server.py`
**Env vars:** `TE_PO_BASE_URL`, `PIPELINE_TOKEN`

**Available Tools:**

| Tool | Purpose |
|------|---------|
| `vector_search` | Semantic search across knowledge base |
| `vector_store` | Store content + embeddings |
| `run_pipeline` | Execute OCR, summarize, translate, embed, taonga pipelines |
| `kaitiaki_register` | Register new guardian agent |
| `kaitiaki_execute_task` | Execute task via kaitiaki |
| `kaitiaki_context` | Get kaitiaki state/capabilities |
| `log_activity` | Append to carving logs |
| `notify` | Send notifications |
| `get_te_po_status` | Health check |
| `list_pipelines` | Available pipelines |
| `list_kaitiaki` | Registered kaitiaki |

**Example Usage (Haiku):**
```
I'll search the knowledge base for information about Māori naming conventions.
<vector_search>
  query: "Māori naming conventions for realms"
  top_k: 5
  threshold: 0.7
</vector_search>

Now I'll store this documentation to vector memory for future reference.
<vector_store>
  content: "[Full documentation text]"
  metadata: {"source": "CONTEXT.md", "type": "guide"}
  tapu_level: 0
</vector_store>
```

### Supabase MCP Server

**File:** `mcp/supabase_server/server.py`
**Env vars:** `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`

**Available Tools:**

| Tool | Purpose |
|------|---------|
| `sql_query` | Execute SQL queries (safe mode by default) |
| `schema_inspect` | Get table/column definitions |
| `list_tables` | List all tables in schema |
| `get_table_info` | Detailed table info (columns, indexes, constraints) |
| `propose_migration` | Suggest schema migration |
| `check_rls` | Inspect Row-Level Security rules |

**Example Usage:**
```
Let me inspect the vector memory table to see what's stored.
<sql_query>
  query: "SELECT id, content, similarity FROM ti_memory LIMIT 5"
  mode: "read_only"
</sql_query>

Now let me propose a migration to add a new index.
<propose_migration>
  table: "ti_memory"
  change: "Add index on realm_id and created_at"
</propose_migration>
```

### Git MCP Server

**File:** `mcp/git_server/server.js`
**Env vars:** `GITHUB_TOKEN`, `GIT_USER_NAME`, `GIT_USER_EMAIL`

**Available Tools:**

| Tool | Purpose |
|------|---------|
| `git_commit` | Create commit with message |
| `git_tag` | Create/list git tags |
| `github_create_pr` | Create pull request |
| `github_list_prs` | List PRs |
| `semantic_version` | Auto-increment version |

### Cloudflare MCP Server

**File:** `mcp/cloudflare_server/server.py`
**Env vars:** `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`

**Available Tools:**

| Tool | Purpose |
|------|---------|
| `deploy_pages` | Deploy to Cloudflare Pages |
| `set_env_var` | Set environment variable |
| `add_custom_domain` | Configure custom domain |
| `list_deployments` | List recent deployments |

### Render MCP Server

**File:** `mcp/render_server/server.py`
**Env vars:** `RENDER_API_KEY`

**Available Tools:**

| Tool | Purpose |
|------|---------|
| `deploy_service` | Deploy/redeploy service |
| `get_service_status` | Check service health |
| `set_env_var` | Update environment variable |
| `list_services` | List all services |

---

## Workflow Examples

### Example 1: Document Processing & Storage

```
User: "Process this PDF and store it in the knowledge base"

Haiku (me):
1. <run_pipeline> name=ocr input_data={"file": "document.pdf"}
2. <run_pipeline> name=summarise input_data={"content": "[OCR output]"}
3. <run_pipeline> name=embed input_data={"text": "[summary]"}
4. <vector_store> content="[full text]" metadata={"source": "document.pdf"}
5. <log_activity> event_type="document_processed" details={...}
```

### Example 2: Autonomous Testing & Deployment

```
User: "Test the API and deploy if healthy"

Haiku (me):
1. <get_te_po_status>  -- Check backend health
2. <sql_query> query="SELECT COUNT(*) FROM realm_registry"  -- Verify DB
3. <kaitiaki_execute_task> kaitiaki="ruru" task="run_test_suite" input_data={...}
4. <git_tag> tag="v1.2.3"  -- Tag release
5. <deploy_service> service="te-po"  -- Deploy
6. <notify> recipient="team" message="Deployment complete: v1.2.3"
```

### Example 3: Knowledge Base Query & Enhancement

```
User: "Answer this question using the knowledge base"

Haiku (me):
1. <vector_search> query="[user question]" top_k=10
2. [Process search results]
3. <vector_store> content="[answer with sources]" metadata={"qa_pair": true}
4. <log_activity> event_type="qa_answered" details={...}
```

---

## Activation Checklist

- [ ] Env vars exported (`TE_PO_BASE_URL`, `PIPELINE_TOKEN`, `SUPABASE_*`, etc.)
- [ ] MCP SDK installed (`pip install mcp` and/or `npm install @modelcontextprotocol/sdk`)
- [ ] Servers tested locally:
  - [ ] `python mcp/tepo_server/server.py`
  - [ ] `python mcp/supabase_server/server.py`
  - [ ] `npm run start -C mcp`
- [ ] IDE configured (VS Code, Claude Desktop, or Cline)
- [ ] MCP tools registered and callable
- [ ] Test a simple tool: `vector_search` or `get_te_po_status`

---

## Troubleshooting

### Server won't start
```bash
# Check Python version (3.8+)
python --version

# Install missing dependencies
pip install mcp httpx supabase aiohttp

# Test server directly
python -m mcp.tepo_server.server --help
```

### Env vars not found
```bash
# Verify exports
env | grep TE_PO
env | grep SUPABASE
env | grep PIPELINE_TOKEN

# Add to .env file
cat > /workspaces/The_Awa_Network/.env << EOF
TE_PO_BASE_URL=http://localhost:8010
PIPELINE_TOKEN=your_token
SUPABASE_URL=your_url
SUPABASE_SERVICE_ROLE_KEY=your_key
EOF

source .env
```

### Connection refused
```bash
# Ensure Te Pō is running
curl http://localhost:8010/env/health

# Check firewall
netstat -an | grep 8010

# Restart Te Pō
docker-compose restart te_po
```

### Supabase queries fail
```bash
# Verify credentials
curl -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
  https://$SUPABASE_URL/rest/v1/

# Check RLS policies
# (via Supabase dashboard)
```

---

## Best Practices

1. **Use read-only by default** — Supabase server defaults to SELECT-only
2. **Carve operations** — Always log important operations with `log_activity`
3. **Respect tapu levels** — Don't expose protected content unnecessarily
4. **Batch queries** — Use single SQL query for multiple rows, not N queries
5. **Cache results** — Store search results locally to avoid re-querying
6. **Monitor tokens** — Track API calls to avoid rate limits
7. **Test locally first** — Validate MCP tools before deploying

---

## Integration with Haiku Codex

Haiku (Copilot) is configured to:
1. Use Te Pō MCP for pipeline execution & vector ops
2. Use Supabase MCP for database queries & audits
3. Use Git MCP for versioning & PRs
4. Use Cloudflare/Render MCPs for deployments
5. Log all operations to carving logs
6. Respect guardian domains (Kitenga Whiro owns all MCP operations)

See `kaitiaki/HAIKU_CODEX.md` for Haiku-specific usage guidelines.

---

## Advanced: Custom MCP Servers

To create your own MCP server:

```python
from mcp.server import Server

server = Server("my-server")

@server.call_tool()
async def my_tool(arg1: str, arg2: int = 5) -> ToolResult:
    """Do something custom."""
    result = f"Called with {arg1}, {arg2}"
    return ToolResult(content=[TextContent(type="text", text=result)])

# Register
server.add_tool(Tool(
    name="my_tool",
    description="Do something custom",
    inputSchema={...}
))
```

See `mcp/src/index.ts` for the main TypeScript MCP server template.
