#!/usr/bin/env python3
"""Simple harness that hits the Render schema paths and fetches the latest analysis document."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List

import requests


def _sample_value(name: str, schema: Dict[str, Any], base_url: str) -> Any:
    if schema.get("enum"):
        return schema["enum"][0]
    t = schema.get("type")
    name_lower = name.lower()
    if "file_url" in name_lower or "url" in name_lower:
        return f"{base_url}/analysis/documents/latest"
    if name_lower in {"text", "input", "payload", "query", "prompt", "content"}:
        return "Kia ora — testing GPT toolflow."
    if name_lower in {"session_id", "job_id", "thread_id"}:
        return "test-session"
    if t == "boolean":
        return True
    if t == "integer":
        return 1
    if t == "number":
        return 1.0
    if t == "array":
        item_schema = schema.get("items", {"type": "string"})
        return [_sample_value(name, item_schema, base_url)]
    if t == "object":
        return _build_sample_from_schema(schema, base_url)
    return "example"


def _build_sample_from_schema(schema: Dict[str, Any], base_url: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for prop_name, prop_schema in schema.get("properties", {}).items():
        result[prop_name] = _sample_value(prop_name, prop_schema, base_url)
    return result


def _build_payload(request_body: Dict[str, Any], base_url: str) -> Dict[str, Any]:
    content = request_body.get("content", {})
    for media_type in ("application/json", "*/*"):
        schema = content.get(media_type, {}).get("schema")
        if schema:
            return _build_sample_from_schema(schema, base_url)
    return {}


def _count_path_params(path: str) -> int:
    return path.count("{")


def _run_review_sync(script_path: Path) -> None:
    try:
        subprocess.run(["python3", str(script_path)], check=True)
    except Exception as exc:  # pragma: no cover
        print(f"⚠️ Failed to run repo review sync: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Hit live tools defined in openapi-core.json")
    parser.add_argument("--base-url", default="https://tiwhanawhana-backend.onrender.com")
    parser.add_argument("--schema", default="app/openapi-core.json")
    parser.add_argument("--token", default="PIPELINE_TOKEN")
    parser.add_argument("--skip-sync", action="store_true")
    args = parser.parse_args()

    schema_path = Path(args.schema)
    if not schema_path.exists():
        raise SystemExit(f"Schema not found: {schema_path}")

    headers = {
        "Authorization": f"Bearer {args.token}",
        "Content-Type": "application/json",
    }
    if args.token == "PIPELINE_TOKEN":
        token_value = Path(".env").read_text().split("\n") if Path(".env").exists() else []
        for line in token_value:
            if line.startswith("PIPELINE_TOKEN="):
                headers["Authorization"] = f"Bearer {line.split('=', 1)[1]}"
                break

    with schema_path.open(encoding="utf-8") as handle:
        spec = json.load(handle)

    results: List[Dict[str, Any]] = []
    for path, methods in spec.get("paths", {}).items():
        for method, operation in methods.items():
            method_lower = method.lower()
            if method_lower not in {"post", "get", "put", "patch"}:
                continue
            if method_lower == "get" and _count_path_params(path) > 0:
                continue

            payload: Dict[str, Any] = {}
            if request_body := operation.get("requestBody"):
                payload = _build_payload(request_body, args.base_url)

            url = args.base_url.rstrip("/") + path
            try:
                method_upper = method.upper()
                if method_lower == "get":
                    resp = requests.get(url, headers=headers, timeout=30)
                else:
                    resp = requests.request(method_upper, url=url, headers=headers, json=payload, timeout=60)
                try:
                    body = resp.json()
                except ValueError:
                    body = resp.text
                results.append({
                    "path": path,
                    "method": method_upper,
                    "status": resp.status_code,
                    "body": body,
                })
            except Exception as exc:  # pragma: no cover
                results.append({"path": path, "method": method.upper(), "error": str(exc)})
            time.sleep(1)

    final_doc = {}
    try:
        resp = requests.get(f"{args.base_url.rstrip('/')}/analysis/documents/latest", headers=headers, timeout=20)
        final_doc = resp.json()
    except Exception as exc:  # pragma: no cover
        print(f"⚠️ Failed to fetch latest document: {exc}")

    summary = {
        "results": results,
        "latest_document": final_doc,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))

    if not args.skip_sync:
        _run_review_sync(Path("analysis/run_repo_review.py"))


if __name__ == "__main__":
    main()
