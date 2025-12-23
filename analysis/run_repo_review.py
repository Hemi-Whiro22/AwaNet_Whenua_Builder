#!/usr/bin/env python3
# 🪶 Kitenga Whiro Repo Review Runner
# Te Pō / Titiraukawa / The Awa Network

"""
This CLI executes the Repo Review Protocol described in /analysis/REPO_REVIEW_PROMPT.md.
It scans the repo structure, summarises FastAPI and MCP routes, and updates the /analysis
artifacts (JSON + Markdown) for reflection and continuity.
"""

import importlib.util
import json
import os
import re
import subprocess
import datetime
from pathlib import Path
from typing import Any, Dict

from analysis import metadata as analysis_metadata

REPO_ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = REPO_ROOT / "analysis"
ANALYSIS_DIR.mkdir(exist_ok=True)
ROUTES_FILE = ANALYSIS_DIR / "routes.json"
SUMMARY_FILE = ANALYSIS_DIR / "routes_summary.json"
COMPACT_FILE = ANALYSIS_DIR / "routes_compact.md"
LOG_FILE = ANALYSIS_DIR / f"review_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
SCRIPT_KEYWORDS = ["real_time", "loop", "event", "awa", "mcp", "orchestrate"]
SCRIPT_EXCLUDE_PARTS = {".venv", "venv", "__pycache__", "node_modules", ".git", "site-packages"}
OPENAPI_CORE = Path("app/openapi-core.json")
TOOLS_MANIFEST_FILE = ANALYSIS_DIR / "mcp_tools_manifest.json"
ROUTES_MD_FILE = ANALYSIS_DIR / "routes.md"
PAYLOAD_SCRIPT_PATH = ANALYSIS_DIR / "te_kaitiaki_o_nga_ahua_kawenga.py"

