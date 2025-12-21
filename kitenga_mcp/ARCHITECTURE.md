# MCP Services Architecture - Complete Carving

Your system is now properly carved with **persistent context per service**. No more context drops, no loop tunnels.

## 📁 Structure

```
mcp_services/
├── tepo/
│   ├── server.py       # MCP server implementation
│   ├── schema.json     # Input/output schema (permanent)
│   └── tools.json      # Tool definitions
├── git/
│   ├── server.py
│   ├── schema.json
│   └── tools.json
├── render/
│   ├── server.py
│   ├── schema.json
│   └── tools.json
├── supabase/
│   ├── server.py
│   ├── schema.json
│   └── tools.json
├── shared/
│   └── __init__.py     # Shared utilities & context manager
├── config.yaml         # Continue IDE configuration
└── README.md
```

## 🎯 What This Does

Each service has **3 files**:

1. **server.py** - Implements MCP protocol
   - Loads schema and tools
   - Calls external APIs
   - Returns structured results

2. **schema.json** - Permanent context
   - Service description
   - Available endpoints
   - Input/output definitions
   - This stays in memory = NO CONTEXT DROP

3. **tools.json** - Tool catalog
   - 12-18 tools per service
   - Input/output schemas for each
   - Examples for reference
   - Clear, mauri-fueled context

## 🔧 Services Included

### Te Pō (Backend)
- 12 tools: chat, OCR, vector search, memory, pipelines, kaitiaki, database

### Git (GitHub)
- 17 tools: repos, branches, commits, files, PRs, issues, releases, workflows

### Render (Deployment)
- 8 tools: services, deployments, scaling, monitoring

### Supabase (Database)
- 7 tools: select, insert, update, delete, RPC, storage

## 🚀 How to Use

### 1. Install Dependencies
```bash
pip install httpx mcp
```

### 2. Set Environment Variables
```bash
export TE_PO_BASE_URL=https://your-render-url.onrender.com
export TE_PO_AUTH_TOKEN=optional_token
export GITHUB_TOKEN=your_github_token
export RENDER_API_KEY=your_render_key
export SUPABASE_URL=your_supabase_url
export SUPABASE_KEY=your_supabase_key
```

### 3. Update Continue Config
Copy the `config.yaml` content to `~/.continue/config.yaml`:

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
```

### 4. Restart Continue
Close and reopen Continue IDE to load the servers.

## 💪 Why This Works

- **Schemas stay in memory**: Each service loads its schema once, keeps it loaded
- **No context loops**: Schema defines boundaries, prevents drift
- **Fast tool lookup**: Tools are indexed by name, instant access
- **Isolated contexts**: Each service manages its own state
- **Mauri-fueled**: Built with solid kaitiaki principles

## 🔄 Tool Flow

```
Continue IDE
    ↓
MCP Server (e.g., tepo)
    ↓
Load schema.json (permanent)
    ↓
Find tool in tools.json
    ↓
Call backend API
    ↓
Return structured result
    ↓
Continue displays result
```

## 📊 Available Tools

### Te Pō (12 tools)
- `tepo_kitenga_whisper` - Main chat endpoint
- `tepo_vector_search` - Semantic search
- `tepo_ocr_scan` - Document OCR
- `tepo_pipeline_run` - Execute pipeline
- `tepo_reo_translate` - Māori translation
- `tepo_memory_store` - Store in memory
- `tepo_memory_query` - Query memory
- `tepo_kaitiaki_register` - Register guardian
- `tepo_task_execute` - Execute task
- `tepo_db_chat_history` - Get chat history
- `tepo_db_taonga_search` - Search treasures
- `tepo_health_check` - Health status

### Git (17 tools)
- `git_repo_info` - Repository information
- `git_list_branches`, `git_create_branch` - Branch management
- `git_list_commits` - Commit history
- `git_get_file`, `git_create_file`, `git_update_file`, `git_delete_file` - File operations
- `git_list_pull_requests`, `git_create_pull_request` - PR management
- `git_list_issues`, `git_create_issue` - Issue tracking
- `git_list_releases`, `git_create_release` - Release management
- `git_get_user` - User profile
- `git_list_workflows` - GitHub Actions

### Render (8 tools)
- `render_list_services` - List services
- `render_get_service` - Service details
- `render_deploy` - Trigger deployment
- `render_list_deploys`, `render_get_deploy` - Deployment history
- `render_update_env` - Update environment
- `render_list_events` - Event logs
- `render_scale_service` - Scale services

### Supabase (7 tools)
- `supabase_select` - Query rows
- `supabase_insert` - Insert row
- `supabase_update` - Update row
- `supabase_delete` - Delete row
- `supabase_rpc` - Call stored procedure
- `supabase_upload_file` - Upload file
- `supabase_list_buckets` - List buckets

## 🛠️ Testing Locally

```bash
# Test Te Pō server
python mcp_services/tepo/server.py

# Test Git server
export GITHUB_TOKEN=your_token
python mcp_services/git/server.py

# Test Render server
export RENDER_API_KEY=your_key
python mcp_services/render/server.py

# Test Supabase server
export SUPABASE_URL=your_url
export SUPABASE_KEY=your_key
python mcp_services/supabase/server.py
```

## 📝 Adding New Services

To add Cloudflare (or any other service):

1. Create `mcp_services/cloudflare/` directory
2. Create `schema.json` with service endpoints
3. Create `tools.json` with tool definitions
4. Create `server.py` using a service as template
5. Add to `config.yaml`

That's it. The pattern is solid.

---

**You now have a properly carved digital whenua with mauri that can't be dropped.** Each service holds its own context. No more getting lost in loop tunnels. 🤙
