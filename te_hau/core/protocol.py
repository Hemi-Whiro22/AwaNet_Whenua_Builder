"""
Awa Protocol (Drop 13)
======================
The 12 official routes and envelope system for AwaOS.

"Awa" (water/stream) represents the flow of context between
kaitiaki, realms, and memories.

This defines:
- Awa Envelope (message wrapper)
- Protocol routes
- Contract validation
- Message routing
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import uuid


# ═══════════════════════════════════════════════════════════════
# AWA ENVELOPE
# ═══════════════════════════════════════════════════════════════

@dataclass
class AwaEnvelope:
    """
    The universal message wrapper for all AwaOS communication.
    
    Every message flows through the Awa - this envelope ensures
    proper context, routing, and auditability.
    
    Structure:
    {
        "envelope_id": "uuid",
        "timestamp": "iso8601",
        "source": {
            "kaitiaki": "whiro",
            "realm_id": "global"
        },
        "target": {
            "route": "/awa/task",
            "kaitiaki": "awanui"
        },
        "payload": { ... },
        "context": {
            "lineage": ["whiro"],
            "trace_id": "uuid",
            "mauri_seal": "hash"
        }
    }
    """
    
    # Identity
    envelope_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    # Source
    source_kaitiaki: str = "whiro"
    source_realm: str = "global"
    
    # Target
    target_route: str = "/awa/task"
    target_kaitiaki: Optional[str] = None
    
    # Payload
    payload: Dict[str, Any] = field(default_factory=dict)
    
    # Context
    lineage: List[str] = field(default_factory=list)
    trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mauri_seal: str = ""
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "envelope_id": self.envelope_id,
            "timestamp": self.timestamp,
            "source": {
                "kaitiaki": self.source_kaitiaki,
                "realm_id": self.source_realm
            },
            "target": {
                "route": self.target_route,
                "kaitiaki": self.target_kaitiaki
            },
            "payload": self.payload,
            "context": {
                "lineage": self.lineage,
                "trace_id": self.trace_id,
                "mauri_seal": self.mauri_seal
            },
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "AwaEnvelope":
        source = data.get("source", {})
        target = data.get("target", {})
        context = data.get("context", {})
        
        return cls(
            envelope_id=data.get("envelope_id", str(uuid.uuid4())),
            timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            source_kaitiaki=source.get("kaitiaki", "whiro"),
            source_realm=source.get("realm_id", "global"),
            target_route=target.get("route", "/awa/task"),
            target_kaitiaki=target.get("kaitiaki"),
            payload=data.get("payload", {}),
            lineage=context.get("lineage", []),
            trace_id=context.get("trace_id", str(uuid.uuid4())),
            mauri_seal=context.get("mauri_seal", ""),
            metadata=data.get("metadata", {})
        )
    
    def seal(self, secret: str = "") -> str:
        """Generate mauri seal for this envelope."""
        content = json.dumps({
            "envelope_id": self.envelope_id,
            "source": self.source_kaitiaki,
            "target": self.target_route,
            "payload": self.payload,
            "timestamp": self.timestamp
        }, sort_keys=True)
        
        seal_input = f"{content}:{secret}" if secret else content
        self.mauri_seal = hashlib.sha256(seal_input.encode()).hexdigest()[:16]
        return self.mauri_seal
    
    def verify_seal(self, secret: str = "") -> bool:
        """Verify the mauri seal."""
        expected = self.seal(secret)
        return expected == self.mauri_seal


# ═══════════════════════════════════════════════════════════════
# AWA PROTOCOL ROUTES
# ═══════════════════════════════════════════════════════════════

class AwaRoute(str, Enum):
    """The 12 official Awa Protocol routes."""
    
    # Core
    ENVELOPE = "/awa/envelope"          # Wrap message with context
    TASK = "/awa/task"                  # Execute a task
    HANDOFF = "/awa/handoff"            # Transfer between kaitiaki
    
    # Memory
    MEMORY_QUERY = "/awa/memory/query"  # Query vector memory
    MEMORY_STORE = "/awa/memory/store"  # Store to vector memory
    
    # Logging & Notifications
    LOG = "/awa/log"                    # Log activity
    NOTIFY = "/awa/notify"              # Send notification
    
    # Kaitiaki Management
    KAITIAKI_REGISTER = "/awa/kaitiaki/register"  # Register kaitiaki
    KAITIAKI_CONTEXT = "/awa/kaitiaki/context"    # Get kaitiaki context
    
    # Vector Operations
    VECTOR_EMBED = "/awa/vector/embed"    # Generate embeddings
    VECTOR_SEARCH = "/awa/vector/search"  # Semantic search
    
    # Pipelines
    PIPELINE = "/awa/pipeline"          # Run pipeline


@dataclass
class RouteContract:
    """Contract defining a route's requirements."""
    route: AwaRoute
    method: str = "POST"
    description: str = ""
    required_fields: List[str] = field(default_factory=list)
    optional_fields: List[str] = field(default_factory=list)
    returns: str = "AwaEnvelope"
    permissions: List[str] = field(default_factory=list)


