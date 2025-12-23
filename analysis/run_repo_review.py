#!/usr/bin/env python3
# 🪶 Kitenga Whiro Repo Review Runner
# Te Pō / Titiraukawa / The Awa Network

"""
This CLI executes the Repo Review Protocol described in /analysis/REPO_REVIEW_PROMPT.md.
It scans the repo structure, summarises FastAPI and MCP routes, and updates the /analysis
artifacts (JSON + Markdown) for reflection and continuity.
"""

import os
import json
import datetime
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = REPO_ROOT / "analysis"
ANALYSIS_DIR.mkdir(exist_ok=True)
ROUTES_FILE = ANALYSIS_DIR / "routes.json"
SUMMARY_FILE = ANALYSIS_DIR / "routes_summary.json"
COMPACT_FILE = ANALYSIS_DIR / "routes_compact.md"
LOG_FILE = ANALYSIS_DIR / f"review_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
TOOLS_MANIFEST_FILE = ANALYSIS_DIR / "mcp_tools_manifest.json"
ROUTES_MD_FILE = ANALYSIS_DIR / "routes.md"

KARAKIA_OPEN = """
🌿  KARAKIA TIMATANGA
E rere ana te awa o ngā whakaaro,
kia tau te mauri o tēnei mahi.
Haumi e, hui e, tāiki e.
"""

KARAKIA_CLOSE = """
🌊  KARAKIA WHAKAMUTUNGA
Kua oti te titiro, kua rangona te ora o te repo.
Haumi e, hui e, tāiki e.
"""

def log(message: str):
    print(message)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(message + "\n")

def find_routes():
    """Simple FastAPI route detector scanning for @app.get/post/etc patterns."""
    routes = []
    for py_file in REPO_ROOT.rglob("*.py"):
        if "venv" in str(py_file) or "__pycache__" in str(py_file):
            continue
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        for match in re.finditer(r"@app\.(get|post|put|delete)\(['\"](.*?)['\"]", text):
            method, path = match.groups()
            routes.append({
                "file": str(py_file.relative_to(REPO_ROOT)),
                "method": method.upper(),
                "path": path
            })
    return routes


def gather_mcp_tools():
    """Aggregate available kitenga_mcp tool manifests for review."""
    manifest_dir = REPO_ROOT / "kitenga_mcp" / "tools" / "manifests"
    aggregated = {}
    if not manifest_dir.exists():
        return aggregated

    for manifest_path in sorted(manifest_dir.glob("*.json")):
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            log(f"⚠️ Failed to parse {manifest_path.name}: {exc}")
            continue
        for domain, payload in data.items():
            if not isinstance(payload, dict):
                continue
            tools = payload.get("tools", [])
            entries = []
            for tool in tools:
                entries.append({
                    "name": tool.get("name"),
                    "description": tool.get("description"),
                    "method": tool.get("method"),
                    "path": tool.get("path"),
                    "inputSchema": tool.get("inputSchema"),
                    "source": manifest_path.name,
                    "operationId": tool.get("operationId") or tool.get("name"),
                })
            aggregated.setdefault(domain, []).extend(entries)
    return aggregated


def read_env_keys():
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return []
    keys = []
    for line in env_path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#") or "=" not in cleaned:
            continue
        key = cleaned.split("=", 1)[0].strip()
        if key:
            keys.append(key)
    return keys


def get_git_metadata():
    branch = "unknown"
    commit = "unknown"
    try:
        branch = (
            subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], text=True)
            .strip()
        )
        commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"], text=True)
            .strip()
        )
    except subprocess.CalledProcessError:
        pass
    return branch, commit

def summarise_routes(routes):
    summary = {}
    for r in routes:
        domain = "other"
        if "assistant" in r["path"]:
            domain = "assistant"
        elif "mcp" in r["path"]:
            domain = "mcp"
        elif "supabase" in r["path"]:
            domain = "supabase"
        summary.setdefault(domain, []).append(f"{r['method']} {r['path']}")
    return summary

