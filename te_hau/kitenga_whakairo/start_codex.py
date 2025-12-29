import os
import sys
from pathlib import Path

from dotenv import load_dotenv

import anyio
from mcp.server.fastmcp import FastMCP

from mauri.te_kete.load_manifest import load_manifest

# Add repo root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


def load_environment():
    """Load Whakairo env with fallbacks."""
    env_candidates = []
    env_override = os.getenv("DOTENV_PATH")
    if env_override:
        env_candidates.append(PROJECT_ROOT / env_override)

    env_candidates.extend(
        [
            Path(__file__).parent / ".env.whakairo",
            PROJECT_ROOT / ".env.whakairo",
            PROJECT_ROOT / "te_po" / "core" / ".env",
            PROJECT_ROOT / ".env",
        ]
    )

    loaded = None
    for path in env_candidates:
        if path.exists():
            load_dotenv(dotenv_path=path, override=False)
            loaded = path
            break

    if loaded:
        print(f"💠 Loaded env from: {loaded}")
    else:
        load_dotenv()
        print("💠 Loaded env from system")

    return loaded


ENV_FILE = load_environment()

from te_hau.kitenga_whakairo.tools.supabase_tools import (  # noqa: E402
    supabase_insert,
    supabase_search,
    supabase_sql,
    supabase_storage_list,
    supabase_table_select,
)
from te_hau.kitenga_whakairo.tools.file_tools import read_file, list_files  # noqa: E402
from te_hau.kitenga_whakairo.tools.rules import rules_writer  # noqa: E402
from te_hau.kitenga_whakairo.tools.carve_tools import (  # noqa: E402
    record_carve_entry,
    sync_carver_context_tool,
)


def log_tool_use(tool_name: str, args: dict, result: Any):
    """Best-effort logging to local carver log and Supabase table."""
    try:
        entry = {
            "title": f"tool::{tool_name}",
            "summary": f"Tool call {tool_name}",
            "files_touched": [],
            "tags": ["whakairo", "tool_call"],
            "mode": "research",
            "created_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            "payload": {"args": args, "result": result},
        }
        log_path = PROJECT_ROOT / "mauri" / "state" / "carver_log.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as fh:
            import json

            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
        # Supabase best-effort
        try:
            from te_po.utils.supabase_client import get_client

            client = get_client()
            if client:
                client.table("carver_context_memory").insert(entry).execute()
        except Exception:
            pass
    except Exception:
        pass


def main():
    try:
        manifest = load_manifest("kitenga_whiro.manifest.json")
    except Exception:
        manifest = {"name": "kitenga_whakairo", "tools": []}

    print(f"\n🛡️ Whakairo Codex ({manifest.get('role', 'carver')}):")
    print(f"   Purpose: {manifest.get('purpose', 'Carving automation for AWANet')}")
    print(f"   Tools: {len(manifest.get('tools', []))} registered in manifest")

    app = FastMCP(
        "kitenga_whakairo",
        host=os.getenv("MCP_HOST", "0.0.0.0"),
        port=int(os.getenv("MCP_PORT", "39285")),
        streamable_http_path="/mcp",
    )

    # Supabase + storage
    app.add_tool(
        lambda ctx, **kwargs: (lambda res: (log_tool_use("supabase_table_select", kwargs, res), res)[1])(supabase_table_select(ctx, **kwargs)),
        name="supabase_table_select",
        description="Fetch rows from a Supabase table with optional limit/order.",
    )
    app.add_tool(
        lambda ctx, **kwargs: (lambda res: (log_tool_use("supabase_search", kwargs, res), res)[1])(supabase_search(ctx, **kwargs)),
        name="supabase_search",
        description="Search a Supabase table by ilike on the 'content' column.",
    )
    app.add_tool(
        lambda ctx, **kwargs: (lambda res: (log_tool_use("supabase_insert", kwargs, res), res)[1])(supabase_insert(ctx, **kwargs)),
        name="supabase_insert",
        description="Insert (or upsert) a record into a Supabase table.",
    )
    app.add_tool(
        lambda ctx, **kwargs: (lambda res: (log_tool_use("supabase_sql", kwargs, res), res)[1])(supabase_sql(ctx, **kwargs)),
        name="supabase_sql",
        description="Execute SQL via Postgres function (execute_sql by default). Blocks destructive SQL unless allow_write=True.",
    )
    app.add_tool(
        lambda ctx, **kwargs: (lambda res: (log_tool_use("supabase_storage_list", kwargs, res), res)[1])(supabase_storage_list(ctx, **kwargs)),
        name="supabase_storage_list",
        description="List objects/metadata from a Supabase storage bucket.",
    )

    # Carver utilities
    app.add_tool(
        lambda ctx, **kwargs: (lambda res: (log_tool_use("rules_writer", kwargs, res), res)[1])(rules_writer(ctx, **kwargs)),
        name="rules_writer",
        description="Return carving safety rules.",
    )
    app.add_tool(
        lambda ctx, **kwargs: (lambda res: (log_tool_use("record_carve_entry", kwargs, res), res)[1])(record_carve_entry(ctx, **kwargs)),
        name="record_carve_entry",
        description="Append a carve entry locally and best-effort to Supabase.",
    )
    app.add_tool(
        lambda ctx, **kwargs: (lambda res: (log_tool_use("sync_carver_context", kwargs, res), res)[1])(sync_carver_context_tool(ctx, **kwargs)),
        name="sync_carver_context",
        description="Sync carver context/logs from Supabase into local cache.",
    )

    # File helpers
    app.add_tool(
        lambda ctx, **kwargs: (lambda res: (log_tool_use("read_file", kwargs, res), res)[1])(read_file(ctx, **kwargs)),
        name="read_file",
        description="Read a UTF-8 file from disk.",
    )
    app.add_tool(
        lambda ctx, **kwargs: (lambda res: (log_tool_use("list_files", kwargs, res), res)[1])(list_files(ctx, **kwargs)),
        name="list_files",
        description="List directory contents.",
    )

    anyio.run(app.run_streamable_http_async)


if __name__ == "__main__":
    main()
