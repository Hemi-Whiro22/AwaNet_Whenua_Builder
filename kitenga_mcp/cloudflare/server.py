#!/usr/bin/env python3
"""
Cloudflare MCP Server
=====================
Supplies CLI + REST helpers for managing Cloudflare Pages projects and deployments.
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


def _normalize_cwd(path: str) -> str:
    return os.path.abspath(os.path.expanduser(path))


def _ensure_cli() -> bool:
    try:
        subprocess.run(["wrangler", "--version"], capture_output=True, text=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


class CloudflareServer:
    def __init__(self):
        self.token = os.getenv("CLOUDFLARE_API_TOKEN", "").strip()
        self.account_id = os.getenv("CLOUDFLARE_ACCOUNT_ID", "").strip()
        if not self.token or not self.account_id:
            raise ValueError("CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID are required")

        self.base_url = "https://api.cloudflare.com/client/v4"
        self.schema = self._load_json("schema.json")
        self.tools = self._load_json("tools.json").get("tools", [])

    @staticmethod
    def _load_json(filename: str) -> Dict[str, Any]:
        path = Path(__file__).parent / filename
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.request(
                method, url, headers=self._headers(), json=payload, params=params
            )
        try:
            body = response.json()
        except ValueError:
            body = response.text
        return {"status": response.status_code, "ok": response.is_success, "body": body}

    async def _run_command(self, args: list[str], cwd: Optional[str] = None) -> Dict[str, Any]:
        def _execute() -> Dict[str, Any]:
            proc = subprocess.run(
                args,
                cwd=_normalize_cwd(cwd) if cwd else None,
                capture_output=True,
                text=True,
                check=False,
            )
            return {
                "returncode": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            }

        return await asyncio.to_thread(_execute)

    async def deploy_pages(
        self,
        dist_path: str,
        project: str,
        branch: str = "main",
        commit_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not _ensure_cli():
            return {"status": "error", "error": "wrangler CLI is not installed"}

        args = ["wrangler", "pages", "deploy", dist_path, f"--project-name={project}", f"--branch={branch}"]
        if commit_message:
            args.append(f"--commit-message={commit_message}")

        result = await self._run_command(args)
        result["command"] = "wrangler pages deploy"
        result["project"] = project
        if result["returncode"] == 0:
            result["status"] = "deployed"
        else:
            result["status"] = "failed"
        return result

    async def deploy_te_ao(self, project_path: str, project_name: str, branch: str = "main") -> Dict[str, Any]:
        build_dir = Path(_normalize_cwd(project_path)) / "te_ao"
        if not build_dir.is_dir():
            return {"status": "error", "error": "te_ao directory not found"}

        build_result = await self._run_command(["npm", "run", "build"], cwd=str(build_dir))
        if build_result["returncode"] != 0:
            return {"status": "build_failed", "details": build_result}

        dist_path = str(build_dir / "dist")
        return await self.deploy_pages(dist_path, project_name, branch)

    async def create_project(self, name: str, production_branch: str = "main") -> Dict[str, Any]:
        payload = {"name": name, "production_branch": production_branch}
        return await self._request("POST", f"/accounts/{self.account_id}/pages/projects", payload)

    async def list_projects(self) -> Dict[str, Any]:
        return await self._request("GET", f"/accounts/{self.account_id}/pages/projects")

    async def get_project(self, name: str) -> Dict[str, Any]:
        return await self._request("GET", f"/accounts/{self.account_id}/pages/projects/{name}")

    async def set_env_vars(
        self, project: str, env_vars: Dict[str, str], preview: bool = False
    ) -> Dict[str, Any]:
        deployment_configs: Dict[str, Any] = {
            "production": {"env_vars": {k: {"value": v, "type": "plain_text"} for k, v in env_vars.items()}}
        }
        if preview:
            deployment_configs["preview"] = deployment_configs["production"]
        payload = {"deployment_configs": deployment_configs}
        return await self._request(
            "PATCH", f"/accounts/{self.account_id}/pages/projects/{project}", payload
        )

    async def list_deployments(self, project: str, limit: int = 10) -> Dict[str, Any]:
        params = {"per_page": limit}
        return await self._request(
            "GET", f"/accounts/{self.account_id}/pages/projects/{project}/deployments", params=params
        )

    async def add_custom_domain(self, project: str, domain: str) -> Dict[str, Any]:
        payload = {"name": domain}
        return await self._request(
            "POST", f"/accounts/{self.account_id}/pages/projects/{project}/domains", payload
        )

    async def purge_cache(self, zone_id: str, purge_everything: bool = True) -> Dict[str, Any]:
        payload = {"purge_everything": purge_everything}
        return await self._request("POST", f"/zones/{zone_id}/purge_cache", payload)


def create_server() -> Server:
    server = Server("cloudflare")
    service = CloudflareServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(name=tool["name"], description=tool.get("description", ""), inputSchema=tool.get("inputSchema", {}))
            for tool in service.tools
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        tool_def = next((t for t in service.tools if t["name"] == name), None)
        if not tool_def:
            return [TextContent(type="text", text=json.dumps({"error": f"Tool {name} not found"}))]

        try:
            if name == "deploy_pages":
                result = await service.deploy_pages(
                    arguments["dist_path"],
                    arguments["project"],
                    arguments.get("branch", "main"),
                    arguments.get("commit_message"),
                )
            elif name == "deploy_te_ao":
                result = await service.deploy_te_ao(
                    arguments["project_path"],
                    arguments["project_name"],
                    arguments.get("branch", "main"),
                )
            elif name == "create_project":
                result = await service.create_project(
                    arguments["name"], arguments.get("production_branch", "main")
                )
            elif name == "list_projects":
                result = await service.list_projects()
            elif name == "get_project":
                result = await service.get_project(arguments["name"])
            elif name == "set_env_vars":
                result = await service.set_env_vars(
                    arguments["project"], arguments["env_vars"], arguments.get("preview", False)
                )
            elif name == "list_deployments":
                result = await service.list_deployments(
                    arguments["project"], arguments.get("limit", 10)
                )
            elif name == "add_custom_domain":
                result = await service.add_custom_domain(arguments["project"], arguments["domain"])
            elif name == "purge_cache":
                result = await service.purge_cache(
                    arguments["zone_id"], arguments.get("purge_everything", True)
                )
            else:
                result = {"error": f"Tool {name} not implemented"}
        except KeyError as exc:
            result = {"error": f"Missing required argument: {exc.args[0]}"}
        except Exception as exc:  # pragma: no cover - surface errors
            result = {"error": str(exc)}

        return [TextContent(type="text", text=json.dumps(result))]

    return server


def create_fastapi_app():
    from fastapi import FastAPI

    mcp_server = create_server()
    app = FastAPI()

    @app.get("/status")
    async def status():
        return {"status": "ok", "service": "cloudflare"}

    app.state.mcp_server = mcp_server
    return app


async def main():
    server = create_server()
    async with stdio_server(server) as streams:
        await streams[1].aclose()


def run_cli():
    asyncio.run(main())


if __name__ == "__main__":
    run_cli()
