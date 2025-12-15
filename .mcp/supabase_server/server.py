#!/usr/bin/env python3
"""
Supabase MCP Server
===================
MCP server for Supabase operations within AwaOS.

Provides:
- Table read/write operations
- SQL migrations
- Realm state sync
- Bucket management (PDF, taonga, OCR)
- Trigger function execution
- Vector memory operations

Environment:
    SUPABASE_URL - Your Supabase project URL
    SUPABASE_KEY - Service role key (for admin ops)
    SUPABASE_ANON_KEY - Anonymous key (for client ops)
"""

import os
import json
import asyncio
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, asdict
from datetime import datetime

# MCP SDK imports
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    print("Warning: MCP SDK not installed. Run: pip install mcp")

# Supabase client
try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    print("Warning: Supabase client not installed. Run: pip install supabase")


# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")  # Service role key
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


@dataclass
class SupabaseConfig:
    """Supabase connection configuration."""
    url: str
    service_key: str
    anon_key: str
    
    @property
    def is_configured(self) -> bool:
        return bool(self.url and (self.service_key or self.anon_key))


# ═══════════════════════════════════════════════════════════════
# SUPABASE CLIENT WRAPPER
# ═══════════════════════════════════════════════════════════════

class SupabaseClient:
    """Wrapper for Supabase operations."""
    
    def __init__(self, config: SupabaseConfig):
        self.config = config
        self._client: Optional[Client] = None
    
    @property
    def client(self) -> Client:
        if self._client is None:
            if not HAS_SUPABASE:
                raise RuntimeError("Supabase client not installed")
            key = self.config.service_key or self.config.anon_key
            self._client = create_client(self.config.url, key)
        return self._client
    
    # ─────────────────────────────────────────────────────────
    # TABLE OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def select(
        self, 
        table: str, 
        columns: str = "*",
        limit: int = 20,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict]:
        """Select rows from a table."""
        query = self.client.table(table).select(columns)
        
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        
        query = query.limit(limit)
        result = query.execute()
        return result.data
    
    def insert(self, table: str, data: Dict[str, Any]) -> Dict:
        """Insert a row into a table."""
        result = self.client.table(table).insert(data).execute()
        return result.data[0] if result.data else {}
    
    def update(
        self, 
        table: str, 
        data: Dict[str, Any], 
        match: Dict[str, Any]
    ) -> List[Dict]:
        """Update rows matching criteria."""
        query = self.client.table(table).update(data)
        for key, value in match.items():
            query = query.eq(key, value)
        result = query.execute()
        return result.data
    
    def delete(self, table: str, match: Dict[str, Any]) -> List[Dict]:
        """Delete rows matching criteria."""
        query = self.client.table(table).delete()
        for key, value in match.items():
            query = query.eq(key, value)
        result = query.execute()
        return result.data
    
    def upsert(self, table: str, data: Dict[str, Any]) -> Dict:
        """Upsert a row (insert or update on conflict)."""
        result = self.client.table(table).upsert(data).execute()
        return result.data[0] if result.data else {}
    
    # ─────────────────────────────────────────────────────────
    # RPC FUNCTIONS
    # ─────────────────────────────────────────────────────────
    
    def rpc(self, function: str, params: Optional[Dict] = None) -> Any:
        """Call a Supabase RPC function."""
        result = self.client.rpc(function, params or {}).execute()
        return result.data
    
    def match_memories(
        self,
        query_embedding: List[float],
        realm_id: str,
        match_threshold: float = 0.7,
        match_count: int = 5,
        include_tapu: bool = False
    ) -> List[Dict]:
        """Vector search using match_memories RPC."""
        return self.rpc("match_memories", {
            "query_embedding": query_embedding,
            "match_realm": realm_id,
            "match_threshold": match_threshold,
            "match_count": match_count,
            "include_tapu": include_tapu
        })
    
    # ─────────────────────────────────────────────────────────
    # BUCKET OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def list_buckets(self) -> List[Dict]:
        """List all storage buckets."""
        return self.client.storage.list_buckets()
    
    def list_files(self, bucket: str, path: str = "") -> List[Dict]:
        """List files in a bucket."""
        return self.client.storage.from_(bucket).list(path)
    
    def upload_file(
        self, 
        bucket: str, 
        path: str, 
        file_content: bytes,
        content_type: str = "application/octet-stream"
    ) -> Dict:
        """Upload a file to storage."""
        result = self.client.storage.from_(bucket).upload(
            path, file_content, {"content-type": content_type}
        )
        return {"path": path, "bucket": bucket}
    
    def get_public_url(self, bucket: str, path: str) -> str:
        """Get public URL for a file."""
        return self.client.storage.from_(bucket).get_public_url(path)
    
    # ─────────────────────────────────────────────────────────
    # REALM OPERATIONS
    # ─────────────────────────────────────────────────────────
    
    def register_realm(
        self,
        realm_id: str,
        realm_name: str,
        glyph: str = "koru_blue",
        kaitiaki: Optional[str] = None
    ) -> Dict:
        """Register a new realm in the registry."""
        data = {
            "realm_id": realm_id,
            "name": realm_name,
            "glyph": glyph,
            "kaitiaki": kaitiaki,
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        return self.upsert("realm_registry", data)
    
    def get_realm(self, realm_id: str) -> Optional[Dict]:
        """Get realm details."""
        results = self.select("realm_registry", filters={"realm_id": realm_id}, limit=1)
        return results[0] if results else None
    
    def list_realms(self, limit: int = 50) -> List[Dict]:
        """List all registered realms."""
        return self.select("realm_registry", limit=limit)
    
    # ─────────────────────────────────────────────────────────
    # MIGRATION SUPPORT
    # ─────────────────────────────────────────────────────────
    
    def run_migration(self, sql: str) -> Dict:
        """Execute raw SQL migration (requires service role)."""
        # This would need to go through a Supabase edge function
        # or use the Management API for actual migrations
        return {"status": "migration_queued", "sql_length": len(sql)}
    
    def sync_schema(self, schema_definition: Dict) -> Dict:
        """Sync schema from definition (placeholder for schema management)."""
        return {
            "status": "schema_synced",
            "tables": list(schema_definition.get("tables", {}).keys())
        }


# ═══════════════════════════════════════════════════════════════
# MCP SERVER
# ═══════════════════════════════════════════════════════════════

def create_supabase_server() -> "Server":
    """Create and configure the Supabase MCP server."""
    
    if not HAS_MCP:
        raise RuntimeError("MCP SDK not installed")
    
    server = Server("supabase")
    config = SupabaseConfig(SUPABASE_URL, SUPABASE_KEY, SUPABASE_ANON_KEY)
    client = SupabaseClient(config)
    
    # Register tools
    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="select",
                description="Select rows from a Supabase table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string", "description": "Table name"},
                        "columns": {"type": "string", "default": "*"},
                        "limit": {"type": "integer", "default": 20},
                        "filters": {"type": "object", "description": "Key-value filters"}
                    },
                    "required": ["table"]
                }
            ),
            Tool(
                name="insert",
                description="Insert a row into a Supabase table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string"},
                        "data": {"type": "object"}
                    },
                    "required": ["table", "data"]
                }
            ),
            Tool(
                name="update",
                description="Update rows in a Supabase table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string"},
                        "data": {"type": "object"},
                        "match": {"type": "object"}
                    },
                    "required": ["table", "data", "match"]
                }
            ),
            Tool(
                name="delete",
                description="Delete rows from a Supabase table",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table": {"type": "string"},
                        "match": {"type": "object"}
                    },
                    "required": ["table", "match"]
                }
            ),
            Tool(
                name="rpc",
                description="Call a Supabase RPC function",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "function": {"type": "string"},
                        "params": {"type": "object"}
                    },
                    "required": ["function"]
                }
            ),
            Tool(
                name="match_memories",
                description="Vector search in realm memory",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query_embedding": {"type": "array", "items": {"type": "number"}},
                        "realm_id": {"type": "string"},
                        "threshold": {"type": "number", "default": 0.7},
                        "count": {"type": "integer", "default": 5},
                        "include_tapu": {"type": "boolean", "default": False}
                    },
                    "required": ["query_embedding", "realm_id"]
                }
            ),
            Tool(
                name="list_buckets",
                description="List all storage buckets",
                inputSchema={"type": "object", "properties": {}}
            ),
            Tool(
                name="upload_file",
                description="Upload a file to storage",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "bucket": {"type": "string"},
                        "path": {"type": "string"},
                        "content_base64": {"type": "string"},
                        "content_type": {"type": "string", "default": "application/octet-stream"}
                    },
                    "required": ["bucket", "path", "content_base64"]
                }
            ),
            Tool(
                name="register_realm",
                description="Register a new realm in the registry",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "realm_id": {"type": "string"},
                        "realm_name": {"type": "string"},
                        "glyph": {"type": "string", "default": "koru_blue"},
                        "kaitiaki": {"type": "string"}
                    },
                    "required": ["realm_id", "realm_name"]
                }
            ),
            Tool(
                name="list_realms",
                description="List all registered realms",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {"type": "integer", "default": 50}
                    }
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        try:
            if name == "select":
                result = client.select(
                    arguments["table"],
                    arguments.get("columns", "*"),
                    arguments.get("limit", 20),
                    arguments.get("filters")
                )
            elif name == "insert":
                result = client.insert(arguments["table"], arguments["data"])
            elif name == "update":
                result = client.update(
                    arguments["table"],
                    arguments["data"],
                    arguments["match"]
                )
            elif name == "delete":
                result = client.delete(arguments["table"], arguments["match"])
            elif name == "rpc":
                result = client.rpc(arguments["function"], arguments.get("params"))
            elif name == "match_memories":
                result = client.match_memories(
                    arguments["query_embedding"],
                    arguments["realm_id"],
                    arguments.get("threshold", 0.7),
                    arguments.get("count", 5),
                    arguments.get("include_tapu", False)
                )
            elif name == "list_buckets":
                result = client.list_buckets()
            elif name == "upload_file":
                import base64
                content = base64.b64decode(arguments["content_base64"])
                result = client.upload_file(
                    arguments["bucket"],
                    arguments["path"],
                    content,
                    arguments.get("content_type", "application/octet-stream")
                )
            elif name == "register_realm":
                result = client.register_realm(
                    arguments["realm_id"],
                    arguments["realm_name"],
                    arguments.get("glyph", "koru_blue"),
                    arguments.get("kaitiaki")
                )
            elif name == "list_realms":
                result = client.list_realms(arguments.get("limit", 50))
            else:
                result = {"error": f"Unknown tool: {name}"}
            
            return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
        except Exception as e:
            return [TextContent(type="text", text=json.dumps({"error": str(e)}))]
    
    return server


