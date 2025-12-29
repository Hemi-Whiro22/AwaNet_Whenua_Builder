# Token Economy & Open AI Cost Optimization

**Budget:** $90 OpenAI | 70% Premium remaining
**Goal:** Reduce token consumption 90%+ via MCP + local inference

---

## Current Situation

**Typical Request (Without MCP):**
```
Read file 1: 5KB
Read file 2: 8KB
Read file 3: 12KB
Grep search: 3KB
Analysis: 2KB
Response: 1KB
─────────────
Total: ~31KB per request
```

**Cost:** 31KB × 0.002/K tokens (GPT-4 input) = ~$0.06 per request
**Monthly (10 requests/day):** ~$18

---

## Phase 1: MCP Tool Usage (Immediate, $0 additional cost)

### Rule: Search Before Reading

**Old Way:**
```python
# Read all glossary files to find a term
read_file("GLOSSARY_EXPANDED.md")  # 15KB
grep_search("kaitiaki")  # 2KB context
# Total: 17KB
```

**New Way (MCP):**
```python
vector_search("kaitiaki definition")  # Returns 2KB directly
# Total: 2KB
# Savings: 90%
```

### Rule: Query Database Instead of File Reading

**Old Way:**
```python
read_file("mauri/state/te_po_state.json")  # 8KB
read_file("mauri/state/te_hau_state.json") # 7KB
read_file("mauri/state/te_ao_state.json")  # 6KB
# Total: 21KB
```

**New Way (MCP):**
```python
sql_query("SELECT * FROM realm_state LIMIT 10")  # Returns 2KB
# Total: 2KB
# Savings: 90%
```

### Rule: Use Git MCP for Repo Context

**Old Way:**
```python
read_file("package.json")  # 3KB
grep_search("version")     # 2KB
# Total: 5KB
```

**New Way (MCP):**
```python
git_tag()  # Returns current version + history, 1KB
# Total: 1KB
# Savings: 80%
```

### Practical Limits
```
Per-request context after MCP optimization:
- Tool call overhead: ~0.5KB
- Small response: ~1KB
- Search results: ~2KB
- Code snippet: ~3KB
──────────────────────
Ideal request: ~6KB (vs. old 31KB)
Savings: 81%

Cost reduction:
- Old: $0.06/request
- New: $0.01/request
- Monthly: $6 (vs. $18)
```

---

## Phase 2: Local Llama3 (GPU/CPU, Free)

### What to Offload

**Use OpenAI For:**
- ✅ Complex code synthesis (architectural decisions)
- ✅ Semantic search (vector embeddings)
- ✅ Multi-step workflows (reasoning)
- ✅ Bug diagnosis (requires deep context)

**Use Local Llama3 For:**
- ✅ Code review (pattern matching)
- ✅ Documentation generation (template filling)
- ✅ Error message analysis (known patterns)
- ✅ Linting suggestions (rule-based)
- ✅ Refactoring proposals (syntax-level)

### Setup: Ollama + Llama3

```bash
# 1. Install Ollama (macOS/Linux/Windows)
curl https://ollama.ai/install.sh | sh

# 2. Pull Llama3
ollama pull llama3

# 3. Verify
ollama list
# llama3   latest     7b    39gb

# 4. Start in background
ollama serve &

# 5. Test
curl http://localhost:11434/api/generate -d '{
  "model": "llama3",
  "prompt": "Review this code: def hello(): print()",
  "stream": false
}'
```

### MCP Wrapper for Llama3

Create `mcp/llama3_server/server.py`:

