#!/usr/bin/env python3
"""
Cloudflare Pages MCP Server
===========================
MCP server for Cloudflare Pages deployment within AwaOS.

Provides:
- Pages project creation
- Build folder deployment
- Domain binding
- Environment variable injection
- Cache invalidation

Environment:
    CLOUDFLARE_API_TOKEN - API token with Pages permissions
    CLOUDFLARE_ACCOUNT_ID - Your Cloudflare account ID
"""

import os
import json
import asyncio
import subprocess
from typing import Optional, Dict, List, Any
from dataclasses import dataclass

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
CLOUDFLARE_API = "https://api.cloudflare.com/client/v4"


@dataclass
class CloudflareConfig:
    """Cloudflare configuration."""
    api_token: str
    account_id: str
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_token and self.account_id)


# ═══════════════════════════════════════════════════════════════
# SHELL UTILITIES
# ═══════════════════════════════════════════════════════════════

def run(cmd: str, cwd: Optional[str] = None, check: bool = True) -> str:
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=check
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}"


# ═══════════════════════════════════════════════════════════════
# CLOUDFLARE CLIENT
# ═══════════════════════════════════════════════════════════════

class CloudflareClient:
    """Cloudflare Pages operations wrapper."""
    
    def __init__(self, config: CloudflareConfig):
        self.config = config
    
    def _headers(self) -> Dict[str, str]:
        """Get API headers."""
        return {
            "Authorization": f"Bearer {self.config.api_token}",
            "Content-Type": "application/json"
        }
    
    # ─────────────────────────────────────────────────────────
    # WRANGLER COMMANDS (CLI-based deployment)
    # ─────────────────────────────────────────────────────────
    
    def deploy_pages(
        self, 
        dist_path: str, 
        project: str,
        branch: str = "main",
        commit_message: Optional[str] = None
    ) -> Dict[str, str]:
        """Deploy to Cloudflare Pages using wrangler."""
        cmd = f"wrangler pages deploy {dist_path} --project-name={project} --branch={branch}"
        
        if commit_message:
            cmd += f' --commit-message="{commit_message}"'
        
        result = run(cmd, check=False)
        
        if "Error" in result:
            return {"status": "failed", "error": result}
        
        return {
            "status": "deployed",
            "project": project,
            "branch": branch,
            "output": result
        }
    
    def deploy_te_ao(self, project_path: str, project_name: str) -> Dict[str, str]:
        """
        Deploy Te Ao frontend to Cloudflare Pages.
        
        This is the standard AwaOS flow:
        1. Build the frontend (npm run build)
        2. Deploy to Pages
        """
        # Build step
        build_result = run("npm run build", cwd=f"{project_path}/te_ao", check=False)
        
        if "Error" in build_result and "error" in build_result.lower():
            return {"status": "build_failed", "error": build_result}
        
        # Deploy step
        dist_path = f"{project_path}/te_ao/dist"
        return self.deploy_pages(dist_path, project_name)
    
    # ─────────────────────────────────────────────────────────
    # CLOUDFLARE API OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def create_project(
        self, 
        name: str,
        production_branch: str = "main"
    ) -> Dict:
        """Create a new Pages project."""
        if not self.config.is_configured:
            return {"error": "Cloudflare not configured"}
        
        url = f"{CLOUDFLARE_API}/accounts/{self.config.account_id}/pages/projects"
        
        data = {
            "name": name,
            "production_branch": production_branch
        }
        
        response = requests.post(url, json=data, headers=self._headers())
        
        if response.status_code in [200, 201]:
            result = response.json()
            if result.get("success"):
                project = result["result"]
                return {
                    "name": project["name"],
                    "subdomain": project.get("subdomain", f"{name}.pages.dev"),
                    "production_branch": project.get("production_branch", production_branch)
                }
        
        return {"error": response.text}
    
    def list_projects(self) -> List[Dict]:
        """List all Pages projects."""
        if not self.config.is_configured:
            return [{"error": "Cloudflare not configured"}]
        
        url = f"{CLOUDFLARE_API}/accounts/{self.config.account_id}/pages/projects"
        response = requests.get(url, headers=self._headers())
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return [
                    {
                        "name": p["name"],
                        "subdomain": p.get("subdomain"),
                        "production_branch": p.get("production_branch")
                    }
                    for p in result.get("result", [])
                ]
        
        return [{"error": response.text}]
    
    def get_project(self, name: str) -> Dict:
        """Get project details."""
        if not self.config.is_configured:
            return {"error": "Cloudflare not configured"}
        
        url = f"{CLOUDFLARE_API}/accounts/{self.config.account_id}/pages/projects/{name}"
        response = requests.get(url, headers=self._headers())
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return result["result"]
        
        return {"error": response.text}
    
    def set_env_vars(self, project: str, env_vars: Dict[str, str], preview: bool = False) -> Dict:
        """Set environment variables for a project."""
        if not self.config.is_configured:
            return {"error": "Cloudflare not configured"}
        
        url = f"{CLOUDFLARE_API}/accounts/{self.config.account_id}/pages/projects/{project}"
        
        # Build deployment configs
        deployment_configs = {
            "production": {
                "env_vars": {
                    k: {"value": v, "type": "plain_text"}
                    for k, v in env_vars.items()
                }
            }
        }
        
        if preview:
            deployment_configs["preview"] = deployment_configs["production"]
        
        data = {"deployment_configs": deployment_configs}
        
        response = requests.patch(url, json=data, headers=self._headers())
        
        if response.status_code == 200:
            return {"status": "env_vars_updated", "project": project}
        
        return {"error": response.text}
    
    def list_deployments(self, project: str, limit: int = 10) -> List[Dict]:
        """List deployments for a project."""
        if not self.config.is_configured:
            return [{"error": "Cloudflare not configured"}]
        
        url = f"{CLOUDFLARE_API}/accounts/{self.config.account_id}/pages/projects/{project}/deployments"
        response = requests.get(url, params={"per_page": limit}, headers=self._headers())
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return [
                    {
                        "id": d["id"],
                        "url": d.get("url"),
                        "environment": d.get("environment"),
                        "created_on": d.get("created_on")
                    }
                    for d in result.get("result", [])
                ]
        
        return [{"error": response.text}]
    
    def add_custom_domain(self, project: str, domain: str) -> Dict:
        """Add a custom domain to a project."""
        if not self.config.is_configured:
            return {"error": "Cloudflare not configured"}
        
        url = f"{CLOUDFLARE_API}/accounts/{self.config.account_id}/pages/projects/{project}/domains"
        
        data = {"name": domain}
        response = requests.post(url, json=data, headers=self._headers())
        
        if response.status_code in [200, 201]:
            return {"status": "domain_added", "domain": domain, "project": project}
        
        return {"error": response.text}
    
    def purge_cache(self, zone_id: str, purge_everything: bool = True) -> Dict:
        """Purge cache for a zone (requires zone ID)."""
        if not self.config.is_configured:
            return {"error": "Cloudflare not configured"}
        
        url = f"{CLOUDFLARE_API}/zones/{zone_id}/purge_cache"
        
        data = {"purge_everything": purge_everything}
        response = requests.post(url, json=data, headers=self._headers())
        
        if response.status_code == 200:
            return {"status": "cache_purged", "zone_id": zone_id}
        
        return {"error": response.text}