# ═══════════════════════════════════════════════════════════════
# COMMANDS.JSON SCHEMA
# ═══════════════════════════════════════════════════════════════

COMMANDS_SCHEMA = {
    "name": "supabase",
    "description": "Supabase MCP Server for AwaOS",
    "version": "1.0.0",
    "commands": {
        "select": {
            "description": "Select rows from a table",
            "params": ["table", "columns?", "limit?", "filters?"]
        },
        "insert": {
            "description": "Insert a row",
            "params": ["table", "data"]
        },
        "update": {
            "description": "Update rows",
            "params": ["table", "data", "match"]
        },
        "delete": {
            "description": "Delete rows",
            "params": ["table", "match"]
        },
        "rpc": {
            "description": "Call RPC function",
            "params": ["function", "params?"]
        },
        "match_memories": {
            "description": "Vector search",
            "params": ["query_embedding", "realm_id", "threshold?", "count?"]
        },
        "list_buckets": {
            "description": "List storage buckets",
            "params": []
        },
        "upload_file": {
            "description": "Upload file to storage",
            "params": ["bucket", "path", "content_base64", "content_type?"]
        },
        "register_realm": {
            "description": "Register a realm",
            "params": ["realm_id", "realm_name", "glyph?", "kaitiaki?"]
        },
        "list_realms": {
            "description": "List all realms",
            "params": ["limit?"]
        }
    }
}


# ═══════════════════════════════════════════════════════════════
# MAIN ENTRY
# ═══════════════════════════════════════════════════════════════

async def main():
    """Run the Supabase MCP server."""
    from mcp.server.stdio import stdio_server
    
    server = create_supabase_server()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
