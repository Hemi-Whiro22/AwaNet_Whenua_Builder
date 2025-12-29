#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌿  TE KAITIAKI O NGĀ ĀHUA KAWENGA
Guardian of Payload Forms
─────────────────────────────
Scans repo for FastAPI routes and Pydantic/dataclass definitions
and publishes a payload registry for the AwaNet/Kitenga bridges.
"""

import ast
import asyncio
import datetime
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

ANALYSIS_DIR = Path(__file__).resolve().parent
ROOT_DIR = ANALYSIS_DIR.parent
sys.path.append(str(ROOT_DIR))
from te_po.utils.supabase_client import get_client  # noqa: E402
from taonga import metadata as analysis_metadata  # noqa: E402
PAYLOAD_JSON = ANALYSIS_DIR / "payload_map.json"
PAYLOAD_MD = ANALYSIS_DIR / "payload_map.md"
DRIFT_LOG = ANALYSIS_DIR / \
    f"review_log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_payload.md"
ROUTES_JSON = ANALYSIS_DIR / "routes.json"
ROUTES_SUMMARY = ANALYSIS_DIR / "routes_summary.json"
ROUTES_COMPACT = ANALYSIS_DIR / "routes_compact.md"
ROUTES_MD = ANALYSIS_DIR / "routes.md"
MCP_TOOLS_MANIFEST = ANALYSIS_DIR / "mcp_tools_manifest.json"
LATEST_LOGS_LIMIT = 3
ANALYSIS_ARTIFACT_DEFS = [
    ("payload_map_json", PAYLOAD_JSON, "json"),
    ("payload_map_md", PAYLOAD_MD, "markdown"),
    ("routes_json", ROUTES_JSON, "json"),
    ("routes_summary", ROUTES_SUMMARY, "json"),
    ("routes_compact", ROUTES_COMPACT, "markdown"),
    ("routes_md", ROUTES_MD, "markdown"),
    ("mcp_tools_manifest", MCP_TOOLS_MANIFEST, "json"),
]

REALM_README_CONFIGS = [
    {
        "id": "te_po",
        "title": "Te Pō – AwaNet Backend Realm",
        "root": ROOT_DIR / "te_po",
        "purpose": "Te Pō houses the FastAPI-driven intelligence, pipelines, and OCR services that power AwaNet.",
        "reason": "clarify the backend role and surface the state, manifest, and pipeline touchpoints so our kaitiaki tooling and Codex agents can keep context fresh while we reorganise the wider awa.",
        "structure": [
            {"path": "app.py / main.py",
                "description": "Expose the FastAPI app that federates routes, helpers, and diagnostics."},
            {"path": "core/, services/, pipeline/",
                "description": "Encapsulate domain logic, OpenAI workflows, Supabase connectors, and automated jobs."},
            {"path": "mauri/, state/, storage/",
                "description": "Hold guarded context, carving logs, and Supabase schema/state definitions."},
            {"path": "scripts/, tests/",
                "description": "Utility helpers, dev scripts, and pytest suites that keep the backend resilient."},
            {"path": "analysis/, docs/ (root)",
             "description": "Explain architecture, manifest intent, and route summaries for humans and kaitiaki."},
        ],
        "how_to_run": {
            "dev_start": ["uvicorn te_po.main:app --reload --host 0.0.0.0 --port 8010"],
            "tests": ["pytest"],
            "key_env": [
                "OPENAI_API_KEY",
                "KITENGA_ASSISTANT_ID",
                "KITENGA_VECTOR_STORE_ID",
                "OPENAI_BASE_URL",
                "SUPABASE_URL",
                "SUPABASE_SERVICE_ROLE_KEY",
                "TE_PO_STATE_BUCKET",
            ],
        },
        "main_files": [
            {"path": "core/, services/",
                "purpose": "Business logic, assistant orchestration, OCR, vector helpers."},
            {"path": "pipeline/, migrations/",
                "purpose": "ETL jobs, data drift detection, schema updates."},
            {"path": "state/, mauri/, storage/",
                "purpose": "Context snapshots, carving logs, Supabase/pgvector state."},
            {"path": "scripts/, tests/",
                "purpose": "Dev tools, export helpers, pytest suites."},
            {"path": "analysis/, docs/ (root)",
             "purpose": "Route catalogs, sync scripts, and architecture intent."},
        ],
        "connects_to": [
            "Supabase vector tables",
            "OpenAI APIs",
            "kitenga_mcp tooling",
            "mauri/state/te_po_state.json",
            "analysis root reviews",
        ],
        "consumed_by": [
            "te_ao dashboards",
            "te_hau CLI proxies",
            "analysis sync jobs",
            "external UIs needing translation/OCR",
        ],
        "why_structure": [
            "The split keeps API logic, memory/state snapshots, and automation tooling in well-defined folders so updates stay readable.",
            "Manifest and state directories keep kaitiaki context packaged for Codex and downstream syncs.",
            "`analysis/` + `docs/` act as the living map so the backend intent is discoverable before we move code around.",
        ],
        "kaitiaki_notes": [
            "After touching routes, tools, or manifests, rerun /analysis/kaitiaki_context_sync.py and update /analysis/routes_summary.json so the wake and memory stay aligned.",
            "Keep mauri/state/te_po_state.json and the Supabase schema snapshots in sync with any schema/pipeline changes.",
            "Document architectural shifts in docs/architecture/ and docs/context/CONTEXT.md so future kaitiaki inherit the intent.",
        ],
    },
    {
        "id": "te_hau",
        "title": "Te Hau – AwaNet Automation Realm",
        "root": ROOT_DIR / "te_hau",
        "purpose": "Te Hau orchestrates CLI tooling, automation, and proxy layers that keep Te Pō reachable for developers and other kaitiaki.",
        "reason": "document how the CLI, event routing, and manifest generation bridge the backend and frontend so we can automate context syncs without losing the wai/tikanga embedded in this layer.",
        "structure": [
            {"path": "app.py", "description": "FastAPI bridge that relays Te Ao/Kitenga requests to Te Pō and emits events onto the awa bus."},
            {"path": "cli/, core/, services/",
                "description": "CLI commands, kaitiaki orchestration helpers, request emitters, and context stores."},
            {"path": "mauri/, state.yaml, mauri/scripts/",
                "description": "Templates and compiled manifests that define agent memory for automation tasks."},
            {"path": "scripts/, start_tehau.sh",
                "description": "Boot scripts that wire Te Hau into the infrastructure and capture logs."},
            {"path": "docs/, analysis/ (root)",
             "description": "Share knowledge of proxies, automation intent, and context sync guidance with other realms."},
        ],
        "how_to_run": {
            "dev_start": ["uvicorn te_hau.app:app --reload --host 0.0.0.0 --port 8020"],
            "tests": ["pytest"],
            "key_env": [
                "TE_HAU_MAURI_PATH",
                "TE_PO_URL",
                "KITENGA_PORT",
                "SUPABASE_URL",
                "SUPABASE_SERVICE_ROLE_KEY",
                "CF_TUNNEL_ID",
                "CF_TUNNEL_NAME",
                "CF_TUNNEL_HOSTNAME",
                "OPENAI_API_KEY",
            ],
        },
        "main_files": [
            {"path": "cli/, core/, services/",
                "purpose": "CLI commands, orchestration helpers, awa bus emitters, OCR/proxy clients."},
            {"path": "start_tehau.sh, Dockerfile",
                "purpose": "Launch scripts that wire Te Hau into the wider CD pipeline."},
            {"path": "mauri/, state.yaml, mauri/scripts/",
                "purpose": "Templates and compiled manifests capturing automation memory and agent identities."},
            {"path": "scripts/, kitenga_whakairo/",
                "purpose": "Utility scripts and carving tools used by governance kaitiaki."},
            {"path": "docs/, analysis/ (root)",
             "purpose": "Explanation of proxies, automation intent, and context sync guidance."},
        ],
        "connects_to": [
            "Te Pō APIs",
            "kitenga_mcp",
            "Supabase for event persistence",
            "Local mauri store for agent memory",
        ],
        "consumed_by": [
            "Te Ao UI",
            "Kitenga CLI consumers",
            "Codex/IDE assistants",
            "Automation jobs that inject context or emit events",
        ],
        "why_structure": [
            "Separating CLI tooling, proxies, and mauri compilations keeps automation logic simple to audit and adjust as we restructure the awa.",
            "The manifest/state folders ensure every change is mirrored in the kaitiaki templates that feed other realms.",
            "Scripts and start_tehau.sh centralize environment loading so Te Hau can keep emitting events even when infrastructure shifts.",
        ],
        "kaitiaki_notes": [
            "After touching CLI endpoints, rerun mauri/scripts/compile_kaitiaki.py so every automation kaitiaki manifest aligns with the new intent.",
            "Keep /analysis/routes_summary.json and /analysis/mcp_tools_manifest.json updated with any new proxies, CLI routes, or tool loaders that Te Hau introduces.",
            "Use docs/context/CONTEXT.md and docs/guides/GUARDIANS.md to narrate changes so future kaitiaki understand the automation contracts.",
        ],
    },
    {
        "id": "te_ao",
        "title": "Te Ao – AwaNet Frontend Realm",
        "root": ROOT_DIR / "te_ao",
        "purpose": "Te Ao delivers the React/Vite dashboard and overview UI that surfaces OCR, translation, and state awareness for whānau and kaitiaki.",
        "reason": "capture the UI’s purpose, connection points, and memory dependencies so we can automate documentation for every realm before we start moving code.",
        "structure": [
            {"path": "src/", "description": "React entrypoints, state management utilities, and UI components that talk to Te Pō and Te Hau."},
            {"path": "config/, state/", "description": "Static config files plus the cached te_ao_state.json that keeps the interface aligned with the backend."},
            {"path": "public/, dist/",
                "description": "Static assets and production build output for deployments."},
            {"path": "package.json, node_modules/",
                "description": "Frontend tooling and dependencies managed by Vite and Tailwind."},
            {"path": "docs/, analysis/ (root)",
             "description": "Document how the UI fits into the wider awa and record any new routes or endpoints."},
        ],
        "how_to_run": {
            "dev_start": [
                "npm install",
                "npm run dev -- --host 0.0.0.0 --port 5173",
            ],
            "tests": ["npm run build", "npm run preview"],
            "key_env": [
                "VITE_API_BASE_URL",
                "VITE_TE_HAU_PROXY_URL",
                "VITE_SUPABASE_URL",
                "VITE_SUPABASE_ANON_KEY",
                "VITE_KITENGA_PORT",
            ],
        },
        "main_files": [
            {"path": "src/", "purpose": "React components, state hooks, and API utilities targeting Te Pō/Te Hau."},
            {"path": "state/te_ao_state.json",
                "purpose": "Cached context that informs UI flows and bookmarks."},
            {"path": "config/, public/",
                "purpose": "Theme/config presets plus static assets (icons, logos)."},
            {"path": "dist/", "purpose": "Production bundle produced by npm run build."},
            {"path": "docs/, analysis/ (root)",
             "purpose": "Human-readable architecture, route summaries, and automation expectations."},
        ],
        "connects_to": [
            "Te Pō FastAPI routes",
            "Te Hau proxies",
            "Supabase insights",
            "Mauri/state files that keep UI state durable",
        ],
        "consumed_by": [
            "Product teams",
            "Kaitiaki",
            "Automation agents relying on the UI to monitor health, translation, and pipeline status",
        ],
        "why_structure": [
            "The split between UI code, state snapshots, and production/dist assets keeps build tooling tidy and makes it obvious where to update the front-end when APIs evolve.",
            "state/ holds the enduring context that Te Ao needs so the UI can replay the awa state even if the backend is still warming up.",
            "Referencing docs/ and analysis/ ensures the UI is described in the same language as the other realms.",
        ],
        "kaitiaki_notes": [
            "Keep state/te_ao_state.json and mauri/state/te_ao_state.json synced whenever new UI flows or statuses are added.",
            "When routes used in the UI change, update /analysis/routes_summary.json and rerun /analysis/kaitiaki_context_sync.py so automations know about the new surface area.",
            "Use docs/context/CONTEXT.md and docs/guides/DEVELOPMENT.md to explain how the UI should be consumed by future kaitiaki dashboards.",
        ],
    },
]

KARAKIA_TIMATANGA = "🌿  KARAKIA TIMATANGA"
KARAKIA_WHAKAMUTUNGA = "🌊  KARAKIA WHAKAMUTUNGA"

EXCLUDE_DIRS = {".venv", "venv", "node_modules", "__pycache__", ".git"}
ROUTE_METHODS = {"get", "post", "put", "patch", "delete"}
ALLOWED_SCHEMAS = {"public", "graphql_public", "kitenga"}
REGISTRY_SCHEMA = "kitenga"
REGISTRY_TABLE = "payload_registry"
MODEL_MARKERS = {"BaseModel", "BaseSettings",
                 "pydantic.BaseModel", "pydantic.BaseSettings"}


def _default_logger(message: str) -> None:
    print(message)
    with open(DRIFT_LOG, "a", encoding="utf-8") as handle:
        handle.write(message + "\n")


def _safe_unparse(node: Optional[ast.AST]) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node).strip()
    except Exception:
        return ""


def _should_skip(path: Path) -> bool:
    return bool(set(path.parts) & EXCLUDE_DIRS)


def _module_name_from_path(path: Path, root: Path) -> str:
    rel = path.relative_to(root).with_suffix("")
    return ".".join(rel.parts)


def _get_decorator_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _collect_models(root: Path) -> Dict[str, Dict[str, Any]]:
    models: Dict[str, Dict[str, Any]] = {}
    for py_file in root.rglob("*.py"):
        if _should_skip(py_file):
            continue
        try:
            text = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(text)
        except Exception:
            continue
        module_name = _module_name_from_path(py_file, root)
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            bases = {_safe_unparse(base)
                     for base in node.bases if _safe_unparse(base)}
            decs = set()
            for dec in node.decorator_list:
                target = dec.func if isinstance(dec, ast.Call) else dec
                name = _get_decorator_name(target)
                if name:
                    decs.add(name)
            is_model = bool(bases & MODEL_MARKERS) or "dataclass" in decs
            if not is_model:
                continue
            fields = []
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    fields.append({
                        "name": stmt.target.id,
                        "type": _safe_unparse(stmt.annotation),
                        "default": _safe_unparse(stmt.value)
                    })
                elif isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name):
                            fields.append({
                                "name": target.id,
                                "type": "",
                                "default": _safe_unparse(stmt.value)
                            })
            info = {
                "name": node.name,
                "module": module_name,
                "fields": fields,
                "kind": "dataclass" if "dataclass" in decs else "pydantic"
            }
            models[(module_name, node.name)] = info
            if node.name not in models:
                models[node.name] = info
    return models


def _build_example(fields: List[Dict[str, Any]]) -> Dict[str, Any]:
    example = {}
    for field in fields:
        hint = (field.get("type") or "").lower()
        if "int" in hint or "float" in hint or "decimal" in hint:
            example[field["name"]] = 0
        elif "bool" in hint:
            example[field["name"]] = False
        elif "list" in hint or "tuple" in hint:
            example[field["name"]] = []
        elif "dict" in hint or "mapping" in hint:
            example[field["name"]] = {}
        elif hint:
            example[field["name"]] = f"example_{field['name']}"
        else:
            example[field["name"]] = "example"
    return example


def _normalize_signature(parameters: List[Dict[str, Any]]) -> Tuple[str, ...]:
    return tuple(sorted(f"{param['name']}:{param.get('annotation', '') or param.get('model', '') or 'any'}" for param in parameters))


def _compute_drift(previous: List[Dict[str, Any]], current: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    def _key(entry: Dict[str, Any]) -> str:
        return f"{entry['method']} {entry['path']}::{entry['function']}"

    prev_map = {(_key(entry)): entry for entry in previous}
    curr_map = {(_key(entry)): entry for entry in current}
    added = [f"{entry['method']} {entry['path']}" for key,
             entry in curr_map.items() if key not in prev_map]
    removed = [f"{entry['method']} {entry['path']}" for key,
               entry in prev_map.items() if key not in curr_map]
    changed = []
    for key in curr_map:
        if key in prev_map:
            prev_sig = _normalize_signature(
                prev_map[key].get("parameters", []))
            curr_sig = _normalize_signature(
                curr_map[key].get("parameters", []))
            if prev_sig != curr_sig:
                route_label = key.replace("::", " → ")
                changed.append(route_label)
    return {"added": sorted(added), "removed": sorted(removed), "changed": sorted(changed)}


def _build_payload_markdown(summary: Dict[str, Any]) -> str:
    lines: List[str] = [
        "# Te Kaitiaki o ngā Āhua Kawenga — Payload Registry", ""]
    lines.append(f"**Scan time:** {summary['timestamp']}")
    lines.append(f"**Mauri score:** {summary['mauri_score']} / 10")
    lines.append("")
    lines.append("## Realm Whakapapa")
    realm = summary.get("realm", {})
    for key in sorted(realm):
        lines.append(f"- {key}: {realm[key]}")
    lines.append("")
    lines.append("## Payload Shapes")
    for entry in summary.get("payload_shapes", []):
        lines.append(
            f"### {entry['method']} {entry['path']} → {entry['function']}")
        lines.append(f"- Module: {entry['module']}")
        lines.append(f"- Whakapapa path: {entry['whakapapa_path']}")
        lines.append(
            f"- Registered route: {'yes' if entry.get('registered') else 'no'}")
        lines.append(f"- Mauri score: {entry.get('mauri_score', 1)}")
        params = entry.get("parameters", [])
        if params:
            lines.append("- Parameters:")
            for param in params:
                desc = f"  - {param['name']} ({param.get('annotation') or param.get('model') or 'any'})"
                if param.get("model_fields"):
                    desc += " → fields: " + \
                        ", ".join(
                            f"{field['name']}" for field in param['model_fields'])
                lines.append(desc)
        if entry.get("example_payload"):
            lines.append("- Example payload:")
            lines.append("```json")
            lines.append(json.dumps(
                entry["example_payload"], indent=2, ensure_ascii=False))
            lines.append("```")
        lines.append("")
    drift = summary.get("drift", {})
    lines.append("## Drift Observations")
    for key in ("added", "removed", "changed"):
        values = drift.get(key, [])
        lines.append(f"- {key.title()}: {len(values)}")
        for line in values:
            lines.append(f"  - {line}")
    lines.append("")
    lines.append("## Notes")
    if drift.get("added") or drift.get("removed") or drift.get("changed"):
        lines.append(
            "- Schema drift detected — keep this artifact aligned with route changes.")
    lines.append(
        "- Karakia: E rere ana te awa o ngā whakaaro, kia tau te mauri o tēnei mahi. Haumi e, hui e, tāiki e.")
    return "\n".join(lines)


def _write_payload_markdown(summary: Dict[str, Any]) -> None:
    text = _build_payload_markdown(summary)
    PAYLOAD_MD.write_text(text, encoding="utf-8")
    metadata = analysis_metadata.write_metadata_file(
        PAYLOAD_MD, "analysis_payload_map_md")
    analysis_metadata.append_markdown_footer(PAYLOAD_MD, metadata)


def _write_payload_json(summary: Dict[str, Any]) -> None:
    PAYLOAD_JSON.write_text(json.dumps(
        summary, indent=2, ensure_ascii=False), encoding="utf-8")
    analysis_metadata.write_metadata_file(
        PAYLOAD_JSON, "analysis_payload_map_json")


def _maybe_sync_supabase(summary: Dict[str, Any], logger: Any) -> None:
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not supabase_key:
        return
    logger("⚡ Supabase credentials detected — summary vector syncing is pending implementation.")


def _format_code_block(lines: List[str]) -> List[str]:
    block: List[str] = ["```sh"]
    block.extend(lines)
    block.append("```")
    return block


def _build_readme_text(config: Dict[str, Any]) -> str:
    lines: List[str] = [f"# {config['title']}", ""]
    lines.extend(
        ["## Purpose", "", f"{config['purpose']} **Reason for recent changes:** {config['reason']}", ""])
    lines.append("## Structure")
    for entry in config["structure"]:
        lines.append(f"- **`{entry['path']}`**: {entry['description']}")
    lines.append("")
    how = config.get("how_to_run", {})
    lines.append("## How to Run")
    dev_start = how.get("dev_start")
    if dev_start:
        lines.append("- **Dev Start:**")
        lines.extend(_format_code_block(dev_start))
    tests = how.get("tests")
    if tests:
        lines.append("")
        lines.append("- **Tests:**")
        lines.extend(_format_code_block(tests))
    key_env = how.get("key_env", [])
    if key_env:
        lines.append("")
        lines.append("- **Key Env Vars:**")
        for env in key_env:
            lines.append(f"  - {env}")
    lines.append("")
    lines.append("### Main Files/Folders")
    lines.append("| Path | Purpose |")
    lines.append("| --- | --- |")
    for entry in config.get("main_files", []):
        lines.append(f"| `{entry['path']}` | {entry['purpose']} |")
    lines.append("")
    lines.append("## How it Connects")
    connects_to = config.get("connects_to", [])
    consumed_by = config.get("consumed_by", [])
    if connects_to:
        lines.append(f"- **Connects to:** {', '.join(connects_to)}")
    if consumed_by:
        lines.append(f"- **Consumed by:** {', '.join(consumed_by)}")
    lines.append("")
    lines.append("## Why This Structure?")
    for inst in config.get("why_structure", []):
        lines.append(f"- {inst}")
    lines.append("")
    lines.append("## Kaitiaki Notes")
    for note in config.get("kaitiaki_notes", []):
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def regenerate_realm_readmes(logger: Any) -> None:
    log = logger or _default_logger
    log("🌿  KARAKIA TIMATANGA — regenerating realm READMEs")
    for config in REALM_README_CONFIGS:
        readme_path = config["root"] / "README.md"
        readme_path.parent.mkdir(parents=True, exist_ok=True)
        readme_path.write_text(_build_readme_text(config), encoding="utf-8")
        log(f"✅ Updated {readme_path.relative_to(ROOT_DIR)}")
    log("🌊  KARAKIA WHAKAMUTUNGA — realm README regeneration complete")


def _read_json_file(path: Path, logger: Any) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger(f"⚠️ Failed to load JSON from {path}: {exc}")
        return None


def _latest_review_logs(limit: int = LATEST_LOGS_LIMIT) -> List[Path]:
    logs = sorted(ANALYSIS_DIR.glob("review_log_*.md"),
                  key=lambda p: p.stat().st_mtime)
    return logs[-limit:]


def _prepare_analysis_artifacts(summary: Dict[str, Any], logger: Any) -> List[Dict[str, Any]]:
    timestamp = datetime.datetime.utcnow().isoformat()
    artifacts: List[Dict[str, Any]] = []
    for name, path, fmt in ANALYSIS_ARTIFACT_DEFS:
        if not path.exists():
            continue
        content = None
        text_content = None
        if fmt == "json":
            content = _read_json_file(path, logger)
            if content is None:
                continue
        else:
            text_content = path.read_text(encoding="utf-8", errors="ignore")
        artifacts.append({
            "name": name,
            "format": fmt,
            "content": content,
            "text": text_content,
            "metadata": {
                "path": str(path.relative_to(ROOT_DIR)),
                "generated_at": timestamp,
                "source": "analysis_runner",
                "summary_timestamp": summary.get("timestamp"),
            },
        })
    for log_path in _latest_review_logs():
        artifacts.append({
            "name": log_path.stem,
            "format": "markdown",
            "content": None,
            "text": log_path.read_text(encoding="utf-8", errors="ignore"),
            "metadata": {
                "path": str(log_path.relative_to(ROOT_DIR)),
                "generated_at": timestamp,
                "source": "review_log",
            },
        })
    return artifacts


async def _sync_analysis_documents(artifacts: List[Dict[str, Any]], logger: Any) -> List[str]:
    client = get_client()
    if client is None or not artifacts:
        return []
    doc_ref = client.schema(REGISTRY_SCHEMA).table("analysis_documents")
    synced: List[str] = []
    for artifact in artifacts:
        payload = {
            "name": artifact["name"],
            "format": artifact["format"],
            "content": artifact["content"],
            "text_content": artifact["text"],
            "metadata": artifact["metadata"],
        }

        def _upsert():
            return doc_ref.upsert(payload, on_conflict="name").execute()
        try:
            resp = await asyncio.to_thread(_upsert)
        except Exception as exc:
            logger(f"⚠️ Document sync failed for {artifact['name']}: {exc}")
            continue
        error = getattr(resp, "error", None)
        if error:
            logger(f"⚠️ Document upsert error for {artifact['name']}: {error}")
            continue
        synced.append(artifact["name"])
    return synced


def _build_analysis_summary(summary: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "timestamp": summary.get("timestamp"),
        "mauri_score": summary.get("mauri_score"),
        "payload_shapes_count": len(summary.get("payload_shapes", [])),
        "drift": summary.get("drift", {}),
        "realm": summary.get("realm", {}),
    }


async def _log_sync_event(
    client: Any,
    summary: Dict[str, Any],
    synced_tables: List[str],
    document_refs: List[str],
    logger: Any,
) -> None:
    if client is None:
        return
    record = {
        "run_id": summary.get("timestamp"),
        "event_type": "repo_review",
        "event_time": datetime.datetime.utcnow().isoformat(),
        "synced_tables": synced_tables,
        "document_refs": document_refs,
        "analysis_summary": _build_analysis_summary(summary),
        "payload_count": len(summary.get("payload_shapes", [])),
    }
    event_ref = client.schema(REGISTRY_SCHEMA).table("analysis_sync_events")

    def _insert():
        return event_ref.insert(record).execute()

    try:
        await asyncio.to_thread(_insert)
    except Exception as exc:
        logger(f"⚠️ Failed to log sync event: {exc}")


async def full_supabase_sync(summary: Dict[str, Any], logger: Any) -> Dict[str, Any]:
    client = get_client()
    logger("🌿  KARAKIA TIMATANGA — Supabase sync")
    if client is None:
        logger("⚠️ Supabase client not configured; skipping payload registry sync.")
        logger("🌊  KARAKIA WHAKAMUTUNGA — Supabase sync aborted")
        return {"synced_tables": [], "error": "client_missing"}

    def _discover_tables():
        for fn in ("list_tables_ext", "list_tables_all", "list_public_tables"):
            try:
                resp = getattr(client, "rpc")(fn).execute()
                rows = getattr(resp, "data", None) or []
                if not rows:
                    continue
                if isinstance(rows[0], str):
                    return sorted(rows)
                if isinstance(rows[0], dict):
                    if "table_name" in rows[0] and "schema_name" in rows[0]:
                        filtered = set()
                        for r in rows:
                            schema = r.get("schema_name", "public")
                            table = r.get("table_name")
                            if table and schema in ALLOWED_SCHEMAS:
                                filtered.add(f"{schema}.{table}")
                        return sorted(filtered)
                    return sorted(
                        {r.get("table_name") or r.get("tablename")
                         for r in rows if r.get("table_name") or r.get("tablename")}
                    )
            except Exception as exc:
                logger(f"[warn] table discovery via {fn} failed: {exc}")
        logger("[warn] table discovery failed: no RPC helper available")
        return []

    def _sample_columns(table: str):
        schema_name = None
        table_name = table
        if "." in table:
            schema_name, table_name = table.split(".", 1)
        ref = client.table(table_name)
        if schema_name:
            try:
                ref = client.schema(schema_name).table(table_name)
            except Exception:
                pass
        resp = ref.select("*").limit(1).execute()
        sample = getattr(resp, "data", None) or []
        if sample and isinstance(sample[0], dict):
            return list(sample[0].keys())
        return []

    tables = await asyncio.to_thread(_discover_tables)
    if not tables:
        logger("⚠️ Supabase table discovery returned nothing; aborting payload sync.")
        logger("🌊  KARAKIA WHAKAMUTUNGA — Supabase sync complete")
        return {"synced_tables": [], "error": "no_tables"}

    try:
        client.schema(REGISTRY_SCHEMA).table(
            REGISTRY_TABLE).select("table_name").limit(1).execute()
    except Exception as exc:
        logger(
            f"⚠️ Supabase registry table {REGISTRY_SCHEMA}.{REGISTRY_TABLE} missing: {exc}")
        logger("🌊  KARAKIA WHAKAMUTUNGA — Supabase sync incomplete")
        return {"synced_tables": [], "error": "registry_missing"}

    analysis_summary = _build_analysis_summary(summary)
    artifacts = _prepare_analysis_artifacts(summary, logger)
    document_refs: List[str] = []
    if artifacts:
        document_refs = await _sync_analysis_documents(artifacts, logger)

    registry_ref = client.schema(REGISTRY_SCHEMA).table(REGISTRY_TABLE)
    synced = []
    payload_routes = summary.get("payload_shapes", [])
    for table in sorted(tables):
        column_names = await asyncio.to_thread(_sample_columns, table)
        columns = [{"name": name, "type": "unknown"} for name in column_names]
        routes = [
            entry["path"]
            for entry in payload_routes
            if table.lower() in entry.get("path", "").lower()
        ]
        schema_name = table.split(".", 1)[0] if "." in table else "public"
        record = {
            "table_name": table,
            "routes": routes,
            "columns": columns,
            "synced_at": datetime.datetime.utcnow().isoformat(),
            "mauri_score": summary.get("mauri_score"),
            "schema_name": schema_name,
            "policy_info": [],
            "analysis_summary": analysis_summary,
            "document_refs": document_refs or None,
        }

        def _upsert():
            return registry_ref.upsert(record, on_conflict="table_name").execute()

        try:
            resp = await asyncio.to_thread(_upsert)
        except Exception as exc:
            logger(f"⚠️ Supabase upsert error for {table}: {exc}")
            continue
        error = getattr(resp, "error", None)
        status = getattr(resp, "status_code", None)
        resp_data = getattr(resp, "data", None)
        if error or (status is not None and status >= 400):
            logger(
                f"⚠️ Supabase upsert skipped for {table}: status={status}, error={error}")
            continue
        if status is None and resp_data is None:
            logger(
                f"⚠️ Supabase upsert skipped for {table}: no status/data returned")
            continue
        synced.append(table)

    logger(f"⚡ Supabase sync wrote {len(synced)} tables to payload_registry: {', '.join(synced[:5])}" + (
        f", ... (+{len(synced)-5} more)" if len(synced) > 5 else ""))
    await _log_sync_event(client, summary, synced, document_refs, logger)
    logger("🌊  KARAKIA WHAKAMUTUNGA — Supabase sync complete")
    return {"synced_tables": synced}


def generate_payload_map(routes: Optional[Iterable[Dict[str, Any]]] = None,
                         logger: Optional[Any] = None,
                         root: Optional[Path] = None) -> Dict[str, Any]:
    root_path = (Path(root) if root else ROOT_DIR).resolve()
    log = logger or _default_logger
    log(KARAKIA_TIMATANGA)
    log("Starting payload scan for Te Pō routes and models.")
    lush_routes = []
    input_routes = list(routes) if routes else []
    if not input_routes:
        candidate = ANALYSIS_DIR / "routes.json"
        if candidate.exists():
            try:
                input_routes = json.loads(
                    candidate.read_text(encoding="utf-8"))
            except Exception:
                input_routes = []
    registered = {(route.get("method"), route.get("path"))
                  for route in input_routes}
    models = _collect_models(root_path)

    payload_shapes: List[Dict[str, Any]] = []
    for py_file in root_path.rglob("*.py"):
        if _should_skip(py_file):
            continue
        try:
            text = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(text)
        except Exception:
            continue
        module_name = _module_name_from_path(py_file, root_path)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                        continue
                    method = decorator.func.attr.lower()
                    if method not in ROUTE_METHODS:
                        continue
                    path = ""
                    if decorator.args:
                        first = decorator.args[0]
                        if isinstance(first, ast.Constant) and isinstance(first.value, str):
                            path = first.value
                    for keyword in decorator.keywords:
                        if keyword.arg in {"path", "route"} and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                            path = keyword.value.value
                    if not path:
                        continue
                    parameters = []
                    for arg in node.args.args:
                        if arg.arg in {"self", "cls"}:
                            continue
                        annotation_text = _safe_unparse(arg.annotation)
                        model_info = None
                        if annotation_text:
                            model_key = (
                                module_name, annotation_text.split(".")[-1])
                            model_info = models.get(model_key) or models.get(
                                annotation_text.split(".")[-1])
                        param_entry: Dict[str, Any] = {
                            "name": arg.arg,
                            "annotation": annotation_text,
                        }
                        if model_info:
                            param_entry["model"] = model_info["name"]
                            param_entry["model_fields"] = model_info["fields"]
                            param_entry["example_payload"] = _build_example(
                                model_info["fields"])
                        parameters.append(param_entry)
                    route_entry = {
                        "path": path,
                        "method": method.upper(),
                        "function": node.name,
                        "module": module_name,
                        "whakapapa_path": str(py_file.relative_to(root_path)),
                        "parameters": parameters,
                        "registered": (method.upper(), path) in registered,
                        "mauri_score": min(10, 1 + len(parameters)),
                    }
                    example_payload = {}
                    for param in parameters:
                        example = param.get("example_payload")
                        if example:
                            example_payload[param["name"]] = example
                    if example_payload:
                        route_entry["example_payload"] = example_payload
                    payload_shapes.append(route_entry)
    drift = _compute_drift(
        (json.loads(PAYLOAD_JSON.read_text(encoding="utf-8"))
         if PAYLOAD_JSON.exists() else {}).get("payload_shapes", []),
        payload_shapes
    )
    realm_data = {}
    realm_file = ROOT_DIR / "realm.json"
    if realm_file.exists():
        try:
            realm_data = json.loads(realm_file.read_text(encoding="utf-8"))
        except Exception:
            realm_data = {}
    summary = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "mauri_score": min(10, len(payload_shapes)),
        "realm": realm_data,
        "payload_shapes": payload_shapes,
        "drift": drift
    }
    _write_payload_json(summary)
    _write_payload_markdown(summary)
    _maybe_sync_supabase(summary, log)
    try:
        asyncio.run(full_supabase_sync(summary, log))
    except RuntimeError as exc:
        log(f"⚠️ Full Supabase sync bypassed: {exc}")
    log(
        f"Payload map persists {len(payload_shapes)} shapes; drift added {len(drift['added'])}, removed {len(drift['removed'])}, changed {len(drift['changed'])}.")
    regenerate_realm_readmes(log)
    log(KARAKIA_WHAKAMUTUNGA)
    return {"count": len(payload_shapes), "drift": drift}


if __name__ == "__main__":
    generate_payload_map()
    _default_logger("✅ Te Kaitiaki scan complete.")
