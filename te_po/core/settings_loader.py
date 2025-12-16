"""
Kitenga Whiro Settings Loader

Reads the manifest + config, resolves secrets from:
1. Environment variables (highest priority)
2. mauri/encrypted_keys/*.json files (fallback)

Does not print secrets.
"""

import json
import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class OpenAISettings:
    """OpenAI-related settings."""
    api_key: str = ""
    model: str = "gpt-4o-mini"
    embed_model: str = "text-embedding-3-small"
    assistant_id: str = ""
    vector_store_id: str = ""
    thread_id: str = ""


@dataclass
class SupabaseSettings:
    """Supabase-related settings."""
    url: str = ""
    service_role_key: str = ""
    project: str = ""
    bucket: str = ""
    tables: List[str] = field(default_factory=list)


@dataclass
class SecuritySettings:
    """Security/auth-related settings."""
    pipeline_token: str = ""
    gateway_bearer: str = ""
    cors_allow_origins: List[str] = field(default_factory=list)


@dataclass
class CloudflareSettings:
    """Cloudflare tunnel settings."""
    tunnel_name: str = ""
    public_base_url: str = ""
    tunnel_token: str = ""


@dataclass
class HTTPSettings:
    """HTTP server settings."""
    host: str = "0.0.0.0"
    port: int = 8000
    public_base_url: str = "http://localhost:8000"


@dataclass
class FeatureFlags:
    """Feature flags."""
    taonga_mode: bool = False
    offline: bool = False


@dataclass
class LimitSettings:
    """Limit settings."""
    max_upload_mb: int = 25
    request_timeout_seconds: int = 60


