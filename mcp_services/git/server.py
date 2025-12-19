#!/usr/bin/env python3
"""
Git MCP Server
==============
GitHub API integration via Model Context Protocol.
Supports repos, branches, commits, PRs, issues, releases.

Env:
  GITHUB_TOKEN    GitHub personal access token (required)
"""

import asyncio
import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

import httpx

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class GitServer:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")

        if not self.token:
            raise ValueError("GITHUB_TOKEN environment variable is required")

        # Load schema and tools
        schema_path = Path(__file__).parent / "schema.json"
        tools_path = Path(__file__).parent / "tools.json"

        with open(schema_path) as f:
            self.schema = json.load(f)

        with open(tools_path) as f:
            tools_data = json.load(f)
            self.tools = tools_data.get("tools", [])

    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json",
        }

    async def call_github(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
        query: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Call GitHub API."""
        url = f"{self.base_url}{path}"
        headers = self.get_headers()

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                if method.upper() == "GET":
                    resp = await client.get(url, params=query, headers=headers)
                elif method.upper() == "POST":
                    resp = await client.post(url, json=payload, params=query, headers=headers)
                elif method.upper() == "PUT":
                    resp = await client.put(url, json=payload, params=query, headers=headers)
                elif method.upper() == "DELETE":
                    resp = await client.delete(url, params=query, headers=headers)
                elif method.upper() == "PATCH":
                    resp = await client.patch(url, json=payload, params=query, headers=headers)
                else:
                    return {"error": f"Unsupported method: {method}"}

                data = resp.json() if resp.text else None

                return {
                    "status": resp.status_code,
                    "data": data,
                    "error": None if resp.is_success else resp.text,
                }
        except Exception as e:
            return {"status": 500, "data": None, "error": str(e)}


def create_server() -> Server:
    server = Server("git")
    git = GitServer()

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available Git tools."""
        return [
            Tool(
                name=tool["name"],
                description=tool["description"],
                inputSchema=tool.get("inputSchema", {}),
            )
            for tool in git.tools
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
        """Execute a Git tool."""

        tool_def = next((t for t in git.tools if t["name"] == name), None)
        if not tool_def:
            return [TextContent(type="text", text=json.dumps({"error": f"Tool {name} not found"}))]

        # Tool to GitHub API mapping
        tool_map = {
            "git_repo_info": ("GET", "/repos/{owner}/{repo}"),
            "git_list_branches": ("GET", "/repos/{owner}/{repo}/branches"),
            "git_create_branch": ("POST", "/repos/{owner}/{repo}/git/refs"),
            "git_list_commits": ("GET", "/repos/{owner}/{repo}/commits"),
            "git_get_file": ("GET", "/repos/{owner}/{repo}/contents/{path}"),
            "git_create_file": ("PUT", "/repos/{owner}/{repo}/contents/{path}"),
            "git_update_file": ("PUT", "/repos/{owner}/{repo}/contents/{path}"),
            "git_delete_file": ("DELETE", "/repos/{owner}/{repo}/contents/{path}"),
            "git_list_pull_requests": ("GET", "/repos/{owner}/{repo}/pulls"),
            "git_get_pull_request": ("GET", "/repos/{owner}/{repo}/pulls/{pull_number}"),
            "git_create_pull_request": ("POST", "/repos/{owner}/{repo}/pulls"),
            "git_list_issues": ("GET", "/repos/{owner}/{repo}/issues"),
            "git_create_issue": ("POST", "/repos/{owner}/{repo}/issues"),
            "git_list_releases": ("GET", "/repos/{owner}/{repo}/releases"),
            "git_create_release": ("POST", "/repos/{owner}/{repo}/releases"),
            "git_get_user": ("GET", "/user"),
            "git_list_workflows": ("GET", "/repos/{owner}/{repo}/actions/workflows"),
        }

        if name not in tool_map:
            return [TextContent(type="text", text=json.dumps({"error": f"Tool {name} not mapped"}))]

        method, path_template = tool_map[name]

        # Format path with arguments
        path = path_template
        for key, value in list(arguments.items()):
            placeholder = "{" + key + "}"
            if placeholder in path:
                path = path.replace(placeholder, str(value))
                arguments.pop(key)

        # Separate query params from payload
        query_params = {}
        payload = None

        if method == "GET":
            query_params = arguments
        else:
            payload = arguments

        result = await git.call_github(method, path, payload=payload, query=query_params)

        return [TextContent(type="text", text=json.dumps(result))]

    return server


async def main():
    server = create_server()
    async with stdio_server(server) as streams:
        await streams[1].aclose()


if __name__ == "__main__":
    asyncio.run(main())
