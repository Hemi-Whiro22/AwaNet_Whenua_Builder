from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from pydantic import BaseModel, Field, ValidationError


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REALM_ROOT = PROJECT_ROOT / "mauri" / "realms"
MANIFEST_FILENAME = "manifest.json"


class RealmConfigError(RuntimeError):
    """Raised when a realm configuration cannot be loaded or parsed."""


class RealmNotFoundError(RealmConfigError):
    """Raised when a realm manifest cannot be found."""


class OpenAIConfig(BaseModel):
    assistant_id: Optional[str] = None
    vector_store_id: Optional[str] = None
    model: Optional[str] = None
    instructions: Optional[str] = None


class SupabaseConfig(BaseModel):
    project_url: Optional[str] = None
    anon_key: Optional[str] = None
    service_role_key: Optional[str] = None
    schema: Optional[str] = None


class FeatureFlags(BaseModel):
    vector_search: bool = False
    pipeline: bool = False
    recall: bool = False
    memory: bool = False
    kaitiaki: bool = False


class RecallConfig(BaseModel):
    vector_store: Optional[str] = None
    top_k: int = Field(default=5, ge=1)
    use_supabase_pgvector: bool = True


class RealmConfig(BaseModel):
    realm_id: str = Field(alias="realm_id")
    display_name: Optional[str] = None
    description: Optional[str] = None
    te_po_url: Optional[str] = None
    auth_mode: str = Field(default="bearer")
    openai: Optional[OpenAIConfig] = None
    supabase: Optional[SupabaseConfig] = None
    features: FeatureFlags = Field(default_factory=FeatureFlags)
    recall_config: Optional[RecallConfig] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    version: Optional[str] = None
    created_at: Optional[str] = None

    class Config:
        populate_by_name = True
        allow_population_by_field_name = True

    @property
    def supports_recall(self) -> bool:
        return bool(self.features and getattr(self.features, "recall", False))

    @property
    def vector_store_strategy(self) -> str:
        if self.recall_config and self.recall_config.vector_store:
            return self.recall_config.vector_store
        return "supabase"


class RealmConfigLoader:
    """
    Loads and caches realm manifests from disk with optional environment overrides.

    Precedence for locating manifests:
      1. REALM_CONFIG_PATH_<REALM_ID> (explicit per-realm override)
      2. REALM_CONFIG_PATH (can contain {realm} placeholder or point to a directory/file)
      3. Default path: <repo>/mauri/realms/{realm}/manifest.json
    """

    _cache: Dict[str, RealmConfig] = {}

    @classmethod
    def clear_cache(cls) -> None:
        cls._cache.clear()

    @classmethod
    def get(cls, realm_id: str) -> RealmConfig:
        realm_key = realm_id.strip().lower()
        if not realm_key:
            raise RealmConfigError("Realm identifier is required.")

        if realm_key in cls._cache:
            return cls._cache[realm_key]

        manifest_path = cls._resolve_manifest_path(realm_key)
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise RealmNotFoundError(f"Realm manifest not found for '{realm_key}' at {manifest_path}") from exc
        except json.JSONDecodeError as exc:
            raise RealmConfigError(f"Invalid JSON in realm manifest '{manifest_path}': {exc}") from exc

        try:
            model = RealmConfig.model_validate(payload)
        except ValidationError as exc:
            raise RealmConfigError(f"Realm manifest validation failed for '{realm_key}': {exc}") from exc

        cls._cache[realm_key] = model
        return model

    @classmethod
    def list_cached_realms(cls) -> List[str]:
        return list(cls._cache.keys())

    @classmethod
    def _resolve_manifest_path(cls, realm_id: str) -> Path:
        for candidate in cls._manifest_candidates(realm_id):
            if candidate.exists():
                return candidate
        # Build helpful error message with checked paths
        searched = ", ".join(str(path) for path in cls._manifest_candidates(realm_id))
        raise RealmNotFoundError(f"No manifest found for realm '{realm_id}'. Checked: {searched}")

    @classmethod
    def _manifest_candidates(cls, realm_id: str) -> Iterable[Path]:
        paths: List[Path] = []

        env_key = f"REALM_CONFIG_PATH_{realm_id.upper()}"
        per_realm = os.getenv(env_key)
        if per_realm:
            paths.append(cls._normalise_env_path(per_realm, realm_id))

        global_override = os.getenv("REALM_CONFIG_PATH")
        if global_override:
            paths.append(cls._normalise_env_path(global_override, realm_id))

        default_path = DEFAULT_REALM_ROOT / realm_id / MANIFEST_FILENAME
        paths.append(default_path)

        return paths

    @staticmethod
    def _normalise_env_path(value: str, realm_id: str) -> Path:
        """
        Support flexible env overrides:
        - Absolute or relative paths to a manifest file.
        - Directory paths (manifest.json appended).
        - Strings containing {realm} placeholder.
        """
        formatted = value.format(realm=realm_id, realm_id=realm_id)
        path = Path(formatted)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        if path.is_dir():
            path = path / MANIFEST_FILENAME
        return path.resolve()


__all__ = [
    "FeatureFlags",
    "OpenAIConfig",
    "RecallConfig",
    "RealmConfig",
    "RealmConfigError",
    "RealmConfigLoader",
    "RealmNotFoundError",
    "SupabaseConfig",
]