def _load_payload_module():
    if not PAYLOAD_SCRIPT_PATH.exists():
        return None, "missing script"
    try:
        spec = importlib.util.spec_from_file_location(
            "analysis.te_kaitiaki_o_nga_ahua_kawenga", PAYLOAD_SCRIPT_PATH
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[attr-defined]
        return module, None
    except Exception as exc:
        return None, str(exc)

_PAYLOAD_MODULE, _PAYLOAD_LOAD_ERROR = _load_payload_module()


def _write_json_with_meta(path: Path, data: Any, resource: str) -> Dict[str, Any]:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return analysis_metadata.write_metadata_file(path, resource)


def _write_markdown_with_meta(path: Path, text: str, resource: str) -> None:
    path.write_text(text, encoding="utf-8")
    meta = analysis_metadata.write_metadata_file(path, resource)
    analysis_metadata.append_markdown_footer(path, meta)

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


def scan_scripts():
    scripts = {}
    for keyword in SCRIPT_KEYWORDS:
        for path in REPO_ROOT.rglob(f"*{keyword}*.py"):
            rel = str(path.relative_to(REPO_ROOT))
            if rel.startswith("analysis/"):
                continue
            if SCRIPT_EXCLUDE_PARTS.intersection(path.parts):
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
            uses_fastapi = "FastAPI" in content or "@router" in content
            uses_asyncio = "asyncio" in content or "await" in content
            functions = []
            for line in content.splitlines():
                match = re.match(r"\s*(async\s+)?def\s+([a-zA-Z0-9_]+)\s*\(([^)]*)\)", line)
                if not match:
                    continue
                is_async = bool(match.group(1))
                name = match.group(2)
                signature = match.group(3).strip()
                functions.append({
                    "name": name,
                    "signature": signature,
                    "async": is_async,
                })
            scripts[rel] = {
                "path": rel,
                "functions": functions,
                "fastapi": uses_fastapi,
                "asyncio": uses_asyncio,
            }
    return scripts

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

def write_outputs(routes, summary, scripts):
    ANALYSIS_DIR.mkdir(exist_ok=True)
    _write_json_with_meta(ROUTES_FILE, routes, "analysis_routes_json")
    summary = update_routes_summary(summary)
    _write_json_with_meta(SUMMARY_FILE, summary, "analysis_routes_summary_json")
    compact_lines = ["| Method | Path | File |", "|--------|------|------|"]
    compact_lines += [f"| {r['method']} | {r['path']} | {r['file']} |" for r in routes]
    _write_markdown_with_meta(COMPACT_FILE, "\n".join(compact_lines), "analysis_routes_compact_md")

    tools_manifest = gather_mcp_tools()
    update_manifest_file(tools_manifest, scripts)

    content = build_markdown(routes, summary, tools_manifest, scripts)
    _write_markdown_with_meta(ROUTES_MD_FILE, content, "analysis_routes_md")


def describe_domain_summary(summary):
    parts = []
    for domain, routes in sorted(summary.items()):
        parts.append(f"### {domain.title()}\n")
        for route in routes:
            parts.append(f"- {route}")
        parts.append("")
    return "\n".join(parts).strip()


def load_json_file(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        log(f"⚠️ Failed to parse {path.name}: {exc}")
        return {}


def update_routes_summary(new_summary: dict) -> dict:
    existing = load_json_file(SUMMARY_FILE)
    merged = {}
    for domain in sorted(set(existing) | set(new_summary)):
        existing_routes = set(existing.get(domain, []))
        current_routes = set(new_summary.get(domain, []))
        combined = sorted(existing_routes | current_routes)
        if combined:
            merged[domain] = combined
    return merged


def update_manifest_file(tools_manifest: dict, script_tools: dict):
    existing = load_json_file(TOOLS_MANIFEST_FILE)
    manifest = existing.copy()

    for domain, entries in tools_manifest.items():
        manifest[domain] = entries

    script_entries = []
    for path in sorted(script_tools):
        info = script_tools[path]
        script_entries.append(
            {
                "name": Path(path).name,
                "path": info["path"],
                "functions": info["functions"],
                "fastapi": info["fastapi"],
                "uses_event_loop": info["asyncio"],
            }
        )

    if script_entries:
        manifest["script_tools"] = script_entries
    elif "script_tools" in manifest:
        manifest.pop("script_tools")

    with open(TOOLS_MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    log(f"Updated {TOOLS_MANIFEST_FILE.name} with {len(script_entries)} script tool entries.")
    analysis_metadata.write_metadata_file(TOOLS_MANIFEST_FILE, "analysis_mcp_manifest")


def build_markdown(routes, summary, tools_manifest, script_tools):
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

    script_count = len(script_tools)
    script_lines = []
    if script_count:
        script_lines.append(f"- Script scan captured {script_count} file(s) matching keywords: {', '.join(SCRIPT_KEYWORDS)}.")
        limit = 5
        for path in sorted(script_tools)[:limit]:
            info = script_tools[path]
            func_names = ", ".join(f"{fn['name']}" for fn in info['functions'][:3])
            if len(info["functions"]) > 3:
                func_names += ", ..."
            script_lines.append(
                f"- `{path}` → FastAPI: {info['fastapi']}, event-loop/async: {info['asyncio']}, functions: {func_names or 'n/a'}"
            )
        if script_count > limit:
            script_lines.append(
                f"- ({script_count - limit} more script tool files recorded.)"
            )
    else:
        script_lines.append("- No keyword-matching scripts detected.")

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
        "## Script Tool Scan",
        *script_lines,
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
    scripts = scan_scripts()
    routes = find_routes()
    summary = summarise_routes(routes)
    write_outputs(routes, summary, scripts)
    if _PAYLOAD_MODULE and hasattr(_PAYLOAD_MODULE, "generate_payload_map"):
        try:
            payload_summary = _PAYLOAD_MODULE.generate_payload_map(routes, logger=log, root=REPO_ROOT)
            drift = payload_summary.get("drift", {})
            log(
                f"Payload map: {payload_summary.get('count')} shapes "
                f"(added {len(drift.get('added', []))}, "
                f"removed {len(drift.get('removed', []))}, "
                f"changed {len(drift.get('changed', []))})."
            )
        except Exception as exc:
            log(f"⚠️ Payload mapper failed: {exc}")
    else:
        log(f"⚠️ Payload mapper unavailable: {_PAYLOAD_LOAD_ERROR}")
    log(f"Detected {len(routes)} routes across {len(summary)} domains.")
    log(f"Script scan keywords {', '.join(SCRIPT_KEYWORDS)} touched {len(scripts)} file(s).")
    log("Outputs written to /analysis/")
    log(KARAKIA_CLOSE)

if __name__ == "__main__":
    main()
