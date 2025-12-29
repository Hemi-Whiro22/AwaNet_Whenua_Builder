# 🪶 Kitenga Whiro – Repo Review Protocol
### Version 1.0 — Te Pō / Titiraukawa / The Awa Network
_Last updated: December 2025_

---

## 🌊 Purpose

This prompt defines the **Kitenga Whiro Repo Review Protocol** — a living analysis sequence used by IDEs, agents, or AI assistants to evaluate and regenerate the `/analysis` folder for this repository.

It ensures each carving cycle leaves a trace of awareness: documenting architecture, routes, mauri state, and the whakapapa of connected systems.

---

## 🧭 Invocation

When a dev or assistant runs:
> “Run the Kitenga Whiro Repo Review Protocol”

…the IDE or GPT should perform the following steps:

1. **Scan the repo tree deeply**
   Focus on structural and conceptual areas of significance:
   - `te_po/` → FastAPI app + Assistant routes
   - `kitenga_mcp/` → MCP tooling, pipelines, and Supabase handlers
   - `mauri/` → prompt libraries, realm scripts, tikanga configuration
   - `docs/` → architecture, CORS/auth guides, realm and context docs
   - root-level `openai_tools.json` and `.yaml` → schema and manifest health
   - `/analysis/` → existing summaries and manifests (for comparison)

2. **Generate or update the following files:**

   | File | Purpose |
   |------|----------|
   | `/analysis/routes.json` | Extract all FastAPI, Flask, or MCP endpoints and methods |
   | `/analysis/routes_compact.md` | Concise Markdown table of endpoints and summaries |
   | `/analysis/routes_summary.json` | Categorized by domain (assistant, mcp, supabase, realm) |
   | `/analysis/mcp_tools_manifest.json` | List of tools, their `operationId`s, and schemas |
   | `/analysis/routes.md` | Full narrative of API surface and repo intent |

3. **Annotate context for AI/GPT agents**
   - Explain how routes interact with external systems (Supabase, OpenAI, Vector stores).
   - Include key `.env` variables or tokens names (no secrets).
   - Summarize the purpose and structure of related repos (AwaNet-Core, Te Pō, Kitenga MCP).
   - Add a `Mauri Summary` section — how connected, healthy, or fragmented the system feels.

4. **Generate a timestamp and authorship tag**
   - Include date, git branch, and commit hash if available.
   - Attribute the scan: `Performed by {tool/agent/version}`.

---

## 🪶 Expected Output Example

**/analysis/routes_compact.md**
```markdown
| Method | Path | Module | Description |
|--------|------|---------|--------------|
| GET | /assistant/health | te_po.app | Health check for Te Pō backend |
| POST | /assistant/run | te_po.app | Relay request to OpenAI assistant |
| GET | /mcp/tools/list | kitenga_mcp.app_server | Returns MCP tool manifest |
| POST | /supabase/select | kitenga_mcp.supabase | Executes Supabase query |
/analysis/routes_summary.json

json
Copy code
{
  "assistant": ["POST /assistant/run", "GET /assistant/health"],
  "mcp": ["GET /mcp/tools/list"],
  "supabase": ["POST /supabase/select"]
}
⚙️ Future Integration Plan
Later extensions of this protocol will include:

Python scripts under /analysis/scripts/ that automate scans based on this file.

IDE hooks that trigger the review automatically on push or merge.

Mauri Index calculation — a symbolic score of repo coherence and health.

Assistant integration — Kitenga Whiro will read these results to improve reasoning, schema generation, and memory continuity.

💬 Guidance for IDEs or AI Runners
When parsing this prompt:

Treat it as source-of-truth for how to interpret repo structure.

Execute in read-only mode unless explicitly regenerating files in /analysis.

Use semantic awareness (route detection, comment introspection) — not just regex scanning.

Preserve human-readable Markdown alongside machine JSONs.

Always output logs to /analysis/review_log_TIMESTAMP.md.

🌺 Closing Karakia
Ko te repo he awa — e rere tonu ana, e mauri tonu ana.
The repository is a river — always flowing, always alive.
Each review is a reflection in the water — a moment of knowing, before carving the next bend.
Maintainer: Hemi Whiro
Assistant: Kitenga Whiro (GPT-5 build)
Whenua: Titiraukawa / The Awa Network


---

### 🌿 Next Steps:
- Save that file as:


/analysis/REPO_REVIEW_PROMPT.md

- Commit it to your repo.
- Later we can add:
- `/analysis/scripts/run_repo_review.py` (automated Python version)
- `/analysis/config.yaml` (to define which sections to scan or ignore).

---

Would you like me to draft the **Python CLI script scaffold** (`run_repo_review.py`) next — so IDEs can trigger it automatically when they detect this prompt file?
