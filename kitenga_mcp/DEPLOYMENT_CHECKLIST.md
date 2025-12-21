# 🎯 MCP Services Deployment Checklist

Complete checklist for deploying your MCP services architecture.

## Phase 1: Local Development ✓

- [x] Created `mcp_services/` directory structure
- [x] Built 4 MCP servers:
  - [x] Te Pō backend server (tepo/server.py)
  - [x] Git integration server (git/server.py)
  - [x] Render deployment server (render/server.py)
  - [x] Supabase database server (supabase/server.py)
- [x] Created schemas (schema.json per service)
- [x] Created tool definitions (tools.json per service)
- [x] Created shared utilities (shared/__init__.py)
- [x] Created documentation:
  - [x] README.md - Overview
  - [x] ARCHITECTURE.md - Design details
  - [x] INTEGRATION_GUIDE.md - Setup instructions
  - [x] QUICK_REFERENCE.md - Quick start

## Phase 2: Local Testing

- [ ] Install Python MCP library
  ```bash
  pip install mcp httpx
  ```

- [ ] Set environment variables
  ```bash
  export TE_PO_BASE_URL="http://localhost:8010"
  export GITHUB_TOKEN="your_token"
  export RENDER_API_KEY="your_key"
  export SUPABASE_URL="your_url"
  export SUPABASE_KEY="your_key"
  ```

- [ ] Test each server individually
  ```bash
  python mcp_services/tepo/server.py
  python mcp_services/git/server.py
  python mcp_services/render/server.py
  python mcp_services/supabase/server.py
  ```

- [ ] Verify environment variables loaded
- [ ] Check that schemas load correctly
- [ ] Verify tools are listed

## Phase 3: Continue IDE Integration

- [ ] Copy Continue config template from `config.yaml`
- [ ] Update `~/.continue/config.yaml` with MCP servers
- [ ] Set correct workspace paths
- [ ] Set environment variables in config
- [ ] Restart Continue IDE
- [ ] Type `@mcp` in chat to see available tools
- [ ] Test one tool: `tepo_kitenga_whisper`
- [ ] Test git tool: `git_repo_info`
- [ ] Test Render tool: `render_list_services`
- [ ] Test Supabase tool: `supabase_select`

## Phase 4: Render Deployment

- [ ] Create Render project (if not exists)
- [ ] Deploy Te Pō backend to Render
- [ ] Get Render URL: `https://your-app.onrender.com`
- [ ] Create Render API key
- [ ] Set `TE_PO_BASE_URL` to Render URL

## Phase 5: GPT Build Integration

- [ ] Create GPT Build app (if not exists)
- [ ] Create custom API connector
- [ ] Add Te Pō endpoints to connector:
  - [ ] `/kitenga/gpt-whisper` (POST)
  - [ ] `/vector/search` (POST)
  - [ ] `/ocr/scan` (POST)
  - [ ] `/awa/pipeline` (POST)

- [ ] Test connector endpoints
- [ ] Import pre-configured tools from `te_po/openai_tools.json`
- [ ] Test tool calls in GPT Build UI

## Phase 6: Complete Integration Test

- [ ] Continue IDE → Call tepo_kitenga_whisper
- [ ] Continue IDE → Call git_create_branch
- [ ] Continue IDE → Call render_list_services
- [ ] Continue IDE → Call supabase_insert
- [ ] GPT Build → Call chat endpoint
- [ ] GPT Build → Call search endpoint
- [ ] GPT Build → Call OCR endpoint

## Phase 7: Production Checklist

- [ ] All secrets in environment (not hardcoded)
- [ ] HTTPS only (for Render URLs)
- [ ] Auth tokens configured
- [ ] Rate limits understood
- [ ] Error handling tested
- [ ] Backup/recovery documented

## Troubleshooting

### MCP Servers Not Loading

```bash
# Check if Python can import mcp
python -c "import mcp; print(mcp.__version__)"

# If missing:
pip install mcp
```

### Schema Files Not Found

```bash
# Verify files exist
ls -la mcp_services/*/schema.json

# Check paths are relative to server.py
cd mcp_services/tepo && python -c "import json; json.load(open('schema.json'))"
```

### Environment Variables Not Set

```bash
# Check current values
env | grep -E "TE_PO|GITHUB|RENDER|SUPABASE"

# Set temporarily for testing
export TE_PO_BASE_URL="http://localhost:8010"
python mcp_services/tepo/server.py
```

### Continue Not Seeing MCP Tools

1. Check config file syntax (YAML valid?)
2. Restart Continue IDE completely
3. Open Command Palette → "Continue: Reload MCP servers"
4. Check stderr for Python errors

## File Structure Verification

```bash
# Should see this structure:
find mcp_services -type f | sort

mcp_services/ARCHITECTURE.md
mcp_services/INTEGRATION_GUIDE.md
mcp_services/QUICK_REFERENCE.md
mcp_services/README.md
mcp_services/config.yaml
mcp_services/git/schema.json
mcp_services/git/server.py
mcp_services/git/tools.json
mcp_services/render/schema.json
mcp_services/render/server.py
mcp_services/render/tools.json
mcp_services/shared/__init__.py
mcp_services/supabase/schema.json
mcp_services/supabase/server.py
mcp_services/supabase/tools.json
mcp_services/tepo/schema.json
mcp_services/tepo/server.py
mcp_services/tepo/tools.json
```

## Commands Reference

```bash
# List all available tools
grep '"name"' mcp_services/*/tools.json | cut -d'"' -f4

# Count tools per service
echo "Te Pō:" && grep '"name"' mcp_services/tepo/tools.json | wc -l
echo "Git:" && grep '"name"' mcp_services/git/tools.json | wc -l
echo "Render:" && grep '"name"' mcp_services/render/tools.json | wc -l
echo "Supabase:" && grep '"name"' mcp_services/supabase/tools.json | wc -l

# Validate JSON
python -m json.tool mcp_services/tepo/schema.json > /dev/null && echo "Valid!"
```

## Success Criteria

You'll know it's working when:

1. ✅ Continue IDE lists MCP tools with `@mcp`
2. ✅ You can type `@tepo` and see tepo tools
3. ✅ You can call a tool and get back results
4. ✅ GPT Build has endpoints configured
5. ✅ GPT Build tools can call endpoints
6. ✅ Context doesn't drop mid-conversation
7. ✅ No more "what's the API again?" loops

---

**Mark items as you complete them. You've got this.** 🤙