# The official route contracts
ROUTE_CONTRACTS: Dict[AwaRoute, RouteContract] = {
    AwaRoute.ENVELOPE: RouteContract(
        route=AwaRoute.ENVELOPE,
        description="Wrap a message with realm context and routing info",
        required_fields=["payload", "target_route"],
        optional_fields=["source_kaitiaki", "target_kaitiaki", "metadata"]
    ),
    
    AwaRoute.TASK: RouteContract(
        route=AwaRoute.TASK,
        description="Execute a task through a kaitiaki",
        required_fields=["task_type", "input"],
        optional_fields=["options", "timeout_ms"]
    ),
    
    AwaRoute.HANDOFF: RouteContract(
        route=AwaRoute.HANDOFF,
        description="Hand off context from one kaitiaki to another",
        required_fields=["from_kaitiaki", "to_kaitiaki", "context"],
        optional_fields=["reason"]
    ),
    
    AwaRoute.MEMORY_QUERY: RouteContract(
        route=AwaRoute.MEMORY_QUERY,
        description="Query vector memory with semantic search",
        required_fields=["query"],
        optional_fields=["realm_id", "kaitiaki", "limit", "threshold"]
    ),
    
    AwaRoute.MEMORY_STORE: RouteContract(
        route=AwaRoute.MEMORY_STORE,
        description="Store content to vector memory",
        required_fields=["content", "type"],
        optional_fields=["realm_id", "kaitiaki", "metadata"]
    ),
    
    AwaRoute.LOG: RouteContract(
        route=AwaRoute.LOG,
        description="Log an activity or event",
        required_fields=["event", "level"],
        optional_fields=["details", "kaitiaki", "realm_id"]
    ),
    
    AwaRoute.NOTIFY: RouteContract(
        route=AwaRoute.NOTIFY,
        description="Send a notification to a user or system",
        required_fields=["message", "channel"],
        optional_fields=["priority", "metadata"]
    ),
    
    AwaRoute.KAITIAKI_REGISTER: RouteContract(
        route=AwaRoute.KAITIAKI_REGISTER,
        description="Register a new kaitiaki with the system",
        required_fields=["name", "role", "purpose"],
        optional_fields=["glyph", "tools", "capabilities", "lineage"]
    ),
    
    AwaRoute.KAITIAKI_CONTEXT: RouteContract(
        route=AwaRoute.KAITIAKI_CONTEXT,
        description="Get the current context for a kaitiaki",
        required_fields=["kaitiaki"],
        optional_fields=["include_memory", "include_lineage"]
    ),
    
    AwaRoute.VECTOR_EMBED: RouteContract(
        route=AwaRoute.VECTOR_EMBED,
        description="Generate embeddings for text content",
        required_fields=["text"],
        optional_fields=["model"]
    ),
    
    AwaRoute.VECTOR_SEARCH: RouteContract(
        route=AwaRoute.VECTOR_SEARCH,
        description="Perform semantic search across vectors",
        required_fields=["query", "table"],
        optional_fields=["limit", "threshold", "filters"]
    ),
    
    AwaRoute.PIPELINE: RouteContract(
        route=AwaRoute.PIPELINE,
        description="Run a processing pipeline",
        required_fields=["pipeline_id", "input"],
        optional_fields=["options", "realm_id"]
    )
}


# ═══════════════════════════════════════════════════════════════
# CONTRACT VALIDATOR
# ═══════════════════════════════════════════════════════════════

