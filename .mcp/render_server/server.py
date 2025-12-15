#!/usr/bin/env python3
"""
Render MCP Server
=================
MCP server for Render deployment within AwaOS.

Provides:
- Service deployment (mini_te_po backends)
- Environment variable management
- Service health checks
- Deploy triggers
- Auto-scaling configuration

Environment:
    RENDER_API_KEY - Render API key
"""

import os
import json
import asyncio
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

RENDER_API_KEY = os.getenv("RENDER_API_KEY", "")
RENDER_API = "https://api.render.com/v1"


@dataclass
class RenderConfig:
    """Render configuration."""
    api_key: str
    
    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)


# ═══════════════════════════════════════════════════════════════
# RENDER CLIENT
# ═══════════════════════════════════════════════════════════════

class RenderClient:
    """Render API operations wrapper."""
    
    def __init__(self, config: RenderConfig):
        self.config = config
    
    def _headers(self) -> Dict[str, str]:
        """Get API headers."""
        return {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
    
    # ─────────────────────────────────────────────────────────
    # SERVICE OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def list_services(self, limit: int = 20) -> List[Dict]:
        """List all services."""
        if not self.config.is_configured:
            return [{"error": "RENDER_API_KEY not configured"}]
        
        response = requests.get(
            f"{RENDER_API}/services",
            params={"limit": limit},
            headers=self._headers()
        )
        
        if response.status_code == 200:
            return [
                {
                    "id": s["service"]["id"],
                    "name": s["service"]["name"],
                    "type": s["service"]["type"],
                    "slug": s["service"].get("slug"),
                    "suspended": s["service"].get("suspended"),
                    "url": s["service"].get("serviceDetails", {}).get("url")
                }
                for s in response.json()
            ]
        
        return [{"error": response.text}]
    
    def get_service(self, service_id: str) -> Dict:
        """Get service details."""
        if not self.config.is_configured:
            return {"error": "RENDER_API_KEY not configured"}
        
        response = requests.get(
            f"{RENDER_API}/services/{service_id}",
            headers=self._headers()
        )
        
        if response.status_code == 200:
            return response.json()
        
        return {"error": response.text}
    
    def deploy(self, service_id: str, clear_cache: bool = False) -> Dict:
        """Trigger a deployment for a service."""
        if not self.config.is_configured:
            return {"error": "RENDER_API_KEY not configured"}
        
        data = {"clearCache": "clear" if clear_cache else "do_not_clear"}
        
        response = requests.post(
            f"{RENDER_API}/services/{service_id}/deploys",
            json=data,
            headers=self._headers()
        )
        
        if response.status_code in [200, 201]:
            deploy = response.json()
            return {
                "id": deploy.get("id"),
                "status": deploy.get("status"),
                "created_at": deploy.get("createdAt")
            }
        
        return {"error": response.text}
    
    def list_deploys(self, service_id: str, limit: int = 10) -> List[Dict]:
        """List deployments for a service."""
        if not self.config.is_configured:
            return [{"error": "RENDER_API_KEY not configured"}]
        
        response = requests.get(
            f"{RENDER_API}/services/{service_id}/deploys",
            params={"limit": limit},
            headers=self._headers()
        )
        
        if response.status_code == 200:
            return [
                {
                    "id": d["deploy"]["id"],
                    "status": d["deploy"]["status"],
                    "created_at": d["deploy"].get("createdAt"),
                    "finished_at": d["deploy"].get("finishedAt")
                }
                for d in response.json()
            ]
        
        return [{"error": response.text}]
    
    def get_deploy(self, service_id: str, deploy_id: str) -> Dict:
        """Get deployment details."""
        if not self.config.is_configured:
            return {"error": "RENDER_API_KEY not configured"}
        
        response = requests.get(
            f"{RENDER_API}/services/{service_id}/deploys/{deploy_id}",
            headers=self._headers()
        )
        
        if response.status_code == 200:
            return response.json()
        
        return {"error": response.text}
    
    # ─────────────────────────────────────────────────────────
    # ENVIRONMENT VARIABLES
    # ─────────────────────────────────────────────────────────
    
    def list_env_vars(self, service_id: str) -> List[Dict]:
        """List environment variables for a service."""
        if not self.config.is_configured:
            return [{"error": "RENDER_API_KEY not configured"}]
        
        response = requests.get(
            f"{RENDER_API}/services/{service_id}/env-vars",
            headers=self._headers()
        )
        
        if response.status_code == 200:
            return [
                {
                    "key": ev["envVar"]["key"],
                    "value": ev["envVar"].get("value", "***"),  # May be hidden
                }
                for ev in response.json()
            ]
        
        return [{"error": response.text}]
    
    def set_env_var(self, service_id: str, key: str, value: str) -> Dict:
        """Set an environment variable."""
        if not self.config.is_configured:
            return {"error": "RENDER_API_KEY not configured"}
        
        data = [{"key": key, "value": value}]
        
        response = requests.put(
            f"{RENDER_API}/services/{service_id}/env-vars",
            json=data,
            headers=self._headers()
        )
        
        if response.status_code == 200:
            return {"status": "env_var_set", "key": key}
        
        return {"error": response.text}
    
    def set_env_vars(self, service_id: str, env_vars: Dict[str, str]) -> Dict:
        """Set multiple environment variables."""
        if not self.config.is_configured:
            return {"error": "RENDER_API_KEY not configured"}
        
        data = [{"key": k, "value": v} for k, v in env_vars.items()]
        
        response = requests.put(
            f"{RENDER_API}/services/{service_id}/env-vars",
            json=data,
            headers=self._headers()
        )
        
        if response.status_code == 200:
            return {"status": "env_vars_updated", "count": len(env_vars)}
        
        return {"error": response.text}
    
    # ─────────────────────────────────────────────────────────
    # SERVICE CONTROL
    # ─────────────────────────────────────────────────────────
    
    def suspend_service(self, service_id: str) -> Dict:
        """Suspend a service."""
        if not self.config.is_configured:
            return {"error": "RENDER_API_KEY not configured"}
        
        response = requests.post(
            f"{RENDER_API}/services/{service_id}/suspend",
            headers=self._headers()
        )
        
        if response.status_code == 200:
            return {"status": "suspended", "service_id": service_id}
        
        return {"error": response.text}
    
    def resume_service(self, service_id: str) -> Dict:
        """Resume a suspended service."""
        if not self.config.is_configured:
            return {"error": "RENDER_API_KEY not configured"}
        
        response = requests.post(
            f"{RENDER_API}/services/{service_id}/resume",
            headers=self._headers()
        )
        
        if response.status_code == 200:
            return {"status": "resumed", "service_id": service_id}
        
        return {"error": response.text}
    
    def restart_service(self, service_id: str) -> Dict:
        """Restart a service (redeploy from latest)."""
        # Render doesn't have explicit restart - we trigger a deploy
        return self.deploy(service_id)
    
    # ─────────────────────────────────────────────────────────
    # AWAOS SPECIFIC
    # ─────────────────────────────────────────────────────────
    
    def deploy_mini_te_po(self, service_id: str, env_vars: Optional[Dict[str, str]] = None) -> Dict:
        """
        Deploy mini_te_po backend service.
        
        This is the standard AwaOS flow:
        1. Update env vars if provided
        2. Trigger deployment
        """
        results = {}
        
        if env_vars:
            env_result = self.set_env_vars(service_id, env_vars)
            results["env_vars"] = env_result
        
        deploy_result = self.deploy(service_id)
        results["deploy"] = deploy_result
        
        return results
    
    def health_check(self, service_id: str) -> Dict:
        """Check service health status."""
        service = self.get_service(service_id)
        
        if "error" in service:
            return service
        
        return {
            "service_id": service_id,
            "name": service.get("name"),
            "suspended": service.get("suspended"),
            "status": "healthy" if not service.get("suspended") else "suspended"
        }


# ═══════════════════════════════════════════════════════════════
# MCP SERVER
# ═══════════════════════════════════════════════════════════════

def create_render_server() -> "Server":
    """Create and configure the Render MCP server."""
    
    if not HAS_MCP:
        raise RuntimeError("MCP SDK not installed")
    
    server = Server("render")
    config = RenderConfig(RENDER_API_KEY)
    client = RenderClient(config)
    
    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="list_services",
                description="List all Render services",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 20}
                    }
                }
            ),
            Tool(
                name="get_service",
                description="Get details for a Render service",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string"}
                    },
                    "required": ["service_id"]
                }
            ),
            Tool(
                name="deploy",
                description="Trigger a deployment for a service",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string"},
                        "clear_cache": {"type": "boolean", "default": False}
                    },
                    "required": ["service_id"]
                }
            ),
            Tool(
                name="list_deploys",
                description="List deployments for a service",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string"},
                        "limit": {"type": "integer", "default": 10}
                    },
                    "required": ["service_id"]
                }
            ),
            Tool(
                name="list_env_vars",
                description="List environment variables for a service",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string"}
                    },
                    "required": ["service_id"]
                }
            ),
            Tool(
                name="set_env_vars",
                description="Set environment variables for a service",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string"},
                        "env_vars": {"type": "object"}
                    },
                    "required": ["service_id", "env_vars"]
                }
            ),
            Tool(
                name="suspend_service",
                description="Suspend a Render service",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string"}
                    },
                    "required": ["service_id"]
                }
            ),
            Tool(
                name="resume_service",
                description="Resume a suspended service",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string"}
                    },
                    "required": ["service_id"]
                }
            ),
            Tool(
                name="deploy_mini_te_po",
                description="Deploy mini_te_po backend (AwaOS standard flow)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string"},
                        "env_vars": {"type": "object", "description": "Optional env vars to set"}
                    },
                    "required": ["service_id"]
                }
            ),
            Tool(
                name="health_check",
                description="Check service health status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "service_id": {"type": "string"}
                    },
                    "required": ["service_id"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "list_services":
                result = client.list_services(arguments.get("limit", 20))
            elif name == "get_service":
                result = client.get_service(arguments["service_id"])
            elif name == "deploy":
                result = client.deploy(
                    arguments["service_id"],
                    arguments.get("clear_cache", False)
                )
            elif name == "list_deploys":
                result = client.list_deploys(
                    arguments["service_id"],
                    arguments.get("limit", 10)
                )
            elif name == "list_env_vars":
                result = client.list_env_vars(arguments["service_id"])
            elif name == "set_env_vars":
                result = client.set_env_vars(
                    arguments["service_id"],
                    arguments["env_vars"]
                )
            elif name == "suspend_service":
                result = client.suspend_service(arguments["service_id"])
            elif name == "resume_service":
                result = client.resume_service(arguments["service_id"])
            elif name == "deploy_mini_te_po":
                result = client.deploy_mini_te_po(
                    arguments["service_id"],
                    arguments.get("env_vars")
                )
            elif name == "health_check":
                result = client.health_check(arguments["service_id"])
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
    """Run the Render MCP server."""
    from mcp.server.stdio import stdio_server
    
    server = create_render_server()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
