"""
Kaitiaki Orchestrator (Drop 12)
===============================
Multi-agent coordination and task routing for AwaOS.

Features:
- Multi-kaitiaki cluster management
- Task routing based on capabilities
- Shared memory bus (SMB)
- Chain-of-thought handoffs
- Context fusion
- Lineage graph enforcement

From the Awa Protocol spec:
"Instead of 1 assistant (Kitenga Whiro), you now have a cluster...
Each project gets its own realm kaitiaki."
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# KAITIAKI TYPES
# ═══════════════════════════════════════════════════════════════

class KaitiakiType(str, Enum):
    """Types of kaitiaki in the cluster."""
    GLOBAL = "global"      # System-level (Kitenga Whiro)
    REALM = "realm"        # Project-specific
    SPECIALIST = "specialist"  # Task-specific (OCR, translate)


class TaskType(str, Enum):
    """Types of tasks that can be routed."""
    CHAT = "chat"
    OCR = "ocr"
    TRANSLATE = "translate"
    SUMMARISE = "summarise"
    EMBED = "embed"
    CLASSIFY = "classify"
    RESEARCH = "research"
    PIPELINE = "pipeline"


@dataclass
class KaitiakiManifest:
    """
    Manifest for a kaitiaki agent.
    
    Stored in: mauri/kaitiaki/<name>.yaml
    """
    name: str
    role: str
    kaitiaki_type: KaitiakiType = KaitiakiType.REALM
    glyph: str = "koru_blue"
    purpose: List[str] = field(default_factory=list)
    vector_store: str = ""
    tools: List[str] = field(default_factory=list)
    capabilities: List[TaskType] = field(default_factory=list)
    lineage: str = ""  # e.g., "whiro → awanui"
    realm_id: Optional[str] = None
    memory_table: str = ""  # Supabase table name
    
    def to_dict(self) -> dict:
        d = asdict(self)
        d["kaitiaki_type"] = self.kaitiaki_type.value
        d["capabilities"] = [c.value for c in self.capabilities]
        return d
    
    @classmethod
    def from_dict(cls, data: dict) -> "KaitiakiManifest":
        data["kaitiaki_type"] = KaitiakiType(data.get("kaitiaki_type", "realm"))
        data["capabilities"] = [TaskType(c) for c in data.get("capabilities", [])]
        return cls(**data)


@dataclass
class TaskRequest:
    """A task to be routed to a kaitiaki."""
    task_type: TaskType
    input_data: Any
    realm_id: str
    options: Dict[str, Any] = field(default_factory=dict)
    source_kaitiaki: Optional[str] = None
    trace_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class TaskResult:
    """Result from a kaitiaki task execution."""
    success: bool
    output: Any
    kaitiaki: str
    task_type: TaskType
    trace_id: Optional[str] = None
    duration_ms: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HandoffRequest:
    """Request to hand off a task between kaitiaki."""
    from_kaitiaki: str
    to_kaitiaki: str
    context: Dict[str, Any]
    reason: str = ""


# ═══════════════════════════════════════════════════════════════
# SHARED MEMORY BUS
# ═══════════════════════════════════════════════════════════════

class SharedMemoryBus:
    """
    Three-layer shared memory system for kaitiaki.
    
    Layer 1: Local Vector Memory (per kaitiaki)
    Layer 2: Whiro Global Memory (cross-realm)
    Layer 3: Supabase Relationship Memory (persistent)
    """
    
    def __init__(self, supabase_client=None):
        self._local_cache: Dict[str, Dict[str, Any]] = {}
        self._global_cache: Dict[str, Any] = {}
        self.supabase = supabase_client
    
    # Layer 1: Local Memory
    def store_local(self, kaitiaki: str, key: str, value: Any):
        """Store in kaitiaki's local memory."""
        if kaitiaki not in self._local_cache:
            self._local_cache[kaitiaki] = {}
        self._local_cache[kaitiaki][key] = value
    
    def get_local(self, kaitiaki: str, key: str) -> Optional[Any]:
        """Get from kaitiaki's local memory."""
        return self._local_cache.get(kaitiaki, {}).get(key)
    
    # Layer 2: Global Memory
    def store_global(self, key: str, value: Any):
        """Store in global (Whiro) memory."""
        self._global_cache[key] = value
    
    def get_global(self, key: str) -> Optional[Any]:
        """Get from global memory."""
        return self._global_cache.get(key)
    
    # Layer 3: Supabase Memory
    async def store_persistent(self, table: str, data: Dict[str, Any]) -> bool:
        """Store to Supabase."""
        if not self.supabase:
            return False
        try:
            self.supabase.table(table).insert(data).execute()
            return True
        except Exception:
            return False
    
    async def query_persistent(
        self, 
        table: str, 
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20
    ) -> List[Dict]:
        """Query from Supabase."""
        if not self.supabase:
            return []
        try:
            query = self.supabase.table(table).select("*")
            if filters:
                for k, v in filters.items():
                    query = query.eq(k, v)
            result = query.limit(limit).execute()
            return result.data
        except Exception:
            return []
    
    # Inter-Kaitiaki Communication
    async def send_message(
        self,
        sender: str,
        receiver: str,
        message_type: str,
        payload: Any
    ) -> bool:
        """Send message between kaitiaki via Supabase."""
        return await self.store_persistent("kaitiaki_messages", {
            "sender": sender,
            "receiver": receiver,
            "type": message_type,
            "payload": json.dumps(payload) if not isinstance(payload, str) else payload,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def get_messages(
        self,
        receiver: str,
        since: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get messages for a kaitiaki."""
        return await self.query_persistent(
            "kaitiaki_messages",
            {"receiver": receiver},
            limit
        )


# ═══════════════════════════════════════════════════════════════
# LINEAGE GRAPH
# ═══════════════════════════════════════════════════════════════

@dataclass
class LineageNode:
    """A node in the kaitiaki lineage graph."""
    name: str
    children: List[str] = field(default_factory=list)
    parent: Optional[str] = None


class LineageGraph:
    """
    Represents the ancestry of kaitiaki.
    
    Stored in: mauri/lineage/graph.yaml
    
    Purpose:
    - Enforcing mauri consistency
    - Determining which memories can be read
    - Maintaining sovereignty
    - Routing tasks through proper whakapapa
    """
    
    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        self.root: Optional[str] = None
    
    def add_kaitiaki(self, name: str, parent: Optional[str] = None):
        """Add a kaitiaki to the lineage."""
        node = LineageNode(name=name, parent=parent)
        self.nodes[name] = node
        
        if parent and parent in self.nodes:
            self.nodes[parent].children.append(name)
        elif parent is None:
            self.root = name
    
    def get_lineage(self, name: str) -> List[str]:
        """Get full lineage path from root to this kaitiaki."""
        path = []
        current = name
        
        while current:
            path.insert(0, current)
            node = self.nodes.get(current)
            current = node.parent if node else None
        
        return path
    
    def get_lineage_string(self, name: str) -> str:
        """Get lineage as 'parent → child' string."""
        return " → ".join(self.get_lineage(name))
    
    def can_access(self, requester: str, target: str) -> bool:
        """
        Check if requester can access target's memory.
        
        Rules:
        - Parent can access child
        - Cannot access siblings without going through parent
        - Root (Whiro) can access everything
        """
        if requester == self.root:
            return True
        
        # Get lineage paths
        req_lineage = self.get_lineage(requester)
        tgt_lineage = self.get_lineage(target)
        
        # Requester can access if target is a descendant
        if requester in tgt_lineage:
            return True
        
        # Or if they share a parent (sibling access via parent)
        req_parent = self.nodes.get(requester, LineageNode("")).parent
        tgt_parent = self.nodes.get(target, LineageNode("")).parent
        
        return req_parent == tgt_parent
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            name: {"children": node.children, "parent": node.parent}
            for name, node in self.nodes.items()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "LineageGraph":
        """Load from dictionary."""
        graph = cls()
        
        # First pass: create nodes
        for name, info in data.items():
            graph.nodes[name] = LineageNode(
                name=name,
                children=info.get("children", []),
                parent=info.get("parent")
            )
            if info.get("parent") is None:
                graph.root = name
        
        return graph


# ═══════════════════════════════════════════════════════════════
# KAITIAKI ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════

class KaitiakiOrchestrator:
    """
    Coordinates multiple kaitiaki minds.
    
    Responsibilities:
    - Task routing based on capabilities
    - Chain-of-thought handoffs
    - Context fusion
    - Memory bus management
    - Lineage enforcement
    """
    
    # Default task routing table
    DEFAULT_ROUTING = {
        TaskType.OCR: "ruru",
        TaskType.TRANSLATE: "awanui",
        TaskType.SUMMARISE: "mataroa",
        TaskType.RESEARCH: "te_puna",
        TaskType.CLASSIFY: "whiro",
        TaskType.EMBED: "whiro",
        TaskType.CHAT: None,  # Routes to realm kaitiaki
        TaskType.PIPELINE: "whiro"
    }
    
    def __init__(self):
        self.kaitiaki: Dict[str, KaitiakiManifest] = {}
        self.memory = SharedMemoryBus()
        self.lineage = LineageGraph()
        self.routing: Dict[TaskType, str] = dict(self.DEFAULT_ROUTING)
        self._handlers: Dict[str, Callable] = {}
    
    def register(self, manifest: KaitiakiManifest):
        """Register a kaitiaki with the orchestrator."""
        self.kaitiaki[manifest.name] = manifest
        
        # Add to lineage
        parent = manifest.lineage.split("→")[0].strip() if "→" in manifest.lineage else None
        self.lineage.add_kaitiaki(manifest.name, parent)
        
        # Update routing for capabilities
        for cap in manifest.capabilities:
            if cap not in self.routing or self.routing[cap] is None:
                self.routing[cap] = manifest.name
    
    def register_handler(self, kaitiaki: str, handler: Callable):
        """Register a task handler for a kaitiaki."""
        self._handlers[kaitiaki] = handler
    
    def route(self, task: TaskRequest) -> str:
        """
        Determine which kaitiaki should handle a task.
        
        Priority:
        1. Explicit routing table
        2. Realm's own kaitiaki for CHAT
        3. Capability-based matching
        4. Default to Whiro
        """
        # Check routing table
        if task.task_type in self.routing and self.routing[task.task_type]:
            return self.routing[task.task_type]
        
        # For chat, use realm's kaitiaki if exists
        if task.task_type == TaskType.CHAT:
            realm_kaitiaki = f"{task.realm_id}_kaitiaki"
            if realm_kaitiaki in self.kaitiaki:
                return realm_kaitiaki
        
        # Find by capability
        for name, manifest in self.kaitiaki.items():
            if task.task_type in manifest.capabilities:
                return name
        
        # Default to Whiro
        return "whiro"
    
    async def execute(self, task: TaskRequest) -> TaskResult:
        """Execute a task through the appropriate kaitiaki."""
        import time
        start = time.time()
        
        # Route to kaitiaki
        target = self.route(task)
        
        # Check handler exists
        if target not in self._handlers:
            return TaskResult(
                success=False,
                output={"error": f"No handler for kaitiaki: {target}"},
                kaitiaki=target,
                task_type=task.task_type,
                trace_id=task.trace_id
            )
        
        try:
            # Execute handler
            handler = self._handlers[target]
            output = await handler(task)
            
            duration = int((time.time() - start) * 1000)
            
            return TaskResult(
                success=True,
                output=output,
                kaitiaki=target,
                task_type=task.task_type,
                trace_id=task.trace_id,
                duration_ms=duration
            )
        
        except Exception as e:
            return TaskResult(
                success=False,
                output={"error": str(e)},
                kaitiaki=target,
                task_type=task.task_type,
                trace_id=task.trace_id
            )
    
    async def handoff(self, request: HandoffRequest) -> TaskResult:
        """
        Hand off a task from one kaitiaki to another.
        
        Example flow:
        1. Ruru OCRs a PDF
        2. Ruru hands off to Mataroa for summarisation
        3. Mataroa hands off to Whiro for embedding
        """
        # Check lineage allows this handoff
        if not self.lineage.can_access(request.from_kaitiaki, request.to_kaitiaki):
            return TaskResult(
                success=False,
                output={"error": "Lineage does not permit this handoff"},
                kaitiaki=request.from_kaitiaki,
                task_type=TaskType.PIPELINE
            )
        
        # Record handoff in memory bus
        await self.memory.send_message(
            sender=request.from_kaitiaki,
            receiver=request.to_kaitiaki,
            message_type="handoff",
            payload=request.context
        )
        
        # Create task for target
        task = TaskRequest(
            task_type=request.context.get("task_type", TaskType.PIPELINE),
            input_data=request.context.get("data"),
            realm_id=request.context.get("realm_id", "global"),
            source_kaitiaki=request.from_kaitiaki
        )
        
        return await self.execute(task)
    
    def fuse_context(
        self,
        realm_id: str,
        kaitiaki: str,
        include_global: bool = True,
        include_lineage: bool = False
    ) -> Dict[str, Any]:
        """
        Fuse context from multiple memory layers.
        
        Combines:
        - Realm memory
        - Kaitiaki local memory
        - Global (Whiro) memory
        - Lineage context
        """
        context = {
            "realm_id": realm_id,
            "kaitiaki": kaitiaki,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add local memory
        local = self.memory._local_cache.get(kaitiaki, {})
        context["local"] = local
        
        # Add global if requested
        if include_global:
            context["global"] = self.memory._global_cache
        
        # Add lineage if requested
        if include_lineage:
            context["lineage"] = self.lineage.get_lineage_string(kaitiaki)
            context["lineage_path"] = self.lineage.get_lineage(kaitiaki)
        
        # Add manifest info
        if kaitiaki in self.kaitiaki:
            manifest = self.kaitiaki[kaitiaki]
            context["purpose"] = manifest.purpose
            context["tools"] = manifest.tools
            context["glyph"] = manifest.glyph
        
        return context
    
    def list_kaitiaki(self) -> List[Dict]:
        """List all registered kaitiaki."""
        return [m.to_dict() for m in self.kaitiaki.values()]


# ═══════════════════════════════════════════════════════════════
# DEFAULT KAITIAKI CLUSTER
# ═══════════════════════════════════════════════════════════════

def create_default_cluster() -> KaitiakiOrchestrator:
    """
    Create the default AwaOS kaitiaki cluster.
    
    Includes:
    - Kitenga Whiro (root)
    - Awanui (translator)
    - Ruru (OCR)
    - Mataroa (research/summary)
    - Te Puna (knowledge portal)
    """
    orchestrator = KaitiakiOrchestrator()
    
    # Root: Kitenga Whiro
    orchestrator.register(KaitiakiManifest(
        name="whiro",
        role="Root Intelligence",
        kaitiaki_type=KaitiakiType.GLOBAL,
        glyph="koru_purple",
        purpose=[
            "Oversee all realms",
            "Route complex tasks",
            "Maintain global memory",
            "Coordinate kaitiaki cluster"
        ],
        capabilities=[TaskType.CLASSIFY, TaskType.EMBED, TaskType.PIPELINE],
        lineage="whiro"
    ))
    
    # Translator: Awanui
    orchestrator.register(KaitiakiManifest(
        name="awanui",
        role="Translator",
        kaitiaki_type=KaitiakiType.SPECIALIST,
        glyph="koru_blue",
        purpose=[
            "Translate reo Māori ↔ English",
            "Preserve dialect integrity",
            "Normalise UTF-8 macrons"
        ],
        tools=["translate_tool", "unicode_normaliser", "glossary_lookup"],
        capabilities=[TaskType.TRANSLATE],
        lineage="whiro → awanui",
        memory_table="awanui_memory"
    ))
    
    # OCR: Ruru
    orchestrator.register(KaitiakiManifest(
        name="ruru",
        role="OCR Specialist",
        kaitiaki_type=KaitiakiType.SPECIALIST,
        glyph="koru_green",
        purpose=[
            "Extract text from images",
            "Process PDF documents",
            "Handle handwritten text"
        ],
        tools=["ocr_tool", "pdf_extractor", "image_processor"],
        capabilities=[TaskType.OCR],
        lineage="whiro → ruru",
        memory_table="ruru_ocr_logs"
    ))
    
    # Research: Mataroa
    orchestrator.register(KaitiakiManifest(
        name="mataroa",
        role="Research & Summarisation",
        kaitiaki_type=KaitiakiType.SPECIALIST,
        glyph="koru_orange",
        purpose=[
            "Summarise documents",
            "Extract key information",
            "Build timelines"
        ],
        tools=["summarise_tool", "entity_extractor", "timeline_builder"],
        capabilities=[TaskType.SUMMARISE, TaskType.RESEARCH],
        lineage="whiro → mataroa",
        memory_table="mataroa_summaries"
    ))
    
    # Knowledge Portal: Te Puna
    orchestrator.register(KaitiakiManifest(
        name="te_puna",
        role="Knowledge Portal",
        kaitiaki_type=KaitiakiType.REALM,
        glyph="koru_teal",
        purpose=[
            "Search and retrieve knowledge",
            "Answer research queries",
            "Navigate archives"
        ],
        tools=["search_tool", "archive_navigator"],
        capabilities=[TaskType.RESEARCH, TaskType.CHAT],
        lineage="whiro → te_puna",
        memory_table="te_puna_knowledge"
    ))
    
    return orchestrator
