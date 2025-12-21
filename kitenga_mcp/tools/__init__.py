import json
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class ToolInput(BaseModel):
    name: str
    type: str
    required: bool = False
    description: Optional[str] = None


class ToolDefinition(BaseModel):
    id: str
    name: str
    description: str
    route: str
    method: str
    inputs: Optional[List[ToolInput]] = None
    output_description: str


_BASE_TOOLS = [
    ToolDefinition(
        id="memory_search",
        name="Search Memory",
        description="Semantic search across realm memory.",
        route="/mcp/memory/search",
        method="POST",
        inputs=[
            ToolInput(
                name="query",
                type="string",
                required=True,
                description="Text to semantically search.",
            )
        ],
        output_description="List of memory chunks ranked by similarity.",
    ),
    ToolDefinition(
        id="pipeline_jobs",
        name="List Recent Pipeline Jobs",
        description="Returns the most recent jobs enqueued for a realm.",
        route="/mcp/pipeline/jobs",
        method="GET",
        inputs=[
            ToolInput(
                name="realm",
                type="string",
                required=False,
                description="Realm to filter the jobs against.",
            )
        ],
        output_description="Recent queued jobs for the requested realm.",
    ),
]

MANIFEST_DIR = Path(__file__).resolve().parent / "manifests"
MANIFEST_FILES = {
    "render": MANIFEST_DIR / "render_commands_hardened.json",
    "git": MANIFEST_DIR / "git_commands_hardened.json",
    "render_service_map": Path(__file__).resolve().parent.parent / "tools" / "render_service_map_template.json",
}

GIT_WRITE_COMMANDS = {"commit_push"}
RENDER_WRITE_COMMANDS = {"set_env_vars", "deploy", "suspend_service", "resume_service"}


def _read_manifest(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_manifest(name: str) -> Dict:
    path = MANIFEST_FILES.get(name)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail=f"Manifest '{name}' not found.")
    try:
        return _read_manifest(path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Could not load manifest '{name}': {exc}")


def _build_tool_inputs(manifest_name: str, cmd_name: str, params: Dict) -> List[ToolInput]:
    inputs: List[ToolInput] = []
    for param_name, param in (params or {}).items():
        inputs.append(
            ToolInput(
                name=param_name,
                type=param.get("type", "string"),
                required=param.get("required", False),
                description=param.get("description") or "",
            )
        )

    if (
        (manifest_name == "git" and cmd_name in GIT_WRITE_COMMANDS)
        or (manifest_name == "render" and cmd_name in RENDER_WRITE_COMMANDS)
    ):
        inputs.append(
            ToolInput(
                name="admin_token",
                type="string",
                required=True,
                description="MCP admin token (Authorization: Bearer MCP_ADMIN_TOKEN).",
            )
        )
    return inputs


def _manifest_to_tools(manifest_name: str) -> List[ToolDefinition]:
    path = MANIFEST_FILES.get(manifest_name)
    if not path or not path.exists():
        return []

    try:
        manifest = _read_manifest(path)
    except Exception:
        return []

    commands = manifest.get("commands", {}) or {}
    tools: List[ToolDefinition] = []
    for cmd_name, config in commands.items():
        tool_inputs = _build_tool_inputs(manifest_name, cmd_name, config.get("params", {}))
        tools.append(
            ToolDefinition(
                id=f"{manifest_name}_{cmd_name}",
                name=config.get("description", cmd_name),
                description=config.get("description", ""),
                route=f"/mcp/{manifest_name}/{cmd_name}",
                method="POST",
                inputs=tool_inputs or None,
                output_description=config.get("description", ""),
            )
        )
    return tools


_tools_registry = _BASE_TOOLS + _manifest_to_tools("git") + _manifest_to_tools("render")

_tools_registry.extend(
    [
        ToolDefinition(
            id="supabase_select",
            name="Supabase Select",
            description="Read rows from Supabase via safe filters.",
            route="/mcp/supabase/select",
            method="POST",
            inputs=[
                ToolInput(name="table", type="string", required=True),
                ToolInput(
                    name="schema",
                    type="string",
                    required=False,
                    description="Allowed schemas: kitenga, public",
                ),
                ToolInput(
                    name="select",
                    type="string",
                    required=False,
                    description="Columns (comma-separated) or *",
                ),
                ToolInput(
                    name="filters",
                    type="object",
                    required=False,
                    description="Equality/inequality filters (eq, ilike, in, gt, gte, lt, lte)",
                ),
                ToolInput(
                    name="limit",
                    type="integer",
                    required=False,
                    description="Maximum number of rows",
                ),
                ToolInput(
                    name="order",
                    type="object",
                    required=False,
                    description="Column sorting directions",
                ),
            ],
            output_description="Supabase select response (data list).",
        ),
        ToolDefinition(
            id="supabase_insert",
            name="Supabase Insert",
            description="Insert rows into Supabase tables via REST.",
            route="/mcp/supabase/insert",
            method="POST",
            inputs=[
                ToolInput(name="table", type="string", required=True),
                ToolInput(
                    name="schema",
                    type="string",
                    required=False,
                    description="Allowed schemas: kitenga, public",
                ),
                ToolInput(
                    name="rows",
                    type="object",
                    required=True,
                    description="List of row objects to insert (min 1).",
                ),
                ToolInput(
                    name="returning",
                    type="string",
                    required=False,
                    description="Prefer return detail: minimal or representation",
                ),
            ],
            output_description="Supabase insert response.",
        ),
        ToolDefinition(
            id="supabase_update",
            name="Supabase Update",
            description="Update rows using filters in Supabase tables.",
            route="/mcp/supabase/update",
            method="POST",
            inputs=[
                ToolInput(name="table", type="string", required=True),
                ToolInput(
                    name="schema",
                    type="string",
                    required=False,
                    description="Allowed schemas: kitenga, public",
                ),
                ToolInput(
                    name="values",
                    type="object",
                    required=True,
                    description="Key/value updates for matched rows.",
                ),
                ToolInput(
                    name="filters",
                    type="object",
                    required=True,
                    description="Filters required to scope update (eq, in, etc.).",
                ),
            ],
            output_description="Supabase update response.",
        ),
    ]
)


def get_tool_registry() -> List[ToolDefinition]:
    """Expose the current registry for other components."""
    return list(_tools_registry)


@router.get("/list", response_model=List[ToolDefinition])
def list_tools():
    return get_tool_registry()


@router.post("/register", response_model=ToolDefinition)
def register_tool(tool: ToolDefinition):
    if any(entry.id == tool.id for entry in _tools_registry):
        raise HTTPException(status_code=400, detail="Tool id already registered.")
    _tools_registry.append(tool)
    return tool


@router.get("/manifests")
def list_manifests():
    return {"available": list(MANIFEST_FILES.keys())}


@router.get("/manifests/{name}")
def get_manifest(name: str):
    return _load_manifest(name)
