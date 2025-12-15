#!/usr/bin/env python3
"""
Te Pō MCP Server
================
MCP server for direct communication with Te Pō backend.

This is the main gateway to your AwaOS backbone.

Provides:
- Whiro context queries
- Vector memory operations
- Pipeline execution
- Kaitiaki invocation
- Bearer token generation
- Realm alignment logs
- OCR/PDF summarise triggers

Environment:
    TEPO_URL - Te Pō backend URL
    TEPO_BEARER - Bearer token for authentication
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
    import httpx
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

TEPO_URL = os.getenv("TEPO_URL", "")
TEPO_BEARER = os.getenv("TEPO_BEARER", "")
TIMEOUT = float(os.getenv("TEPO_TIMEOUT", "120"))


@dataclass
class TePoConfig:
    """Te Pō configuration."""
    url: str
    bearer: str
    timeout: float = 120.0
    
    @property
    def is_configured(self) -> bool:
        return bool(self.url)


# ═══════════════════════════════════════════════════════════════
# TE PŌ CLIENT
# ═══════════════════════════════════════════════════════════════

class TePoClient:
    """Te Pō backend operations wrapper."""
    
    def __init__(self, config: TePoConfig):
        self.config = config
    
    def _headers(self) -> Dict[str, str]:
        """Get API headers."""
        headers = {"Content-Type": "application/json"}
        if self.config.bearer:
            headers["Authorization"] = f"Bearer {self.config.bearer}"
        return headers
    
    def _call(self, route: str, payload: Optional[Dict] = None, method: str = "POST") -> Dict:
        """Make a request to Te Pō."""
        if not self.config.is_configured:
            return {"error": "TEPO_URL not configured"}
        
        url = f"{self.config.url}/{route.lstrip('/')}"
        
        try:
            if method == "GET":
                response = requests.get(
                    url,
                    params=payload,
                    headers=self._headers(),
                    timeout=self.config.timeout
                )
            else:
                response = requests.post(
                    url,
                    json=payload or {},
                    headers=self._headers(),
                    timeout=self.config.timeout
                )
            
            if response.status_code == 200:
                return response.json()
            
            return {"error": response.text, "status_code": response.status_code}
        
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except requests.exceptions.ConnectionError:
            return {"error": f"Cannot connect to Te Pō at {self.config.url}"}
        except Exception as e:
            return {"error": str(e)}
    
    # ─────────────────────────────────────────────────────────
    # AWA PROTOCOL ROUTES
    # ─────────────────────────────────────────────────────────
    
    def awa_query(self, route: str, payload: Optional[Dict] = None) -> Dict:
        """Generic Awa Protocol query."""
        return self._call(f"awa/{route}", payload)
    
    def awa_envelope(self, realm_id: str, content: Any, kaitiaki: Optional[str] = None) -> Dict:
        """Wrap message with realm context."""
        payload = {
            "realm_id": realm_id,
            "content": content,
            "kaitiaki": kaitiaki
        }
        return self._call("awa/envelope", payload)
    
    def awa_task(self, task_type: str, input_data: Any, realm_id: str, options: Optional[Dict] = None) -> Dict:
        """Execute a kaitiaki task."""
        payload = {
            "task_type": task_type,
            "input": input_data,
            "realm_id": realm_id,
            "options": options
        }
        return self._call("awa/task", payload)
    
    def awa_handoff(self, from_kaitiaki: str, to_kaitiaki: str, context: Dict) -> Dict:
        """Hand off task between kaitiaki."""
        payload = {
            "from": from_kaitiaki,
            "to": to_kaitiaki,
            "context": context
        }
        return self._call("awa/handoff", payload)
    
    # ─────────────────────────────────────────────────────────
    # MEMORY OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def memory_query(
        self, 
        query: str, 
        realm_id: str, 
        limit: int = 5,
        threshold: float = 0.7
    ) -> Dict:
        """Query vector memory."""
        payload = {
            "query": query,
            "realm_id": realm_id,
            "limit": limit,
            "threshold": threshold
        }
        return self._call("awa/memory/query", payload)
    
    def memory_store(
        self, 
        content: str, 
        realm_id: str, 
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Store content to vector memory."""
        payload = {
            "content": content,
            "realm_id": realm_id,
            "metadata": metadata
        }
        return self._call("awa/memory/store", payload)
    
    # ─────────────────────────────────────────────────────────
    # VECTOR OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def vector_embed(self, text: str, realm_id: Optional[str] = None) -> Dict:
        """Generate embeddings for text."""
        payload = {"text": text, "realm_id": realm_id}
        return self._call("awa/vector/embed", payload)
    
    def vector_search(
        self, 
        query: str, 
        realm_id: str, 
        limit: int = 5
    ) -> Dict:
        """Semantic search in vector store."""
        payload = {
            "query": query,
            "realm_id": realm_id,
            "limit": limit
        }
        return self._call("awa/vector/search", payload)
    
    # ─────────────────────────────────────────────────────────
    # KAITIAKI OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def kaitiaki_register(
        self, 
        name: str, 
        realm_id: str, 
        manifest: Dict
    ) -> Dict:
        """Register a kaitiaki with Te Pō."""
        payload = {
            "name": name,
            "realm_id": realm_id,
            "manifest": manifest
        }
        return self._call("awa/kaitiaki/register", payload)
    
    def kaitiaki_context(self, name: str, realm_id: str) -> Dict:
        """Get kaitiaki context."""
        payload = {"name": name, "realm_id": realm_id}
        return self._call("awa/kaitiaki/context", payload)
    
    def kaitiaki_invoke(
        self, 
        name: str, 
        action: str, 
        params: Optional[Dict] = None
    ) -> Dict:
        """Invoke a kaitiaki action."""
        payload = {
            "kaitiaki": name,
            "action": action,
            "params": params
        }
        return self._call("awa/kaitiaki/invoke", payload)
    
    def kaitiaki_list(self) -> Dict:
        """List all registered kaitiaki."""
        return self._call("awa/kaitiaki/list", method="GET")
    
    # ─────────────────────────────────────────────────────────
    # PIPELINE OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def pipeline_run(
        self, 
        pipeline: str, 
        input_data: Any, 
        realm_id: str,
        options: Optional[Dict] = None
    ) -> Dict:
        """Run a pipeline (ocr, summarise, translate, embed, etc.)."""
        payload = {
            "pipeline": pipeline,
            "input": input_data,
            "realm_id": realm_id,
            "options": options
        }
        return self._call("awa/pipeline", payload)
    
    def ocr_image(self, image_url: str, realm_id: str) -> Dict:
        """OCR an image."""
        return self.pipeline_run("ocr", {"url": image_url}, realm_id)
    
    def pdf_summarise(self, file_url: str, realm_id: str) -> Dict:
        """Summarise a PDF document."""
        return self.pipeline_run("summarise", {"url": file_url}, realm_id)
    
    def translate(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str,
        dialect: str = "standard"
    ) -> Dict:
        """Translate text."""
        return self.pipeline_run("translate", {
            "text": text,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "dialect": dialect
        }, realm_id="global")
    
    # ─────────────────────────────────────────────────────────
    # LOGGING & NOTIFICATIONS
    # ─────────────────────────────────────────────────────────
    
    def log(self, realm_id: str, event: str, data: Optional[Dict] = None) -> Dict:
        """Log activity to Te Pō."""
        payload = {
            "realm_id": realm_id,
            "event": event,
            "data": data
        }
        return self._call("awa/log", payload)
    
    def notify(self, realm_id: str, message: str, channel: str = "default") -> Dict:
        """Send notification via Te Pō."""
        payload = {
            "realm_id": realm_id,
            "message": message,
            "channel": channel
        }
        return self._call("awa/notify", payload)
    
    # ─────────────────────────────────────────────────────────
    # REALM OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def realm_register(self, realm_id: str, name: str, glyph: str = "koru_blue") -> Dict:
        """Register a new realm."""
        payload = {
            "realm_id": realm_id,
            "name": name,
            "glyph": glyph
        }
        return self._call("realms/register", payload)
    
    def realm_info(self, realm_id: str) -> Dict:
        """Get realm information."""
        return self._call(f"realms/{realm_id}", method="GET")
    
    def realm_list(self) -> Dict:
        """List all realms."""
        return self._call("realms", method="GET")
    
    # ─────────────────────────────────────────────────────────
    # MAURI OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def mauri_check(self, realm_id: str, seal_hash: str) -> Dict:
        """Verify mauri seal."""
        payload = {
            "realm_id": realm_id,
            "seal_hash": seal_hash
        }
        return self._call("mauri/check", payload)
    
    def mauri_seal(self, realm_id: str, manifest: Dict) -> Dict:
        """Create mauri seal for a realm."""
        payload = {
            "realm_id": realm_id,
            "manifest": manifest
        }
        return self._call("mauri/seal", payload)


