#!/usr/bin/env python3
"""
Register or update the Kitenga Whiro assistant on OpenAI using a manifest and environment values.

Runs the following steps:
1. Loads /shared/openai.json or falls back to mauri/openai_tools_manifest.json.
2. Loads environment values from te_po/core/.env and the current process env.
3. Injects env values into the manifest (string placeholders like ${SUPABASE_URL}).
4. Ensures the file_search tool is present and linked to the configured vector store.
5. Calls the OpenAI Assistants API to update/create the assistant.
6. Writes the updated manifest (including assistant_id) back to disk.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict

from openai import OpenAI

MANIFEST_CANDIDATES = [
    Path("/shared/openai.json"),
    Path("mauri/openai_tools_manifest.json"),
]
ENV_PATH = Path("te_po/core/.env")
PLACEHOLDER_RE = re.compile(r"\$\{([^}]+)\}")


def find_manifest() -> Path:
    for path in MANIFEST_CANDIDATES:
        if path.exists():
            return path
    raise SystemExit("Manifest not found in /shared or mauri directories.")


def load_env_file(path: Path) -> Dict[str, str]:
    env: Dict[str, str] = {}
    if not path.exists():
        return env
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith(("'", '"')) and value.endswith(("'", '"')):
            value = value[1:-1]
        env[key] = value
    return env


def apply_env_placeholders(data: Any, env: Dict[str, str]) -> Any:
    if isinstance(data, dict):
        return {k: apply_env_placeholders(v, env) for k, v in data.items()}
    if isinstance(data, list):
        return [apply_env_placeholders(item, env) for item in data]
    if isinstance(data, str):
        def repl(match: re.Match[str]) -> str:
            key = match.group(1)
            return env.get(key, match.group(0))
        return PLACEHOLDER_RE.sub(repl, data)
    return data


def ensure_file_search(manifest: Dict[str, Any], vector_store_id: str | None) -> None:
    if not vector_store_id:
        return
    tools = manifest.setdefault("tools", [])
    has_file_search = any(tool.get("type") == "file_search" for tool in tools)
    if not has_file_search:
        tools.append({"type": "file_search"})
    resources = manifest.setdefault("tool_resources", {})
    file_search = resources.setdefault("file_search", {})
    ids = file_search.setdefault("vector_store_ids", [])
    if vector_store_id not in ids:
        ids.append(vector_store_id)


def build_payload(config: Dict[str, Any]) -> Dict[str, Any]:
    payload: Dict[str, Any] = {}
    for key in ("name", "instructions", "model", "metadata"):
        if config.get(key):
            payload[key] = config[key]
    if config.get("tools"):
        payload["tools"] = config["tools"]
    if config.get("tool_resources"):
        payload["tool_resources"] = config["tool_resources"]
    return payload


def main() -> None:
    manifest_path = find_manifest()
    config = json.loads(manifest_path.read_text() or "{}")

    env_values = load_env_file(ENV_PATH)
    env_values.update(os.environ)
    config = apply_env_placeholders(config, env_values)

    assistant_id = config.get("assistant_id") or env_values.get("KITENGA_ASSISTANT_ID", "")
    vector_store_id = env_values.get("OPENAI_VECTOR_STORE_ID")
    ensure_file_search(config, vector_store_id)

    payload = build_payload(config)
    client = OpenAI()

    created = None
    if assistant_id and assistant_id != "asst_XXXX":
        updated = client.beta.assistants.update(assistant_id=assistant_id, **payload)
        assistant = updated
        print(f"[kitenga] Updated assistant {updated.id} with {len(payload.get('tools', []))} tools.")
    else:
        created = client.beta.assistants.create(**payload)
        assistant = created
        assistant_id = created.id
        print(f"[kitenga] Created new assistant {assistant_id}.")

    config["assistant_id"] = assistant_id
    manifest_path.write_text(json.dumps(config, indent=2) + "\n")
    print(f"[kitenga] Manifest updated at {manifest_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[kitenga] Failed to register assistant: {exc}", file=sys.stderr)
        sys.exit(1)
