"""
Kaitiaki SDK Loader - Load kaitiaki definitions from YAML/JSON.
"""

import json
from pathlib import Path
from typing import Optional

import yaml

from .types import (
    KaitiakiSpec,
    KaitiakiMetadata,
    KaitiakiConfig,
    ToolDefinition,
    ConstraintConfig,
    TriggerDefinition,
    EvolutionConfig,
    PersonalityConfig,
    EvolutionStage,
)
from .compiler import KaitiakiCompiler


def load_kaitiaki_yaml(path: str | Path) -> KaitiakiSpec:
    """
    Load a kaitiaki definition from a YAML file.
    
    Args:
        path: Path to .kaitiaki.yaml file
        
    Returns:
        Compiled KaitiakiSpec
    """
    compiler = KaitiakiCompiler()
    return compiler.compile(path)


def load_kaitiaki_json(path: str | Path) -> KaitiakiSpec:
    """
    Load a kaitiaki definition from a JSON file.
    
    Args:
        path: Path to .json file
        
    Returns:
        KaitiakiSpec
    """
    path = Path(path)
    with open(path) as f:
        data = json.load(f)
    
    # Convert JSON to spec
    metadata = KaitiakiMetadata(
        name=data.get("metadata", {}).get("name", ""),
        realm=data.get("metadata", {}).get("realm", ""),
        description=data.get("metadata", {}).get("description", ""),
        labels=data.get("metadata", {}).get("labels", {}),
        version=data.get("metadata", {}).get("version", "1.0.0"),
    )
    
    spec_data = data.get("spec", {})
    
    # Parse stage
    stage_str = spec_data.get("stage", "seed")
    try:
        stage = EvolutionStage(stage_str)
    except ValueError:
        stage = EvolutionStage.SEED
    
    # Parse tools
    tools = []
    for tool_data in spec_data.get("tools", []):
        tools.append(ToolDefinition(
            name=tool_data.get("name", ""),
            type=tool_data.get("type", "builtin"),
            description=tool_data.get("description", ""),
            config=tool_data.get("config", {}),
            handler=tool_data.get("handler"),
            permissions=tool_data.get("permissions", []),
            schema=tool_data.get("schema", {}),
        ))
    
    # Parse personality
    personality_data = spec_data.get("personality", {})
    personality = PersonalityConfig(
        tone=personality_data.get("tone", "respectful, knowledgeable"),
        language=personality_data.get("language", "bilingual (en, mi)"),
        style=personality_data.get("style", "formal but warm"),
        traits=personality_data.get("traits", []),
    )
    
    # Parse constraints
    constraints_data = spec_data.get("constraints", {})
    constraints = ConstraintConfig(
        max_tokens=constraints_data.get("max_tokens", 4000),
        forbidden_topics=constraints_data.get("forbidden_topics", []),
        allowed_files=constraints_data.get("allowed_files", ["**/*.md", "**/*.json", "**/*.yaml"]),
        rate_limit=constraints_data.get("rate_limit"),
        tapu_max=constraints_data.get("tapu_max", 2),
    )
    
    # Parse triggers
    triggers = []
    for trigger_data in spec_data.get("triggers", []):
        triggers.append(TriggerDefinition(
            event=trigger_data.get("event", ""),
            pattern=trigger_data.get("pattern"),
            keywords=trigger_data.get("keywords", []),
            action=trigger_data.get("action", ""),
        ))
    
    # Parse evolution
    evolution_data = spec_data.get("evolution", {})
    evolution = EvolutionConfig(
        auto_promote=evolution_data.get("auto_promote", False),
        min_interactions=evolution_data.get("min_interactions", {}),
        approval_required=evolution_data.get("approval_required", True),
    )
    
    # Parse context rules
    context_rules = spec_data.get("context_rules", {})
    
    config = KaitiakiConfig(
        stage=stage,
        model=spec_data.get("model", "gpt-4o"),
        personality=personality,
        system_prompt=spec_data.get("system_prompt", ""),
        tools=tools,
        constraints=constraints,
        triggers=triggers,
        evolution=evolution,
        vector_namespace=spec_data.get("vector_namespace"),
        max_recent_messages=context_rules.get("max_recent_messages", 50),
        include_global=context_rules.get("include_global", False),
        include_lineage=context_rules.get("include_lineage", False),
    )
    
    return KaitiakiSpec(
        api_version=data.get("apiVersion", "awaos/v1"),
        kind=data.get("kind", "Kaitiaki"),
        metadata=metadata,
        spec=config,
    )


def find_kaitiaki_files(directory: str | Path) -> list[Path]:
    """
    Find all kaitiaki definition files in a directory.
    
    Looks for:
    - *.kaitiaki.yaml
    - *.kaitiaki.json
    - .kaitiaki/*.json
    
    Args:
        directory: Directory to search
        
    Returns:
        List of paths to kaitiaki files
    """
    directory = Path(directory)
    files = []
    
    # YAML files
    files.extend(directory.glob("**/*.kaitiaki.yaml"))
    files.extend(directory.glob("**/*.kaitiaki.yml"))
    
    # JSON files in .kaitiaki directory
    kaitiaki_dir = directory / ".kaitiaki"
    if kaitiaki_dir.exists():
        files.extend(kaitiaki_dir.glob("*.json"))
    
    return sorted(set(files))