# ═══════════════════════════════════════════════════════════════
# MCP SERVER
# ═══════════════════════════════════════════════════════════════

def create_cloudflare_server() -> "Server":
    """Create and configure the Cloudflare MCP server."""
    
    if not HAS_MCP:
        raise RuntimeError("MCP SDK not installed")
    
    server = Server("cloudflare")
    config = CloudflareConfig(CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID)
    client = CloudflareClient(config)
    
    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="deploy_pages",
                description="Deploy a directory to Cloudflare Pages",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dist_path": {"type": "string", "description": "Path to build output"},
                        "project": {"type": "string", "description": "Pages project name"},
                        "branch": {"type": "string", "default": "main"},
                        "commit_message": {"type": "string"}
                    },
                    "required": ["dist_path", "project"]
                }
            ),
            Tool(
                name="deploy_te_ao",
                description="Build and deploy Te Ao frontend to Cloudflare Pages",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Path to AwaOS project"},
                        "project_name": {"type": "string", "description": "Pages project name"}
                    },
                    "required": ["project_path", "project_name"]
                }
            ),
            Tool(
                name="create_project",
                description="Create a new Cloudflare Pages project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "production_branch": {"type": "string", "default": "main"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="list_projects",
                description="List all Cloudflare Pages projects",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="get_project",
                description="Get details for a Pages project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="set_env_vars",
                description="Set environment variables for a project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project": {"type": "string"},
                        "env_vars": {"type": "object"},
                        "preview": {"type": "boolean", "default": False}
                    },
                    "required": ["project", "env_vars"]
                }
            ),
            Tool(
                name="list_deployments",
                description="List deployments for a project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project": {"type": "string"},
                        "limit": {"type": "integer", "default": 10}
                    },
                    "required": ["project"]
                }
            ),
            Tool(
                name="add_custom_domain",
                description="Add a custom domain to a project",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "project": {"type": "string"},
                        "domain": {"type": "string"}
                    },
                    "required": ["project", "domain"]
                }
            ),
            Tool(
                name="purge_cache",
                description="Purge cache for a Cloudflare zone",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "zone_id": {"type": "string"}
                    },
                    "required": ["zone_id"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "deploy_pages":
                result = client.deploy_pages(
                    arguments["dist_path"],
                    arguments["project"],
                    arguments.get("branch", "main"),
                    arguments.get("commit_message")
                )
            elif name == "deploy_te_ao":
                result = client.deploy_te_ao(
                    arguments["project_path"],
                    arguments["project_name"]
                )
            elif name == "create_project":
                result = client.create_project(
                    arguments["name"],
                    arguments.get("production_branch", "main")
                )
            elif name == "list_projects":
                result = client.list_projects()
            elif name == "get_project":
                result = client.get_project(arguments["name"])
            elif name == "set_env_vars":
                result = client.set_env_vars(
                    arguments["project"],
                    arguments["env_vars"],
                    arguments.get("preview", False)
                )
            elif name == "list_deployments":
                result = client.list_deployments(
                    arguments["project"],
                    arguments.get("limit", 10)
                )
            elif name == "add_custom_domain":
                result = client.add_custom_domain(
                    arguments["project"],
                    arguments["domain"]
                )
            elif name == "purge_cache":
                result = client.purge_cache(arguments["zone_id"])
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
    
    return server


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY
# ═══════════════════════════════════════════════════════════════

async def main():
    """Run the Cloudflare MCP server."""
    from mcp.server.stdio import stdio_server
    
    server = create_cloudflare_server()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