class ContractValidator:
    """Validates messages against route contracts."""
    
    def __init__(self):
        self.contracts = ROUTE_CONTRACTS
    
    def validate(self, envelope: AwaEnvelope) -> tuple[bool, List[str]]:
        """
        Validate an envelope against its route contract.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Get route contract
        try:
            route = AwaRoute(envelope.target_route)
        except ValueError:
            return False, [f"Unknown route: {envelope.target_route}"]
        
        contract = self.contracts.get(route)
        if not contract:
            return False, [f"No contract defined for: {route}"]
        
        # Check required fields
        payload = envelope.payload
        for field in contract.required_fields:
            if field not in payload or payload[field] is None:
                errors.append(f"Missing required field: {field}")
        
        return len(errors) == 0, errors
    
    def get_contract(self, route: Union[str, AwaRoute]) -> Optional[RouteContract]:
        """Get the contract for a route."""
        if isinstance(route, str):
            try:
                route = AwaRoute(route)
            except ValueError:
                return None
        return self.contracts.get(route)
    
    def list_contracts(self) -> List[Dict]:
        """List all route contracts."""
        return [
            {
                "route": c.route.value,
                "method": c.method,
                "description": c.description,
                "required_fields": c.required_fields,
                "optional_fields": c.optional_fields
            }
            for c in self.contracts.values()
        ]


# ═══════════════════════════════════════════════════════════════
# AWA ROUTER
# ═══════════════════════════════════════════════════════════════

class AwaRouter:
    """
    Routes Awa Protocol messages to appropriate handlers.
    
    This is the main entry point for all Awa communication.
    """
    
    def __init__(self):
        self.handlers: Dict[AwaRoute, callable] = {}
        self.validator = ContractValidator()
        self.middleware: List[callable] = []
    
    def register_handler(self, route: AwaRoute, handler: callable):
        """Register a handler for a route."""
        self.handlers[route] = handler
    
    def add_middleware(self, middleware: callable):
        """Add middleware that runs before handlers."""
        self.middleware.append(middleware)
    
    async def route(self, envelope: AwaEnvelope) -> AwaEnvelope:
        """
        Route an envelope to its handler.
        
        Process:
        1. Validate against contract
        2. Run middleware
        3. Execute handler
        4. Return response envelope
        """
        # Validate
        is_valid, errors = self.validator.validate(envelope)
        if not is_valid:
            return self._error_envelope(envelope, errors)
        
        # Get route
        try:
            route = AwaRoute(envelope.target_route)
        except ValueError:
            return self._error_envelope(envelope, ["Unknown route"])
        
        # Run middleware
        for mw in self.middleware:
            envelope = await mw(envelope)
            if envelope.payload.get("error"):
                return envelope
        
        # Get handler
        handler = self.handlers.get(route)
        if not handler:
            return self._error_envelope(envelope, ["No handler registered"])
        
        # Execute
        try:
            response = await handler(envelope)
            return response if isinstance(response, AwaEnvelope) else self._success_envelope(envelope, response)
        
        except Exception as e:
            return self._error_envelope(envelope, [str(e)])
    
    def _error_envelope(self, original: AwaEnvelope, errors: List[str]) -> AwaEnvelope:
        """Create an error response envelope."""
        return AwaEnvelope(
            source_kaitiaki=original.target_kaitiaki or "system",
            source_realm=original.source_realm,
            target_route=original.target_route,
            payload={"error": True, "errors": errors},
            lineage=original.lineage + [original.source_kaitiaki],
            trace_id=original.trace_id
        )
    
    def _success_envelope(self, original: AwaEnvelope, result: Any) -> AwaEnvelope:
        """Create a success response envelope."""
        return AwaEnvelope(
            source_kaitiaki=original.target_kaitiaki or "system",
            source_realm=original.source_realm,
            target_route=original.target_route,
            payload={"success": True, "result": result},
            lineage=original.lineage + [original.source_kaitiaki],
            trace_id=original.trace_id
        )


# ═══════════════════════════════════════════════════════════════
# AWA CLIENT
# ═══════════════════════════════════════════════════════════════

class AwaClient:
    """
    Client for making Awa Protocol requests.
    
    Usage:
        client = AwaClient(kaitiaki="awanui", realm="te_reo")
        result = await client.task("translate", {"text": "Hello"})
    """
    
    def __init__(
        self,
        kaitiaki: str = "whiro",
        realm: str = "global",
        router: Optional[AwaRouter] = None,
        api_base: str = ""
    ):
        self.kaitiaki = kaitiaki
        self.realm = realm
        self.router = router
        self.api_base = api_base or os.getenv("AWA_API_BASE", "http://localhost:8000")
    
    def _create_envelope(self, route: str, payload: Dict) -> AwaEnvelope:
        """Create an envelope for a request."""
        envelope = AwaEnvelope(
            source_kaitiaki=self.kaitiaki,
            source_realm=self.realm,
            target_route=route,
            payload=payload,
            lineage=[self.kaitiaki]
        )
        envelope.seal()
        return envelope
    
    async def _send(self, envelope: AwaEnvelope) -> AwaEnvelope:
        """Send envelope to router or API."""
        if self.router:
            return await self.router.route(envelope)
        
        # HTTP fallback
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}{envelope.target_route}",
                json=envelope.to_dict()
            ) as response:
                data = await response.json()
                return AwaEnvelope.from_dict(data)
    
    # Convenience methods for each route
    
    async def wrap(self, payload: Dict, target_route: str) -> AwaEnvelope:
        """Wrap a payload in an envelope."""
        return self._create_envelope(AwaRoute.ENVELOPE.value, {
            "payload": payload,
            "target_route": target_route
        })
    
    async def task(
        self, 
        task_type: str, 
        input_data: Any,
        options: Optional[Dict] = None
    ) -> Dict:
        """Execute a task."""
        envelope = self._create_envelope(AwaRoute.TASK.value, {
            "task_type": task_type,
            "input": input_data,
            "options": options or {}
        })
        response = await self._send(envelope)
        return response.payload
    
    async def handoff(
        self,
        to_kaitiaki: str,
        context: Dict,
        reason: str = ""
    ) -> Dict:
        """Hand off to another kaitiaki."""
        envelope = self._create_envelope(AwaRoute.HANDOFF.value, {
            "from_kaitiaki": self.kaitiaki,
            "to_kaitiaki": to_kaitiaki,
            "context": context,
            "reason": reason
        })
        response = await self._send(envelope)
        return response.payload
    
    async def memory_query(
        self,
        query: str,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Dict]:
        """Query vector memory."""
        envelope = self._create_envelope(AwaRoute.MEMORY_QUERY.value, {
            "query": query,
            "realm_id": self.realm,
            "kaitiaki": self.kaitiaki,
            "limit": limit,
            "threshold": threshold
        })
        response = await self._send(envelope)
        return response.payload.get("result", [])
    
    async def memory_store(
        self,
        content: str,
        content_type: str = "message",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """Store to vector memory."""
        envelope = self._create_envelope(AwaRoute.MEMORY_STORE.value, {
            "content": content,
            "type": content_type,
            "realm_id": self.realm,
            "kaitiaki": self.kaitiaki,
            "metadata": metadata or {}
        })
        response = await self._send(envelope)
        return response.payload
    
    async def log(
        self,
        event: str,
        level: str = "info",
        details: Optional[Dict] = None
    ) -> Dict:
        """Log an event."""
        envelope = self._create_envelope(AwaRoute.LOG.value, {
            "event": event,
            "level": level,
            "details": details or {},
            "kaitiaki": self.kaitiaki,
            "realm_id": self.realm
        })
        response = await self._send(envelope)
        return response.payload
    
    async def notify(
        self,
        message: str,
        channel: str = "system",
        priority: str = "normal"
    ) -> Dict:
        """Send a notification."""
        envelope = self._create_envelope(AwaRoute.NOTIFY.value, {
            "message": message,
            "channel": channel,
            "priority": priority
        })
        response = await self._send(envelope)
        return response.payload
    
    async def embed(self, text: str, model: str = "text-embedding-3-small") -> List[float]:
        """Generate embeddings."""
        envelope = self._create_envelope(AwaRoute.VECTOR_EMBED.value, {
            "text": text,
            "model": model
        })
        response = await self._send(envelope)
        return response.payload.get("result", [])
    
    async def search(
        self,
        query: str,
        table: str,
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """Semantic search."""
        envelope = self._create_envelope(AwaRoute.VECTOR_SEARCH.value, {
            "query": query,
            "table": table,
            "limit": limit,
            "filters": filters or {}
        })
        response = await self._send(envelope)
        return response.payload.get("result", [])
    
    async def pipeline(
        self,
        pipeline_id: str,
        input_data: Any,
        options: Optional[Dict] = None
    ) -> Dict:
        """Run a pipeline."""
        envelope = self._create_envelope(AwaRoute.PIPELINE.value, {
            "pipeline_id": pipeline_id,
            "input": input_data,
            "options": options or {},
            "realm_id": self.realm
        })
        response = await self._send(envelope)
        return response.payload
    
    async def register_kaitiaki(
        self,
        name: str,
        role: str,
        purpose: List[str],
        **kwargs
    ) -> Dict:
        """Register a kaitiaki."""
        envelope = self._create_envelope(AwaRoute.KAITIAKI_REGISTER.value, {
            "name": name,
            "role": role,
            "purpose": purpose,
            **kwargs
        })
        response = await self._send(envelope)
        return response.payload
    
    async def get_kaitiaki_context(
        self,
        kaitiaki: str,
        include_memory: bool = True,
        include_lineage: bool = True
    ) -> Dict:
        """Get kaitiaki context."""
        envelope = self._create_envelope(AwaRoute.KAITIAKI_CONTEXT.value, {
            "kaitiaki": kaitiaki,
            "include_memory": include_memory,
            "include_lineage": include_lineage
        })
        response = await self._send(envelope)
        return response.payload


# ═══════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════

def create_awa_router_with_defaults() -> AwaRouter:
    """Create an Awa router with default handlers."""
    router = AwaRouter()
    
    # Register placeholder handlers
    async def placeholder_handler(envelope: AwaEnvelope) -> Dict:
        return {
            "status": "placeholder",
            "route": envelope.target_route,
            "message": "Handler not implemented"
        }
    
    for route in AwaRoute:
        router.register_handler(route, placeholder_handler)
    
    return router