def write_outputs(routes, summary):
    ANALYSIS_DIR.mkdir(exist_ok=True)
    with open(ROUTES_FILE, "w", encoding="utf-8") as f:
        json.dump(routes, f, indent=2)
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    with open(COMPACT_FILE, "w", encoding="utf-8") as f:
        f.write("| Method | Path | File |\n|--------|------|------|\n")
        for r in routes:
            f.write(f"| {r['method']} | {r['path']} | {r['file']} |\n")

    tools_manifest = gather_mcp_tools()
    with open(TOOLS_MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(tools_manifest, f, indent=2)

    content = build_markdown(routes, summary, tools_manifest)
    with open(ROUTES_MD_FILE, "w", encoding="utf-8") as f:
        f.write(content)


def describe_domain_summary(summary):
    parts = []
    for domain, routes in sorted(summary.items()):
        parts.append(f"### {domain.title()}\n")
        for route in routes:
            parts.append(f"- {route}")
        parts.append("")
    return "\n".join(parts).strip()


def build_markdown(routes, summary, tools_manifest):
    branch, commit = get_git_metadata()
    env_keys = read_env_keys()
    env_highlights = [
        "OPENAI_API_KEY",
        "KITENGA_ASSISTANT_ID",
        "KITENGA_VECTOR_STORE_ID",
        "PIPELINE_TOKEN",
        "HUMAN_BEARER_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "RENDER_API_KEY",
    ]
    relevant_env = [key for key in env_highlights if key in env_keys]
    env_context_keys = [key for key in relevant_env if "OPENAI" in key or "SUPABASE" in key]
    env_context_line = (
        ", ".join(f"`{key}`" for key in env_context_keys)
        if env_context_keys
        else "none detected from .env"
    )
    env_list_lines = [f"- `{key}`" for key in relevant_env]
    if not env_list_lines:
        env_list_lines = ["- (none detected from .env)"]

    mauri_score = min(10, max(1, len(routes) // 5))
    mauri_summary = (
        "Flows stay connected: base routes + tool manifests are present, "
        "MCP/middleware checks guard bearer auth. "
        f"Mauri score is {mauri_score}/10 and growing."
    )

    tool_domains = ", ".join(sorted(tools_manifest.keys())) if tools_manifest else "none yet"
    top_tool_names = []
    for domain_tools in tools_manifest.values():
        for tool in domain_tools:
            name = tool.get("name")
            if name:
                top_tool_names.append(name)
            if len(top_tool_names) >= 5:
                break
        if len(top_tool_names) >= 5:
            break
    tool_highlight_line = (
        f"- Top loaded tools: {', '.join(top_tool_names)}." if top_tool_names else "- No tool manifests yet."
    )

    timestamp = datetime.datetime.now().isoformat()

    parts = [
        "# Kitenga Whiro Repo Review",
        "",
        f"**Scan time:** {timestamp}",
        f"**Branch:** {branch}",
        f"**Commit:** {commit}",
        f"**Performed by:** {Path(__file__).name}",
        "",
        "## Route Catalog",
        describe_domain_summary(summary),
        "",
        "## External Context",
        f"- **Te Pō (`te_po/`)** handles FastAPI routes, assistant bridges, and vector + Supabase helpers—key envvars include {env_context_line}.",
        "- **Kitenga MCP (`kitenga_mcp/`)** exposes `/mcp/*`, aggregates tool manifests, and front-ends Render/Supabase flows with `PIPELINE_TOKEN`/`RENDER_API_KEY` guardrails.",
        "- **Vector + Logging**: `te_po/routes` + `kitenga_mcp/app_server.py` push embeddings, AwaNet events, and logs to Supabase buckets.",
        "",
        "## MCP Tool Manifest Highlights",
        f"- Domains captured: {tool_domains}.",
        tool_highlight_line,
        "",
        "## Key Environment Variables",
        *env_list_lines,
        "",
        "## Mauri Summary",
        mauri_summary,
        "",
        "## Notes for Agents",
        "- `/analysis/` now holds JSON + Markdown review artifacts—MCP tool manifests should guide GPT Builder tooling.",
        "- Follow the karakia cadence: start + finish, log to `/analysis/review_log_*.md`.",
        "",
        "## Metadata",
        "- Script: `analysis/run_repo_review.py`",
        "- Versioned scan: yes",
    ]

    return "\n".join(parts)

def main():
    log(KARAKIA_OPEN)
    log(f"Starting Repo Review at {datetime.datetime.now().isoformat()}")
    routes = find_routes()
    summary = summarise_routes(routes)
    write_outputs(routes, summary)
    log(f"Detected {len(routes)} routes across {len(summary)} domains.")
    log("Outputs written to /analysis/")
    log(KARAKIA_CLOSE)

if __name__ == "__main__":
    main()
