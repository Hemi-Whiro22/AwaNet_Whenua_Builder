"""
Kaitiaki SDK Type Definitions.

Based on spec 15: Kaitiaki SDK (Compiler)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
from datetime import datetime


class EvolutionStage(str, Enum):
    """Evolution stages for kaitiaki (spec 02, 09)."""
    PEPI = "pēpi"           # Infant - newly created
    TAMARIKI = "tamariki"   # Child - basic operations
    RANGATAHI = "rangatahi" # Youth - growing capabilities
    PAKEKE = "pakeke"       # Adult - full capabilities
    KAUMATUA = "kaumātua"   # Elder - mentor capabilities
    
    # Legacy aliases
    SEED = "seed"
    WORKER = "worker"
    SPECIALIST = "specialist"
    GUARDIAN = "guardian"


@dataclass
class ToolDefinition:
    """Definition of a tool available to the kaitiaki."""
    name: str
    type: str  # 'builtin', 'llm', 'custom', 'mcp'
    description: str = ""
    config: dict = field(default_factory=dict)
    handler: Optional[str] = None  # Path to custom handler
    permissions: list[str] = field(default_factory=list)
    schema: dict = field(default_factory=dict)  # Input schema


@dataclass
class ConstraintConfig:
    """Constraints on kaitiaki behavior."""
    max_tokens: int = 4000
    forbidden_topics: list[str] = field(default_factory=list)
    allowed_files: list[str] = field(default_factory=lambda: ["**/*.md", "**/*.json", "**/*.yaml"])
    rate_limit: Optional[int] = None  # Requests per minute
    tapu_max: int = 2  # Maximum tapu level accessible


@dataclass
class TriggerDefinition:
    """Event trigger for automatic kaitiaki actions."""
    event: str  # 'file_changed', 'question_asked', 'pipeline_complete'
    pattern: Optional[str] = None
    keywords: list[str] = field(default_factory=list)
    action: str = ""


@dataclass
class EvolutionConfig:
    """Configuration for kaitiaki evolution."""
    auto_promote: bool = False
    min_interactions: dict[str, int] = field(default_factory=lambda: {
        "tamariki": 100,
        "rangatahi": 500,
        "pakeke": 2000
    })
    tools_required: dict[str, list[str]] = field(default_factory=dict)
    approval_required: bool = True


@dataclass
class PersonalityConfig:
    """Personality traits for the kaitiaki."""
    tone: str = "respectful, knowledgeable"
    language: str = "bilingual (en, mi)"
    style: str = "formal but warm"
    traits: list[str] = field(default_factory=list)


@dataclass 
class KaitiakiMetadata:
    """Metadata about the kaitiaki."""
    name: str
    realm: str
    description: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    version: str = "1.0.0"
    created_at: Optional[datetime] = None


@dataclass
class KaitiakiConfig:
    """Core configuration for a kaitiaki."""
    stage: EvolutionStage = EvolutionStage.SEED
    model: str = "gpt-4o"
    personality: PersonalityConfig = field(default_factory=PersonalityConfig)
    system_prompt: str = ""
    tools: list[ToolDefinition] = field(default_factory=list)
    constraints: ConstraintConfig = field(default_factory=ConstraintConfig)
    triggers: list[TriggerDefinition] = field(default_factory=list)
    evolution: EvolutionConfig = field(default_factory=EvolutionConfig)
    
    # Memory configuration
    vector_namespace: Optional[str] = None
    supabase_tables: list[str] = field(default_factory=list)
    local_embeddings: bool = False
    
    # Context rules
    max_recent_messages: int = 50
    include_global: bool = False
    include_lineage: bool = False


@dataclass
class KaitiakiSpec:
    """
    Complete kaitiaki specification.
    
    Matches the YAML schema from spec 15:
    
    ```yaml
    apiVersion: awaos/v1
    kind: Kaitiaki
    metadata: ...
    spec: ...
    ```
    """
    api_version: str = "awaos/v1"
    kind: str = "Kaitiaki"
    metadata: KaitiakiMetadata = field(default_factory=lambda: KaitiakiMetadata(name="", realm=""))
    spec: KaitiakiConfig = field(default_factory=KaitiakiConfig)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "apiVersion": self.api_version,
            "kind": self.kind,
            "metadata": {
                "name": self.metadata.name,
                "realm": self.metadata.realm,
                "description": self.metadata.description,
                "labels": self.metadata.labels,
                "version": self.metadata.version,
            },
            "spec": {
                "stage": self.spec.stage.value if isinstance(self.spec.stage, EvolutionStage) else self.spec.stage,
                "model": self.spec.model,
                "personality": {
                    "tone": self.spec.personality.tone,
                    "language": self.spec.personality.language,
                    "style": self.spec.personality.style,
                    "traits": self.spec.personality.traits,
                },
                "system_prompt": self.spec.system_prompt,
                "tools": [
                    {
                        "name": t.name,
                        "type": t.type,
                        "description": t.description,
                        "config": t.config,
                        "handler": t.handler,
                        "permissions": t.permissions,
                    }
                    for t in self.spec.tools
                ],
                "constraints": {
                    "max_tokens": self.spec.constraints.max_tokens,
                    "forbidden_topics": self.spec.constraints.forbidden_topics,
                    "allowed_files": self.spec.constraints.allowed_files,
                    "rate_limit": self.spec.constraints.rate_limit,
                    "tapu_max": self.spec.constraints.tapu_max,
                },
                "triggers": [
                    {
                        "event": t.event,
                        "pattern": t.pattern,
                        "keywords": t.keywords,
                        "action": t.action,
                    }
                    for t in self.spec.triggers
                ],
                "evolution": {
                    "auto_promote": self.spec.evolution.auto_promote,
                    "min_interactions": self.spec.evolution.min_interactions,
                    "approval_required": self.spec.evolution.approval_required,
                },
                "vector_namespace": self.spec.vector_namespace,
                "context_rules": {
                    "max_recent_messages": self.spec.max_recent_messages,
                    "include_global": self.spec.include_global,
                    "include_lineage": self.spec.include_lineage,
                },
            },
        }


# Builtin tools available to all kaitiaki
BUILTIN_TOOLS = {
    "search_memory": ToolDefinition(
        name="search_memory",
        type="builtin",
        description="Search vector memory",
        schema={
            "query": {"type": "string", "required": True},
            "top_k": {"type": "number", "default": 5},
        },
    ),
    "read_file": ToolDefinition(
        name="read_file",
        type="builtin",
        description="Read file contents",
        schema={
            "path": {"type": "string", "required": True},
        },
    ),
    "summarize": ToolDefinition(
        name="summarize",
        type="llm",
        description="Summarize content",
        schema={
            "content": {"type": "string", "required": True},
            "max_length": {"type": "number", "default": 500},
        },
    ),
    "translate": ToolDefinition(
        name="translate",
        type="builtin",
        description="Translate to te reo Māori",
        schema={
            "text": {"type": "string", "required": True},
            "direction": {"enum": ["en_to_mi", "mi_to_en"]},
        },
    ),
    "embed": ToolDefinition(
        name="embed",
        type="builtin",
        description="Embed and store content",
        schema={
            "content": {"type": "string", "required": True},
            "metadata": {"type": "object"},
        },
    ),
    "ocr": ToolDefinition(
        name="ocr",
        type="builtin",
        description="Extract text from images",
        schema={
            "image_path": {"type": "string", "required": True},
        },
    ),
}
