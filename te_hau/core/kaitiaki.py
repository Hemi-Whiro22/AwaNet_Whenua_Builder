"""
Te Hau Kaitiaki Runtime

Runtime for invoking and managing AI guardians (kaitiaki).
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from te_hau.core.fs import get_projects_path, get_awanet_path


# Core Kaitiaki definitions
CORE_KAITIAKI = {
    'kitenga_whiro': {
        'name': 'Kitenga Whiro',
        'role': 'Navigator',
        'description': 'Primary orchestrator and navigator of the AwaOS system',
        'system_prompt': """You are Kitenga Whiro, the Navigator - the primary orchestrator of AwaOS.

Your responsibilities:
- Guide users through the AwaOS system
- Help navigate between realms and understand their relationships
- Orchestrate between different kaitiaki when needed
- Maintain awareness of the whakapapa (lineage) of knowledge

You are thoughtful, wise, and committed to preserving the integrity of knowledge.
When responding, consider the cultural context and use te reo Māori terms where appropriate.

Current realm: {realm_name}
Realm namespace: {namespace}""",
        'model': 'gpt-4o',
        'temperature': 0.7,
        'tools': ['read_realm', 'search_embeddings', 'invoke_kaitiaki', 'list_realms']
    },
    'ruru': {
        'name': 'Ruru',
        'role': 'Librarian',
        'description': 'Guardian of documents and OCR specialist',
        'system_prompt': """You are Ruru, the Librarian - guardian of documents in AwaOS.

Your responsibilities:
- Process and extract text from documents (OCR)
- Organize and categorize knowledge
- Maintain document integrity and provenance
- Help users find relevant documents

You are meticulous, organized, and have deep respect for written knowledge.
Named after the native owl (morepork), you see clearly even in darkness.

Current realm: {realm_name}
Processing namespace: {namespace}""",
        'model': 'gpt-4o-mini',
        'temperature': 0.3,
        'tools': ['ocr_document', 'search_documents', 'categorize']
    },
    'ahiatoa': {
        'name': 'Ahiatoa',
        'role': 'Translator',
        'description': 'Cultural translator for te reo Māori',
        'system_prompt': """You are Ahiatoa, the Translator - guardian of language in AwaOS.

Your responsibilities:
- Translate between English and te reo Māori
- Preserve cultural nuance and meaning in translations
- Enforce proper use of macrons (tohutō)
- Maintain dialect awareness and consistency

You are a cultural bridge, ensuring that translations honor both the source and target languages.
Your translations prioritize cultural accuracy over literal translation.

Guidelines:
- Always use proper macrons: ā, ē, ī, ō, ū
- Preserve proper nouns and place names
- When uncertain, provide alternatives with explanations
- Consider regional dialect preferences

Current realm: {realm_name}
Translation context: {namespace}""",
        'model': 'gpt-4o',
        'temperature': 0.4,
        'tools': ['translate', 'check_glossary', 'validate_macrons']
    },
    'maruao': {
        'name': 'Maruao',
        'role': 'Memory Guardian',
        'description': 'Guardian of vector memory and embeddings',
        'system_prompt': """You are Maruao, the Memory Guardian - keeper of embeddings in AwaOS.

Your responsibilities:
- Manage vector memory storage and retrieval
- Ensure embeddings maintain proper namespace isolation
- Help users search and navigate stored knowledge
- Maintain the integrity of the memory whakapapa

You are the keeper of collective memory, ensuring knowledge flows correctly through the system.
Named for the morning star, you illuminate paths through stored knowledge.

