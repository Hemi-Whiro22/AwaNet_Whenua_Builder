# Te Hau Core Module
"""Core functionality for Te Hau CLI."""

from te_hau.core.fs import (
    ensure_directory,
    ensure_empty_directory,
    copy_tree,
    write_json,
    read_json,
    write_env,
    read_env,
    get_awaos_root,
    get_template_path,
    get_projects_path,
    get_user_config_path,
    get_awanet_path,
    list_realms,
    realm_exists,
)

from te_hau.core.secrets import (
    generate_bearer_token,
    generate_realm_id,
)

from te_hau.core.renderer import (
    render_template_string,
    render_template_file,
    render_directory,
)

# AI Client - lazy import to avoid requiring deps when not used
def get_ai_client():
    """Get or create AI client instance."""
    from te_hau.core.ai import AIClient
    return AIClient()

# Supabase Client - lazy import
def get_supabase_client():
    """Get or create Supabase client instance."""
    from te_hau.core.supabase import SupabaseClient
    return SupabaseClient()

# Pipeline Executor - lazy import
def get_pipeline_executor(realm_name: str, verbose: bool = False):
    """Get pipeline executor for a realm."""
    from te_hau.core.pipeline import PipelineExecutor
    return PipelineExecutor(realm_name, verbose=verbose)

# Orchestrator - lazy import
def get_orchestrator():
    """Get kaitiaki orchestrator instance."""
    from te_hau.core.orchestrator import KaitiakiOrchestrator, create_default_cluster
    return create_default_cluster()

# Awa Protocol - lazy import
def get_awa_router():
    """Get Awa Protocol router."""
    from te_hau.core.protocol import AwaRouter, create_awa_router_with_defaults
    return create_awa_router_with_defaults()

def get_awa_client(kaitiaki: str = "whiro", realm: str = "global"):
    """Get Awa Protocol client."""
    from te_hau.core.protocol import AwaClient
    return AwaClient(kaitiaki=kaitiaki, realm=realm)

# Self-Healing - lazy import
def get_healing_engine(realm_path: str):
    """Get self-healing engine for a realm."""
    from pathlib import Path
    from te_hau.core.healing import SelfHealingEngine
    return SelfHealingEngine(Path(realm_path))

# Infrastructure Provisioner - lazy import
def get_infra_provisioner(realm_path: str):
    """Get infrastructure provisioner for a realm."""
    from pathlib import Path
    from te_hau.core.infra import InfraProvisioner
    return InfraProvisioner(Path(realm_path))

__all__ = [
    # Filesystem
    'ensure_directory',
    'ensure_empty_directory',
    'copy_tree',
    'write_json',
    'read_json',
    'write_env',
    'read_env',
    'get_awaos_root',
    'get_template_path',
    'get_projects_path',
    'get_user_config_path',
    'get_awanet_path',
    'list_realms',
    'realm_exists',
    # Secrets
    'generate_bearer_token',
    'generate_realm_id',
    # Renderer
    'render_template_string',
    'render_template_file',
    'render_directory',
    # AI
    'get_ai_client',
    # Supabase
    'get_supabase_client',
    # Pipeline
    'get_pipeline_executor',
    # Orchestrator
    'get_orchestrator',
    # Awa Protocol
    'get_awa_router',
    'get_awa_client',
    # Self-Healing
    'get_healing_engine',
    # Infrastructure
    'get_infra_provisioner',
]