@dataclass
class KitengaWhiroSettings:
    """Complete Kitenga Whiro settings."""
    name: str = "kitenga_whiro"
    role: str = "oracle_kaitiaki"
    purpose: str = ""
    korowai: str = "te_po"
    cloak_status: str = "sealed"
    
    openai: OpenAISettings = field(default_factory=OpenAISettings)
    supabase: SupabaseSettings = field(default_factory=SupabaseSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    cloudflare: CloudflareSettings = field(default_factory=CloudflareSettings)
    http: HTTPSettings = field(default_factory=HTTPSettings)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    limits: LimitSettings = field(default_factory=LimitSettings)
    
    tools: List[str] = field(default_factory=list)
    api_paths: dict = field(default_factory=dict)
    mauri_seal: str = ""
    glyph: str = "🐺"


def _resolve_env(env_key: str, default: str = "") -> str:
    """Resolve an environment variable, returning default if not set."""
    return os.getenv(env_key, default)


def _resolve_env_bool(env_key: str, default: bool = False) -> bool:
    """Resolve an environment variable as a boolean."""
    val = os.getenv(env_key, "").lower()
    if val in ("true", "1", "yes"):
        return True
    if val in ("false", "0", "no"):
        return False
    return default


def _resolve_env_int(env_key: str, default: int = 0) -> int:
    """Resolve an environment variable as an integer."""
    val = os.getenv(env_key, "")
    try:
        return int(val) if val else default
    except ValueError:
        return default


def _resolve_env_list(env_key: str, fallback: Optional[List[str]] = None) -> List[str]:
    """Resolve an environment variable as a comma-separated list."""
    val = os.getenv(env_key, "")
    if val:
        return [item.strip() for item in val.split(",") if item.strip()]
    return fallback or []


def _find_project_root() -> Path:
    """Find the project root by looking for mauri folder."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "mauri").is_dir():
            return parent
    return Path.cwd()


def load_manifest(manifest_path: Optional[Path] = None) -> dict:
    """Load the Kitenga Whiro manifest JSON."""
    if manifest_path is None:
        root = _find_project_root()
        manifest_path = root / "mauri" / "te_kete" / "kitenga_whiro.manifest.json"
    
    if not manifest_path.exists():
        return {}
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_config(config_path: Optional[Path] = None) -> dict:
    """Load the Kitenga Whiro runtime config JSON."""
    if config_path is None:
        root = _find_project_root()
        config_path = root / "mauri" / "services" / "kitenga_whiro.config.json"
    
    if not config_path.exists():
        return {}
    
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_settings(
    manifest_path: Optional[Path] = None,
    config_path: Optional[Path] = None
) -> KitengaWhiroSettings:
    """
    Load manifest + config, resolve secrets from env vars.
    Returns a KitengaWhiroSettings dataclass.
    
    Does NOT print secrets.
    """
    manifest = load_manifest(manifest_path)
    config = load_config(config_path)
    
    # OpenAI settings
    openai_cfg = manifest.get("openai", {})
    openai = OpenAISettings(
        api_key=_resolve_env("OPENAI_API_KEY"),
        model=_resolve_env(openai_cfg.get("model_env", "OPENAI_MODEL"), "gpt-4o-mini"),
        embed_model=_resolve_env(openai_cfg.get("embed_model_env", "OPENAI_EMBED_MODEL"), "text-embedding-3-small"),
        assistant_id=_resolve_env(openai_cfg.get("assistant_id_env", "KITENGA_ASSISTANT_ID")),
        vector_store_id=_resolve_env(openai_cfg.get("vector_store_id_env", "KITENGA_VECTOR_STORE_ID")),
        thread_id=_resolve_env(openai_cfg.get("thread_id_env", "KITENGA_THREAD_ID")),
    )
    
    # Supabase settings
    supa_cfg = manifest.get("supabase", {})
    supabase = SupabaseSettings(
        url=_resolve_env(supa_cfg.get("url_env", "SUPABASE_URL")),
        service_role_key=_resolve_env("SUPABASE_SERVICE_ROLE_KEY"),
        project=supa_cfg.get("project", ""),
        bucket=supa_cfg.get("bucket", ""),
        tables=supa_cfg.get("tables", []),
    )
    
    # Security settings
    sec_cfg = manifest.get("security", {})
    cors_cfg = config.get("cors", {})
    security = SecuritySettings(
        pipeline_token=_resolve_env(sec_cfg.get("bearer_env", "PIPELINE_TOKEN")),
        gateway_bearer=_resolve_env(sec_cfg.get("gateway_bearer_env", "KITENGA_GATEWAY_BEARER")),
        cors_allow_origins=_resolve_env_list(
            sec_cfg.get("cors_allow_origins_env", "CORS_ALLOW_ORIGINS"),
            cors_cfg.get("fallback", [])
        ),
    )
    
    # Cloudflare settings
    cf_cfg = manifest.get("cloudflare", {})
    cloudflare = CloudflareSettings(
        tunnel_name=cf_cfg.get("tunnel_name", ""),
        public_base_url=_resolve_env(cf_cfg.get("public_base_url_env", "PUBLIC_BASE_URL")),
        tunnel_token=_resolve_env(cf_cfg.get("tunnel_token_env", "CLOUDFLARE_TUNNEL_TOKEN")),
    )
    
    # HTTP settings
    http_cfg = config.get("http", {})
    http = HTTPSettings(
        host=_resolve_env(http_cfg.get("host_env", "HOST"), "0.0.0.0"),
        port=_resolve_env_int(http_cfg.get("port_env", "PORT"), 8000),
        public_base_url=_resolve_env(http_cfg.get("public_base_url_env", "PUBLIC_BASE_URL"), "http://localhost:8000"),
    )
    
    # Feature flags
    feat_cfg = config.get("features", {})
    features = FeatureFlags(
        taonga_mode=_resolve_env_bool(feat_cfg.get("taonga_mode_env", "TAONGA_MODE")),
        offline=_resolve_env_bool(feat_cfg.get("offline_env", "OFFLINE")),
    )
    
    # Limits
    lim_cfg = config.get("limits", {})
    limits = LimitSettings(
        max_upload_mb=_resolve_env_int(lim_cfg.get("max_upload_mb_env", "MAX_UPLOAD_MB"), 25),
        request_timeout_seconds=_resolve_env_int(lim_cfg.get("request_timeout_seconds_env", "REQUEST_TIMEOUT_SECONDS"), 60),
    )
    
    # Trace info
    trace = manifest.get("trace", {})
    
    return KitengaWhiroSettings(
        name=manifest.get("name", "kitenga_whiro"),
        role=manifest.get("role", "oracle_kaitiaki"),
        purpose=manifest.get("purpose", ""),
        korowai=manifest.get("korowai", "te_po"),
        cloak_status=manifest.get("cloak_status", "sealed"),
        openai=openai,
        supabase=supabase,
        security=security,
        cloudflare=cloudflare,
        http=http,
        features=features,
        limits=limits,
        tools=manifest.get("tools", []),
        api_paths=manifest.get("api", {}),
        mauri_seal=trace.get("mauri_seal", ""),
        glyph=trace.get("glyph", "🐺"),
    )


# Singleton cached settings
_cached_settings: Optional[KitengaWhiroSettings] = None


def get_cached_settings(force_reload: bool = False) -> KitengaWhiroSettings:
    """
    Get cached settings (singleton pattern).
    Use force_reload=True to refresh from disk/env.
    """
    global _cached_settings
    if _cached_settings is None or force_reload:
        _cached_settings = get_settings()
    return _cached_settings


if __name__ == "__main__":
    # Quick test - does not print secrets
    settings = get_settings()
    print(f"Service: {settings.name}")
    print(f"Role: {settings.role}")
    print(f"Glyph: {settings.glyph}")
    print(f"Tools: {len(settings.tools)} registered")
    print(f"Supabase Project: {settings.supabase.project}")
    print(f"API Paths: {settings.api_paths}")
    print(f"Features: taonga_mode={settings.features.taonga_mode}, offline={settings.features.offline}")