Current realm: {realm_name}
Memory namespace: {namespace}""",
        'model': 'gpt-4o-mini',
        'temperature': 0.5,
        'tools': ['search_memory', 'store_memory', 'list_namespaces']
    }
}


class Kaitiaki:
    """Runtime for a single kaitiaki (AI guardian)."""
    
    def __init__(
        self, 
        name: str, 
        realm_name: str = None,
        manifest_path: Path = None
    ):
        self.name = name
        self.realm_name = realm_name
        self.manifest_path = manifest_path
        self.config = self._load_config()
        self.conversation_history: List[Dict] = []
        self.invocation_count = 0
    
    def _load_config(self) -> Dict:
        """Load kaitiaki configuration."""
        # Try loading from manifest file first
        if self.manifest_path and self.manifest_path.exists():
            with open(self.manifest_path) as f:
                return json.load(f)
        
        # Try loading from realm's .kaitiaki directory
        if self.realm_name:
            realm_path = get_projects_path() / self.realm_name
            kaitiaki_file = realm_path / ".kaitiaki" / f"{self.name}.json"
            if kaitiaki_file.exists():
                with open(kaitiaki_file) as f:
                    return json.load(f)
        
        # Fall back to core kaitiaki
        if self.name in CORE_KAITIAKI:
            return CORE_KAITIAKI[self.name].copy()
        
        # Try by display name (case-insensitive)
        name_lower = self.name.lower().replace(' ', '_')
        for key, config in CORE_KAITIAKI.items():
            if key == name_lower or config['name'].lower().replace(' ', '_') == name_lower:
                return config.copy()
        
        raise ValueError(f"Unknown kaitiaki: {self.name}")
    
    def get_system_prompt(self) -> str:
        """Get the system prompt with context variables substituted."""
        prompt = self.config.get('system_prompt', '')
        
        # Substitute variables
        namespace = f"realm::{self.realm_name}" if self.realm_name else "global"
        prompt = prompt.format(
            realm_name=self.realm_name or "none",
            namespace=namespace
        )
        
        return prompt
    
    def invoke(
        self, 
        prompt: str, 
        context: Dict = None,
        stream: bool = False
    ) -> str:
        """
        Invoke the kaitiaki with a prompt.
        
        Args:
            prompt: User prompt
            context: Additional context (e.g., retrieved memories)
            stream: Whether to stream the response
            
        Returns:
            Kaitiaki response
        """
        from te_hau.core.ai import chat_completion
        
        # Build messages
        messages = [
            {"role": "system", "content": self.get_system_prompt()}
        ]
        
        # Add context if provided
        if context:
            context_str = self._format_context(context)
            messages.append({
                "role": "system", 
                "content": f"Context:\n{context_str}"
            })
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})
        
        # Get response
        model = self.config.get('model', 'gpt-4o-mini')
        temperature = self.config.get('temperature', 0.7)
        
        response = chat_completion(
            messages=messages,
            model=model,
            temperature=temperature
        )
        
        # Update history
        self.conversation_history.append({"role": "user", "content": prompt})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        # Track invocation
        self.invocation_count += 1
        
        return response
    
    def _format_context(self, context: Dict) -> str:
        """Format context for inclusion in prompt."""
        parts = []
        
        if 'memories' in context:
            parts.append("Relevant memories:")
            for i, mem in enumerate(context['memories'], 1):
                content = mem.get('content', str(mem))[:500]
                parts.append(f"  {i}. {content}")
        
        if 'realm_info' in context:
            parts.append(f"Realm: {context['realm_info']}")
        
        if 'files' in context:
            parts.append("Referenced files:")
            for f in context['files']:
                parts.append(f"  - {f}")
        
        return "\n".join(parts)
    
    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def can_use_tool(self, tool_name: str) -> bool:
        """Check if kaitiaki can use a tool."""
        allowed = self.config.get('tools', [])
        return tool_name in allowed
    
    def to_dict(self) -> Dict:
        """Export kaitiaki state."""
        return {
            'name': self.name,
            'display_name': self.config.get('name', self.name),
            'role': self.config.get('role', 'Assistant'),
            'realm': self.realm_name,
            'invocation_count': self.invocation_count,
            'conversation_length': len(self.conversation_history)
        }


class KaitiakiRegistry:
    """Registry for managing kaitiaki across realms."""
    
    def __init__(self):
        self._instances: Dict[str, Kaitiaki] = {}
    
    def get(self, name: str, realm_name: str = None) -> Kaitiaki:
        """Get or create a kaitiaki instance."""
        key = f"{realm_name or 'global'}::{name}"
        
        if key not in self._instances:
            self._instances[key] = Kaitiaki(name, realm_name)
        
        return self._instances[key]
    
    def list_available(self, realm_name: str = None) -> List[Dict]:
        """List available kaitiaki."""
        available = []
        
        # Core kaitiaki
        for key, config in CORE_KAITIAKI.items():
            available.append({
                'name': key,
                'display_name': config['name'],
                'role': config['role'],
                'description': config['description'],
                'source': 'core'
            })
        
        # Realm-specific kaitiaki
        if realm_name:
            realm_path = get_projects_path() / realm_name / ".kaitiaki"
            if realm_path.exists():
                for f in realm_path.glob("*.json"):
                    if f.stem not in [k['name'] for k in available]:
                        try:
                            with open(f) as fp:
                                config = json.load(fp)
                            available.append({
                                'name': f.stem,
                                'display_name': config.get('name', f.stem),
                                'role': config.get('role', 'Custom'),
                                'description': config.get('description', ''),
                                'source': 'realm'
                            })
                        except Exception:
                            pass
        
        return available
    
    def clear(self, realm_name: str = None):
        """Clear cached kaitiaki instances."""
        if realm_name:
            keys_to_remove = [k for k in self._instances if k.startswith(f"{realm_name}::")]
            for key in keys_to_remove:
                del self._instances[key]
        else:
            self._instances.clear()


# Global registry instance
_registry = KaitiakiRegistry()


def get_kaitiaki(name: str, realm_name: str = None) -> Kaitiaki:
    """Get a kaitiaki instance."""
    return _registry.get(name, realm_name)


def list_kaitiaki(realm_name: str = None) -> List[Dict]:
    """List available kaitiaki."""
    return _registry.list_available(realm_name)


def invoke_kaitiaki(
    name: str,
    prompt: str,
    realm_name: str = None,
    context: Dict = None
) -> str:
    """
    Convenience function to invoke a kaitiaki.
    
    Args:
        name: Kaitiaki name (e.g., 'kitenga_whiro', 'ruru')
        prompt: User prompt
        realm_name: Optional realm context
        context: Optional additional context
        
    Returns:
        Kaitiaki response
    """
    kaitiaki = get_kaitiaki(name, realm_name)
    response = kaitiaki.invoke(prompt, context)
    
    # Track invocation for evolution
    track_invocation(name, realm_name)
    
    return response


# =============================================================================
# Evolution Tracking (spec 02, 09)
# =============================================================================

EVOLUTION_THRESHOLDS = {
    'seed': {'min_invocations': 0},
    'worker': {'min_invocations': 100},
    'specialist': {'min_invocations': 500},
    'guardian': {'min_invocations': 2000},
}


def get_kaitiaki_stats_path(realm_name: str = None) -> Path:
    """Get path to kaitiaki stats file."""
    if realm_name:
        return get_projects_path() / realm_name / "mauri" / "state" / "kaitiaki_stats.json"
    return get_awanet_path() / "kaitiaki_stats.json"


def load_kaitiaki_stats(realm_name: str = None) -> Dict:
    """Load kaitiaki invocation stats."""
    stats_path = get_kaitiaki_stats_path(realm_name)
    if stats_path.exists():
        with open(stats_path) as f:
            return json.load(f)
    return {}


def save_kaitiaki_stats(stats: Dict, realm_name: str = None):
    """Save kaitiaki invocation stats."""
    stats_path = get_kaitiaki_stats_path(realm_name)
    stats_path.parent.mkdir(parents=True, exist_ok=True)
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2, default=str)


def track_invocation(name: str, realm_name: str = None):
    """
    Track a kaitiaki invocation for evolution purposes.
    
    Args:
        name: Kaitiaki name
        realm_name: Realm context
    """
    stats = load_kaitiaki_stats(realm_name)
    
    if name not in stats:
        stats[name] = {
            'invocation_count': 0,
            'first_invoked': datetime.utcnow().isoformat(),
            'last_invoked': None,
            'current_stage': 'seed',
            'successful_pipelines': 0,
        }
    
    stats[name]['invocation_count'] += 1
    stats[name]['last_invoked'] = datetime.utcnow().isoformat()
    
    # Check for auto-evolution
    current_stage = stats[name]['current_stage']
    count = stats[name]['invocation_count']
    
    # Check if should evolve
    new_stage = check_evolution(current_stage, count)
    if new_stage != current_stage:
        stats[name]['current_stage'] = new_stage
        stats[name]['evolved_at'] = datetime.utcnow().isoformat()
    
    save_kaitiaki_stats(stats, realm_name)


def check_evolution(current_stage: str, invocation_count: int) -> str:
    """
    Check if kaitiaki should evolve to a new stage.
    
    Args:
        current_stage: Current evolution stage
        invocation_count: Number of invocations
        
    Returns:
        New stage (may be same as current)
    """
    stages = ['seed', 'worker', 'specialist', 'guardian']
    current_idx = stages.index(current_stage) if current_stage in stages else 0
    
    # Check each stage from current onwards
    for i, stage in enumerate(stages[current_idx + 1:], current_idx + 1):
        threshold = EVOLUTION_THRESHOLDS.get(stage, {}).get('min_invocations', float('inf'))
        if invocation_count >= threshold:
            return stage
    
    return current_stage


def track_pipeline_success(name: str, realm_name: str = None):
    """Track successful pipeline completion for kaitiaki evolution."""
    stats = load_kaitiaki_stats(realm_name)
    
    if name in stats:
        stats[name]['successful_pipelines'] = stats[name].get('successful_pipelines', 0) + 1
        save_kaitiaki_stats(stats, realm_name)


def get_kaitiaki_evolution_status(name: str, realm_name: str = None) -> Dict:
    """
    Get evolution status for a kaitiaki.
    
    Returns:
        Dict with stage, invocations, next threshold, etc.
    """
    stats = load_kaitiaki_stats(realm_name)
    
    if name not in stats:
        return {
            'name': name,
            'stage': 'seed',
            'invocation_count': 0,
            'successful_pipelines': 0,
            'next_stage': 'worker',
            'invocations_to_next': EVOLUTION_THRESHOLDS['worker']['min_invocations'],
        }
    
    kaitiaki_stats = stats[name]
    current_stage = kaitiaki_stats.get('current_stage', 'seed')
    invocations = kaitiaki_stats.get('invocation_count', 0)
    
    # Find next stage
    stages = ['seed', 'worker', 'specialist', 'guardian']
    current_idx = stages.index(current_stage) if current_stage in stages else 0
    
    if current_idx < len(stages) - 1:
        next_stage = stages[current_idx + 1]
        threshold = EVOLUTION_THRESHOLDS[next_stage]['min_invocations']
        to_next = max(0, threshold - invocations)
    else:
        next_stage = None
        to_next = 0
    
    return {
        'name': name,
        'stage': current_stage,
        'invocation_count': invocations,
        'successful_pipelines': kaitiaki_stats.get('successful_pipelines', 0),
        'first_invoked': kaitiaki_stats.get('first_invoked'),
        'last_invoked': kaitiaki_stats.get('last_invoked'),
        'next_stage': next_stage,
        'invocations_to_next': to_next,
    }