# ═══════════════════════════════════════════════════════════════
# MCP SERVER
# ═══════════════════════════════════════════════════════════════

def create_tepo_server() -> "Server":
    """Create and configure the Te Pō MCP server."""
    
    if not HAS_MCP:
        raise RuntimeError("MCP SDK not installed")
    
    server = Server("tepo")
    config = TePoConfig(TEPO_URL, TEPO_BEARER, TIMEOUT)
    client = TePoClient(config)
    
    @server.list_tools()
    async def list_tools():
        return [
            # Awa Protocol
            Tool(
                name="awa_query",
                description="Generic Awa Protocol query to Te Pō",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "route": {"type": "string", "description": "Awa route (e.g., 'memory/query')"},
                        "payload": {"type": "object"}
                    },
                    "required": ["route"]
                }
            ),
            Tool(
                name="awa_task",
                description="Execute a kaitiaki task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_type": {"type": "string", "description": "chat, summarise, translate, embed, ocr"},
                        "input": {"description": "Task input data"},
                        "realm_id": {"type": "string"},
                        "options": {"type": "object"}
                    },
                    "required": ["task_type", "input", "realm_id"]
                }
            ),
            
            # Memory
            Tool(
                name="memory_query",
                description="Query vector memory for relevant context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "realm_id": {"type": "string"},
                        "limit": {"type": "integer", "default": 5},
                        "threshold": {"type": "number", "default": 0.7}
                    },
                    "required": ["query", "realm_id"]
                }
            ),
            Tool(
                name="memory_store",
                description="Store content to vector memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content": {"type": "string"},
                        "realm_id": {"type": "string"},
                        "metadata": {"type": "object"}
                    },
                    "required": ["content", "realm_id"]
                }
            ),
            
            # Vector
            Tool(
                name="vector_embed",
                description="Generate embeddings for text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "realm_id": {"type": "string"}
                    },
                    "required": ["text"]
                }
            ),
            Tool(
                name="vector_search",
                description="Semantic search in vector store",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "realm_id": {"type": "string"},
                        "limit": {"type": "integer", "default": 5}
                    },
                    "required": ["query", "realm_id"]
                }
            ),
            
            # Kaitiaki
            Tool(
                name="kaitiaki_invoke",
                description="Invoke a kaitiaki action",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "action": {"type": "string"},
                        "params": {"type": "object"}
                    },
                    "required": ["name", "action"]
                }
            ),
            Tool(
                name="kaitiaki_context",
                description="Get kaitiaki context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "realm_id": {"type": "string"}
                    },
                    "required": ["name", "realm_id"]
                }
            ),
            
            # Pipelines
            Tool(
                name="pipeline_run",
                description="Run a pipeline (ocr, summarise, translate, embed, taonga)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "pipeline": {"type": "string"},
                        "input": {"description": "Pipeline input"},
                        "realm_id": {"type": "string"},
                        "options": {"type": "object"}
                    },
                    "required": ["pipeline", "input", "realm_id"]
                }
            ),
            Tool(
                name="ocr_image",
                description="OCR an image",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "image_url": {"type": "string"},
                        "realm_id": {"type": "string"}
                    },
                    "required": ["image_url", "realm_id"]
                }
            ),
            Tool(
                name="pdf_summarise",
                description="Summarise a PDF document",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "file_url": {"type": "string"},
                        "realm_id": {"type": "string"}
                    },
                    "required": ["file_url", "realm_id"]
                }
            ),
            Tool(
                name="translate",
                description="Translate text",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "text": {"type": "string"},
                        "source_lang": {"type": "string"},
                        "target_lang": {"type": "string"},
                        "dialect": {"type": "string", "default": "standard"}
                    },
                    "required": ["text", "source_lang", "target_lang"]
                }
            ),
            
            # Realm & Mauri
            Tool(
                name="realm_info",
                description="Get realm information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "realm_id": {"type": "string"}
                    },
                    "required": ["realm_id"]
                }
            ),
            Tool(
                name="mauri_check",
                description="Verify mauri seal integrity",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "realm_id": {"type": "string"},
                        "seal_hash": {"type": "string"}
                    },
                    "required": ["realm_id", "seal_hash"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "awa_query":
                result = client.awa_query(arguments["route"], arguments.get("payload"))
            elif name == "awa_task":
                result = client.awa_task(
                    arguments["task_type"],
                    arguments["input"],
                    arguments["realm_id"],
                    arguments.get("options")
                )
            elif name == "memory_query":
                result = client.memory_query(
                    arguments["query"],
                    arguments["realm_id"],
                    arguments.get("limit", 5),
                    arguments.get("threshold", 0.7)
                )
            elif name == "memory_store":
                result = client.memory_store(
                    arguments["content"],
                    arguments["realm_id"],
                    arguments.get("metadata")
                )
            elif name == "vector_embed":
                result = client.vector_embed(
                    arguments["text"],
                    arguments.get("realm_id")
                )
            elif name == "vector_search":
                result = client.vector_search(
                    arguments["query"],
                    arguments["realm_id"],
                    arguments.get("limit", 5)
                )
            elif name == "kaitiaki_invoke":
                result = client.kaitiaki_invoke(
                    arguments["name"],
                    arguments["action"],
                    arguments.get("params")
                )
            elif name == "kaitiaki_context":
                result = client.kaitiaki_context(
                    arguments["name"],
                    arguments["realm_id"]
                )
            elif name == "pipeline_run":
                result = client.pipeline_run(
                    arguments["pipeline"],
                    arguments["input"],
                    arguments["realm_id"],
                    arguments.get("options")
                )
            elif name == "ocr_image":
                result = client.ocr_image(
                    arguments["image_url"],
                    arguments["realm_id"]
                )
            elif name == "pdf_summarise":
                result = client.pdf_summarise(
                    arguments["file_url"],
                    arguments["realm_id"]
                )
            elif name == "translate":
                result = client.translate(
                    arguments["text"],
                    arguments["source_lang"],
                    arguments["target_lang"],
                    arguments.get("dialect", "standard")
                )
            elif name == "realm_info":
                result = client.realm_info(arguments["realm_id"])
            elif name == "mauri_check":
                result = client.mauri_check(
                    arguments["realm_id"],
                    arguments["seal_hash"]
                )
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
    """Run the Te Pō MCP server."""
    from mcp.server.stdio import stdio_server
    
    server = create_tepo_server()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
