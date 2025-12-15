"""
Te Hau Context Manager

Resolves configuration from realm local, parent, and global contexts.
Implements sovereign data flow with proper precedence.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from functools import lru_cache

from te_hau.core.fs import get_projects_path, get_awanet_path


class ContextManager:
    """
    Manages context resolution across realm hierarchy.
    
    Context precedence (highest to lowest):
    1. Realm local config
    2. Parent realm config (if exists)
    3. Global config
    4. Defaults
    """
    
    def __init__(self, realm_name: str = None):
        self.realm_name = realm_name
        self.realm_path = get_projects_path() / realm_name if realm_name else None
        self._cache = {}
    
    def resolve(self, key: str, default: Any = None) -> Any:
        """
        Resolve a configuration key through the context hierarchy.
        
        Args:
            key: Dot-notation key (e.g., 'kaitiaki.model', 'pipeline.embed.chunk_size')
            default: Default value if not found
            
        Returns:
            Resolved value
        """
        # Try realm local first
        if self.realm_name:
            value = self._get_realm_config(key)
            if value is not None:
                return value
            
            # Try parent realm
            parent = self._get_parent_realm()
            if parent:
                parent_ctx = ContextManager(parent)
                value = parent_ctx.resolve(key)
                if value is not None:
                    return value
        
        # Try global config
        value = self._get_global_config(key)
        if value is not None:
            return value
        
        return default
    
    def resolve_merged(self, key: str, merge_type: str = 'additive') -> Any:
        """
        Resolve and merge config from all context layers.
        
        Args:
            key: Configuration key
            merge_type: 'additive' (lists concatenate) or 'consultative' (dicts merge)
            
        Returns:
            Merged value
        """
        values = []
        
        # Collect from all layers
        if self.realm_name:
            realm_val = self._get_realm_config(key)
            if realm_val is not None:
                values.append(realm_val)
            
            # Parent chain
            parent = self._get_parent_realm()
            while parent:
                parent_ctx = ContextManager(parent)
                parent_val = parent_ctx._get_realm_config(key)
                if parent_val is not None:
                    values.append(parent_val)
                parent = parent_ctx._get_parent_realm()
        
        global_val = self._get_global_config(key)
        if global_val is not None:
            values.append(global_val)
        
        if not values:
            return None
        
        # Merge based on type
        if merge_type == 'additive':
            return self._merge_additive(values)
        elif merge_type == 'consultative':
            return self._merge_consultative(values)
        else:
            return values[0]  # Just return highest priority
    
    def _merge_additive(self, values: List[Any]) -> Any:
        """Merge lists by concatenation (deduped)."""
        if not values:
            return None
        
        if isinstance(values[0], list):
            result = []
            seen = set()
            for val_list in values:
                if isinstance(val_list, list):
                    for item in val_list:
                        key = str(item)
                        if key not in seen:
                            seen.add(key)
                            result.append(item)
            return result
        
        return values[0]
    
    def _merge_consultative(self, values: List[Any]) -> Any:
        """Merge dicts with lower priority values filling gaps."""
        if not values:
            return None
        
        if isinstance(values[0], dict):
            result = {}
            # Start from lowest priority, override with higher
            for val_dict in reversed(values):
                if isinstance(val_dict, dict):
                    result.update(val_dict)
            return result
        
        return values[0]
    
    def _get_realm_config(self, key: str) -> Any:
        """Get config from realm's config directory."""
        if not self.realm_path or not self.realm_path.exists():
            return None
        
        config_dir = self.realm_path / "config"
        
        # Try loading from config files
        parts = key.split('.')
        
        # First part might be a config file name
        config_file = config_dir / f"{parts[0]}.json"
        if config_file.exists():
            try:
                data = json.loads(config_file.read_text(encoding='utf-8'))
                return self._deep_get(data, parts[1:]) if len(parts) > 1 else data
            except Exception:
                pass
        
        # Try main config.json
        main_config = config_dir / "config.json"
        if main_config.exists():
            try:
                data = json.loads(main_config.read_text(encoding='utf-8'))
                return self._deep_get(data, parts)
            except Exception:
                pass
        
        # Try realm_lock.json for identity info
        realm_lock = self.realm_path / "mauri" / "realm_lock.json"
        if realm_lock.exists():
            try:
                data = json.loads(realm_lock.read_text(encoding='utf-8'))
                return self._deep_get(data, parts)
            except Exception:
                pass
        
        return None
    
    def _get_global_config(self, key: str) -> Any:
        """Get config from global AwaNet config."""
        config_path = get_awanet_path() / "config" / "global.json"
        
        if not config_path.exists():
            return None
        
        try:
            data = json.loads(config_path.read_text(encoding='utf-8'))
            parts = key.split('.')
            return self._deep_get(data, parts)
        except Exception:
            return None
    
    def _get_parent_realm(self) -> Optional[str]:
        """Get parent realm name from realm_lock."""
        if not self.realm_path:
            return None
        
        realm_lock = self.realm_path / "mauri" / "realm_lock.json"
        if not realm_lock.exists():
            return None
        
        try:
            data = json.loads(realm_lock.read_text(encoding='utf-8'))
            return data.get('parent_realm')
        except Exception:
            return None
    
    def _deep_get(self, data: Dict, keys: List[str]) -> Any:
        """Get nested dictionary value."""
        for key in keys:
            if isinstance(data, dict) and key in data:
                data = data[key]
            else:
                return None
        return data
    
    def get_full_context(self) -> Dict:
        """
        Get complete context for export (e.g., to OpenAI system prompt).
        
        Returns:
            Dict with realm info, config, and namespace
        """
        context = {
            'realm_name': self.realm_name,
            'namespace': f"realm::{self.realm_name}" if self.realm_name else "global",
            'config': {},
            'parent': self._get_parent_realm(),
            'lineage': self._get_lineage()
        }
        
        # Add realm-specific info
        if self.realm_path and self.realm_path.exists():
            realm_lock = self.realm_path / "mauri" / "realm_lock.json"
            if realm_lock.exists():
                try:
                    data = json.loads(realm_lock.read_text(encoding='utf-8'))
                    context['realm_id'] = data.get('realm_id')
                    context['created_at'] = data.get('created_at')
                    context['sealed'] = 'seal_hash' in data
                except Exception:
                    pass
        
        return context
    
    def _get_lineage(self) -> List[str]:
        """Get full parent chain (whakapapa)."""
        lineage = []
        
        if self.realm_name:
            lineage.append(self.realm_name)
        
        parent = self._get_parent_realm()
        visited = {self.realm_name}  # Prevent cycles
        
        while parent and parent not in visited:
            lineage.append(parent)
            visited.add(parent)
            parent_ctx = ContextManager(parent)
            parent = parent_ctx._get_parent_realm()
        
        return lineage
    
    def export_for_ai(self) -> str:
        """
        Export context as formatted string for AI system prompts.
        
        Returns:
            Formatted context string
        """
        ctx = self.get_full_context()
        
        lines = [
            f"Realm: {ctx['realm_name'] or 'None'}",
            f"Namespace: {ctx['namespace']}",
        ]
        
        if ctx.get('realm_id'):
            lines.append(f"Realm ID: {ctx['realm_id']}")
        
        if ctx.get('sealed'):
            lines.append("Status: Sealed (verified)")
        
        if ctx.get('lineage') and len(ctx['lineage']) > 1:
            lines.append(f"Lineage: {' → '.join(ctx['lineage'])}")
        
        return "\n".join(lines)


def resolve_context(realm_name: str, key: str, default: Any = None) -> Any:
    """
    Convenience function to resolve a config key.
    
    Args:
        realm_name: Realm name
        key: Config key (dot notation)
        default: Default value
        
    Returns:
        Resolved value
    """
    ctx = ContextManager(realm_name)
    return ctx.resolve(key, default)


def get_realm_context(realm_name: str) -> Dict:
    """
    Get full context for a realm.
    
    Args:
        realm_name: Realm name
        
    Returns:
        Context dictionary
    """
    ctx = ContextManager(realm_name)
    return ctx.get_full_context()


def export_context_for_ai(realm_name: str) -> str:
    """
    Export realm context formatted for AI prompts.
    
    Args:
        realm_name: Realm name
        
    Returns:
        Formatted context string
    """
    ctx = ContextManager(realm_name)
    return ctx.export_for_ai()
