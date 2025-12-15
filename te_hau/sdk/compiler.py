"""
Kaitiaki SDK Compiler - Parse, validate, and generate kaitiaki configs.

Based on spec 15: Kaitiaki SDK (Compiler)

Compiler Pipeline:
    Source YAML
        │
        ▼
    ┌─────────────┐
    │   Parser    │ ─── Parse YAML, resolve imports
    └─────────────┘
        │
        ▼
    ┌─────────────┐
    │  Validator  │ ─── Check schema, validate refs
    └─────────────┘
        │
        ▼
    ┌─────────────┐
    │ Transformer │ ─── Apply defaults, expand macros
    └─────────────┘
        │
        ▼
    ┌─────────────┐
    │  Generator  │ ─── Output JSON configs
    └─────────────┘
        │
        ▼
    Output JSON
"""

import json
import logging
from pathlib import Path
from typing import Optional, Any
from datetime import datetime

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
    BUILTIN_TOOLS,
)

logger = logging.getLogger(__name__)


class CompilerError(Exception):
    """Error during kaitiaki compilation."""
    pass


class ValidationError(CompilerError):
    """Validation error in kaitiaki spec."""
    pass


class KaitiakiCompiler:
    """
    Compiler for kaitiaki YAML definitions.
    
    Usage:
        compiler = KaitiakiCompiler()
        spec = compiler.compile("my-kaitiaki.kaitiaki.yaml")
        compiler.generate(spec, output_dir=".kaitiaki/")
    """
    
    def __init__(self):
        self.errors: list[str] = []
        self.warnings: list[str] = []
    
    def compile(self, source_path: str | Path) -> KaitiakiSpec:
        """
        Compile a kaitiaki YAML file to a KaitiakiSpec.
        
        Args:
            source_path: Path to .kaitiaki.yaml file
            
        Returns:
            Compiled KaitiakiSpec
            
        Raises:
            CompilerError: If compilation fails
        """
        self.errors = []
        self.warnings = []
        
        source_path = Path(source_path)
        
        # Step 1: Parse
        raw_data = self._parse(source_path)
        
        # Step 2: Validate
        self._validate(raw_data)
        
        if self.errors:
            raise ValidationError(f"Validation failed: {'; '.join(self.errors)}")
        
        # Step 3: Transform
        spec = self._transform(raw_data)
        
        # Step 4: Return spec (generation is separate)
        return spec
    
    def _parse(self, source_path: Path) -> dict:
        """Parse YAML source file."""
        if not source_path.exists():
            raise CompilerError(f"Source file not found: {source_path}")
        
        try:
            with open(source_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise CompilerError(f"YAML parse error: {e}")
        
        if not isinstance(data, dict):
            raise CompilerError("Invalid YAML: root must be a mapping")
        
        # Resolve imports if any
        data = self._resolve_imports(data, source_path.parent)
        
        return data
    
    def _resolve_imports(self, data: dict, base_path: Path) -> dict:
        """Resolve any $import directives."""
        # Support importing tool definitions from external files
        if "spec" in data and "tools" in data["spec"]:
            tools = data["spec"]["tools"]
            resolved_tools = []
            
            for tool in tools:
                if isinstance(tool, dict) and "$import" in tool:
                    import_path = base_path / tool["$import"]
                    if import_path.exists():
                        with open(import_path) as f:
                            imported = yaml.safe_load(f)
                            if isinstance(imported, list):
                                resolved_tools.extend(imported)
                            else:
                                resolved_tools.append(imported)
                    else:
                        self.warnings.append(f"Import not found: {import_path}")
                else:
                    resolved_tools.append(tool)
            
            data["spec"]["tools"] = resolved_tools
        
        return data
    
    def _validate(self, data: dict) -> None:
        """Validate the parsed data against schema."""
        # Check required fields
        if data.get("apiVersion") != "awaos/v1":
            self.errors.append(f"Invalid apiVersion: expected 'awaos/v1'")
        
        if data.get("kind") != "Kaitiaki":
            self.errors.append(f"Invalid kind: expected 'Kaitiaki'")
        
        # Validate metadata
        metadata = data.get("metadata", {})
        if not metadata.get("name"):
            self.errors.append("metadata.name is required")
        if not metadata.get("realm"):
            self.errors.append("metadata.realm is required")
        
        # Validate spec
        spec = data.get("spec", {})
        if not spec:
            self.errors.append("spec is required")
            return
        
        # Validate stage
        stage = spec.get("stage", "seed")
        valid_stages = [s.value for s in EvolutionStage]
        if stage not in valid_stages:
            self.warnings.append(f"Unknown stage '{stage}', using 'seed'")
        
        # Validate tools
        tools = spec.get("tools", [])
        for i, tool in enumerate(tools):
            if not isinstance(tool, dict):
                self.errors.append(f"tools[{i}]: must be a mapping")
                continue
            if not tool.get("name"):
                self.errors.append(f"tools[{i}]: name is required")
            if not tool.get("type"):
                self.errors.append(f"tools[{i}]: type is required")
    
    def _transform(self, data: dict) -> KaitiakiSpec:
        """Transform raw data into KaitiakiSpec with defaults."""
        metadata_raw = data.get("metadata", {})
        spec_raw = data.get("spec", {})
        
        # Build metadata
        metadata = KaitiakiMetadata(
            name=metadata_raw.get("name", ""),
            realm=metadata_raw.get("realm", ""),
            description=metadata_raw.get("description", ""),
            labels=metadata_raw.get("labels", {}),
            version=metadata_raw.get("version", "1.0.0"),
            created_at=datetime.utcnow(),
        )
        
        # Build personality
        personality_raw = spec_raw.get("personality", {})
        personality = PersonalityConfig(
            tone=personality_raw.get("tone", "respectful, knowledgeable"),
            language=personality_raw.get("language", "bilingual (en, mi)"),
            style=personality_raw.get("style", "formal but warm"),
            traits=personality_raw.get("traits", []),
        )
        
        # Build tools
        tools = []
        for tool_raw in spec_raw.get("tools", []):
            tool = ToolDefinition(
                name=tool_raw.get("name", ""),
                type=tool_raw.get("type", "builtin"),
                description=tool_raw.get("description", ""),
                config=tool_raw.get("config", {}),
                handler=tool_raw.get("handler"),
                permissions=tool_raw.get("permissions", []),
                schema=tool_raw.get("schema", {}),
            )
            # Merge with builtin if applicable
            if tool.type == "builtin" and tool.name in BUILTIN_TOOLS:
                builtin = BUILTIN_TOOLS[tool.name]
                if not tool.description:
                    tool.description = builtin.description
                if not tool.schema:
                    tool.schema = builtin.schema
            tools.append(tool)
        
        # Build constraints
        constraints_raw = spec_raw.get("constraints", {})
        constraints = ConstraintConfig(
            max_tokens=constraints_raw.get("max_tokens", 4000),
            forbidden_topics=constraints_raw.get("forbidden_topics", []),
            allowed_files=constraints_raw.get("allowed_files", ["**/*.md", "**/*.json", "**/*.yaml"]),
            rate_limit=constraints_raw.get("rate_limit"),
            tapu_max=constraints_raw.get("tapu_max", 2),
        )
        
        # Build triggers
        triggers = []
        for trigger_raw in spec_raw.get("triggers", []):
            triggers.append(TriggerDefinition(
                event=trigger_raw.get("event", ""),
                pattern=trigger_raw.get("pattern"),
                keywords=trigger_raw.get("keywords", []),
                action=trigger_raw.get("action", ""),
            ))
        
        # Build evolution
        evolution_raw = spec_raw.get("evolution", {})
        evolution = EvolutionConfig(
            auto_promote=evolution_raw.get("auto_promote", False),
            min_interactions=evolution_raw.get("requirements", {}).get("min_interactions", 
                                              evolution_raw.get("min_interactions", {})),
            approval_required=evolution_raw.get("approval_required", True),
        )
        
        # Parse stage
        stage_str = spec_raw.get("stage", "seed")
        try:
            stage = EvolutionStage(stage_str)
        except ValueError:
            stage = EvolutionStage.SEED
        
        # Build config
        context_rules = spec_raw.get("context_rules", {})
        config = KaitiakiConfig(
            stage=stage,
            model=spec_raw.get("model", "gpt-4o"),
            personality=personality,
            system_prompt=spec_raw.get("system_prompt", ""),
            tools=tools,
            constraints=constraints,
            triggers=triggers,
            evolution=evolution,
            vector_namespace=spec_raw.get("vector_namespace"),
            max_recent_messages=context_rules.get("max_recent_messages", 50),
            include_global=context_rules.get("include_global", False),
            include_lineage=context_rules.get("include_lineage", False),
        )
        
        # Expand macros in system prompt
        config.system_prompt = self._expand_macros(
            config.system_prompt,
            realm=metadata.realm,
            name=metadata.name,
        )
        
        return KaitiakiSpec(
            api_version=data.get("apiVersion", "awaos/v1"),
            kind=data.get("kind", "Kaitiaki"),
            metadata=metadata,
            spec=config,
        )
    
    def _expand_macros(self, text: str, **kwargs) -> str:
        """Expand {{macro}} placeholders in text."""
        for key, value in kwargs.items():
            text = text.replace(f"{{{{{key}}}}}", str(value))
            text = text.replace(f"{{{{realm_name}}}}", kwargs.get("realm", ""))
        return text
    
    def generate(
        self, 
        spec: KaitiakiSpec, 
        output_dir: str | Path,
        overwrite: bool = False
    ) -> dict[str, Path]:
        """
        Generate output JSON files from compiled spec.
        
        Args:
            spec: Compiled KaitiakiSpec
            output_dir: Directory to write output files
            overwrite: Whether to overwrite existing files
            
        Returns:
            Dict mapping output type to file path
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        name = spec.metadata.name
        outputs = {}
        
        # Main config
        config_path = output_dir / f"{name}.json"
        if config_path.exists() and not overwrite:
            logger.warning(f"Skipping {config_path} (exists)")
        else:
            with open(config_path, "w") as f:
                json.dump(spec.to_dict(), f, indent=2, default=str)
            outputs["config"] = config_path
        
        # Tools config
        tools_path = output_dir / f"{name}.tools.json"
        tools_data = [
            {
                "name": t.name,
                "type": t.type,
                "description": t.description,
                "schema": t.schema,
                "config": t.config,
            }
            for t in spec.spec.tools
        ]
        with open(tools_path, "w") as f:
            json.dump(tools_data, f, indent=2)
        outputs["tools"] = tools_path
        
        # Prompts config
        prompts_path = output_dir / f"{name}.prompts.json"
        prompts_data = {
            "system": spec.spec.system_prompt,
            "personality": {
                "tone": spec.spec.personality.tone,
                "language": spec.spec.personality.language,
                "style": spec.spec.personality.style,
            },
        }
        with open(prompts_path, "w") as f:
            json.dump(prompts_data, f, indent=2)
        outputs["prompts"] = prompts_path
        
        logger.info(f"Generated {len(outputs)} files in {output_dir}")
        return outputs
    
    def validate_file(self, source_path: str | Path) -> tuple[bool, list[str], list[str]]:
        """
        Validate a kaitiaki YAML file without compiling.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self.errors = []
        self.warnings = []
        
        try:
            data = self._parse(Path(source_path))
            self._validate(data)
        except CompilerError as e:
            self.errors.append(str(e))
        
        return len(self.errors) == 0, self.errors, self.warnings