```python
#!/usr/bin/env python3
"""Local Llama3 MCP Server - Zero Cost Code Review & Docs"""

import httpx
import asyncio
import json
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult

server = Server("llama3-mcp")
OLLAMA_URL = "http://localhost:11434"

@server.call_tool()
async def code_review(code: str, language: str = "python") -> ToolResult:
    """Review code for quality, style, security issues."""
    prompt = f"""Review this {language} code for:
- Security issues
- Performance problems
- Style violations
- Refactoring opportunities

Code:
{code}

Provide concise, actionable feedback."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": "llama3", "prompt": prompt, "stream": False}
            )
            result = response.json()
            return ToolResult(
                content=[TextContent(type="text", text=result['response'])],
                is_error=False
            )
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {e}")],
            is_error=True
        )

@server.call_tool()
async def generate_docstring(code: str, language: str = "python") -> ToolResult:
    """Generate docstring for function/class."""
    prompt = f"""Generate a {language} docstring for:

{code}

Format: Clear, concise, include params and return type."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": "llama3", "prompt": prompt, "stream": False}
            )
            result = response.json()
            return ToolResult(
                content=[TextContent(type="text", text=result['response'])],
                is_error=False
            )
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {e}")],
            is_error=True
        )

@server.call_tool()
async def error_analysis(error: str, context: str = "") -> ToolResult:
    """Analyze error message and suggest fixes."""
    prompt = f"""Analyze this error and suggest fixes:

Error:
{error}

Context:
{context}

Provide 2-3 likely causes and solutions."""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": "llama3", "prompt": prompt, "stream": False}
            )
            result = response.json()
            return ToolResult(
                content=[TextContent(type="text", text=result['response'])],
                is_error=False
            )
    except Exception as e:
        return ToolResult(
            content=[TextContent(type="text", text=f"Error: {e}")],
            is_error=True
        )

async def main():
    async with server:
        await server.wait_for_shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Usage In Workflow

```python
# Intelligent tool selection
def refactor_code(code_snippet):
    # For complex refactoring -> OpenAI
    if "architectural" in task:
        return openai_tool("refactor")

    # For syntax-level -> Llama3 (free)
    else:
        return llama3_tool("code_review") + llama3_tool("generate_docstring")

# Result: 99% cost savings on documentation tasks
```

---

## Hybrid Strategy: Monthly Budget Allocation

### Budget: $90
```
Phase 1 (MCP optimization):     -$5  (vector search, DB queries)
Phase 2 (Llama3 local):          -$0  (all local inference)
Reserved (semantic tasks):       $10
Reserved (complex synthesis):    $15
Safety margin:                   $70
───────────────────────
Total: $90 available
```

### Monthly Spend Estimate (New Model)
```
Vector search (5/day):           $2   (low token count)
Code synthesis (2/day):          $4   (uses Llama3 mostly)
Database queries (3/day):        $1   (MCP, ~0 tokens)
Error analysis (2/day):          $0   (Llama3)
Semantic search (1/day):         $2   (OpenAI embeddings)
Complex workflows (weekend):     $5
───────────────────────
Total: ~$14/month (vs. $72/month old way)
```

**Savings: 81%** ✅

---

## Implementation Checklist

### Week 1: MCP Optimization
- [ ] Activate MCP tools in IDE
- [ ] Replace 5 file reads with `vector_search`
- [ ] Replace 3 grep searches with `sql_query`
- [ ] Monitor token usage in requests

### Week 2: Llama3 Setup
- [ ] Install Ollama + Llama3
- [ ] Create `mcp/llama3_server/server.py`
- [ ] Test code_review, generate_docstring, error_analysis
- [ ] Add to `.mcp/config.json`

### Week 3: Integration
- [ ] Update Haiku workflow to use Llama3 for non-critical tasks
- [ ] Create decision tree (when to use which tool)
- [ ] Track token usage per tool
- [ ] Adjust as needed

---

## Decision Tree

```
User Request
│
├─ Needs semantic understanding? → OpenAI vector_search
├─ Needs database access? → Supabase MCP sql_query
├─ Needs code review? → Llama3 code_review (free)
├─ Needs docstring? → Llama3 generate_docstring (free)
├─ Needs error fix? → Llama3 error_analysis (free)
├─ Needs complex synthesis? → OpenAI with MCP context
└─ Needs deployment? → Git/Cloudflare/Render MCPs
```

---

## Monitoring

Track in `kaitiaki/haiku/haiku_state.json`:

```json
{
  "token_tracking": {
    "openai_spent": "$X",
    "openai_budget_remaining": "$Y",
    "llama3_calls": N,
    "cost_savings_percent": 81,
    "efficiency_trend": "improving"
  }
}
```

---

## Result

**Before:** High context, expensive, slow
**After:** MCP-optimized, Llama3 for free tasks, 81% cheaper

Welcome to token efficiency. 🪶
