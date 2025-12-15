"""
Infrastructure Manifest System (Drop 10)
========================================
Auto-generates infrastructure from infra.yaml specification.

Features:
- Single source of truth for realm infrastructure
- Auto-generate database schemas
- Auto-generate GitHub repos
- Auto-generate Cloudflare deployments
- Auto-generate Render services

From the Awa Protocol spec:
"Instead of manually managing config... you define infra.yaml
and the system does the rest."
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
import hashlib


# ═══════════════════════════════════════════════════════════════
# MANIFEST TYPES
# ═══════════════════════════════════════════════════════════════

class ServiceType(str, Enum):
    """Types of services in infrastructure."""
    SUPABASE = "supabase"
    GITHUB = "github"
    CLOUDFLARE = "cloudflare"
    RENDER = "render"
    VECTOR = "vector"
    MCP = "mcp"


class ResourceType(str, Enum):
    """Types of resources that can be provisioned."""
    DATABASE_TABLE = "database_table"
    STORAGE_BUCKET = "storage_bucket"
    EDGE_FUNCTION = "edge_function"
    GITHUB_REPO = "github_repo"
    PAGES_PROJECT = "pages_project"
    RENDER_SERVICE = "render_service"
    VECTOR_INDEX = "vector_index"
    ENV_SECRET = "env_secret"


@dataclass
class ResourceSpec:
    """Specification for a single resource."""
    name: str
    type: ResourceType
    service: ServiceType
    config: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)


@dataclass
class InfraManifest:
    """
    Complete infrastructure manifest for a realm.
    
    Location: mauri/infra.yaml
    """
    realm_id: str
    version: str = "1.0"
    description: str = ""
    resources: List[ResourceSpec] = field(default_factory=list)
    environment: Dict[str, str] = field(default_factory=dict)
    secrets: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    
    # Deployment targets
    frontend_url: str = ""
    backend_url: str = ""
    api_url: str = ""
    
    def to_dict(self) -> dict:
        return {
            "realm_id": self.realm_id,
            "version": self.version,
            "description": self.description,
            "resources": [
                {
                    "name": r.name,
                    "type": r.type.value,
                    "service": r.service.value,
                    "config": r.config,
                    "depends_on": r.depends_on
                }
                for r in self.resources
            ],
            "environment": self.environment,
            "secrets": self.secrets,
            "dependencies": self.dependencies,
            "frontend_url": self.frontend_url,
            "backend_url": self.backend_url,
            "api_url": self.api_url
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "InfraManifest":
        resources = [
            ResourceSpec(
                name=r["name"],
                type=ResourceType(r["type"]),
                service=ServiceType(r["service"]),
                config=r.get("config", {}),
                depends_on=r.get("depends_on", [])
            )
            for r in data.get("resources", [])
        ]
        
        return cls(
            realm_id=data["realm_id"],
            version=data.get("version", "1.0"),
            description=data.get("description", ""),
            resources=resources,
            environment=data.get("environment", {}),
            secrets=data.get("secrets", []),
            dependencies=data.get("dependencies", {}),
            frontend_url=data.get("frontend_url", ""),
            backend_url=data.get("backend_url", ""),
            api_url=data.get("api_url", "")
        )


@dataclass
class ProvisionResult:
    """Result of provisioning a resource."""
    resource_name: str
    resource_type: ResourceType
    success: bool
    message: str
    outputs: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ═══════════════════════════════════════════════════════════════
# RESOURCE GENERATORS
# ═══════════════════════════════════════════════════════════════

class SupabaseGenerator:
    """Generate Supabase resources from manifest."""
    
    def __init__(self, supabase_url: str = "", supabase_key: str = ""):
        self.url = supabase_url or os.getenv("SUPABASE_URL", "")
        self.key = supabase_key or os.getenv("SUPABASE_KEY", "")
    
    def generate_table_sql(self, spec: ResourceSpec) -> str:
        """Generate SQL for creating a table."""
        config = spec.config
        table_name = spec.name
        
        columns = config.get("columns", [])
        primary_key = config.get("primary_key", "id")
        enable_rls = config.get("enable_rls", True)
        
        sql_lines = [f"CREATE TABLE IF NOT EXISTS {table_name} ("]
        
        for col in columns:
            col_name = col["name"]
            col_type = col.get("type", "TEXT")
            nullable = "" if col.get("nullable", True) else " NOT NULL"
            default = f" DEFAULT {col['default']}" if "default" in col else ""
            sql_lines.append(f"    {col_name} {col_type}{nullable}{default},")
        
        # Add timestamps
        if config.get("timestamps", True):
            sql_lines.append("    created_at TIMESTAMP DEFAULT NOW(),")
            sql_lines.append("    updated_at TIMESTAMP DEFAULT NOW(),")
        
        sql_lines.append(f"    PRIMARY KEY ({primary_key})")
        sql_lines.append(");")
        
        # RLS
        if enable_rls:
            sql_lines.append(f"\nALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")
        
        return "\n".join(sql_lines)
    
    def generate_bucket_sql(self, spec: ResourceSpec) -> str:
        """Generate SQL for creating a storage bucket."""
        bucket_name = spec.name
        is_public = spec.config.get("public", False)
        
        return f"""
INSERT INTO storage.buckets (id, name, public)
VALUES ('{bucket_name}', '{bucket_name}', {str(is_public).lower()})
ON CONFLICT (id) DO NOTHING;
"""
    
    def generate_function_sql(self, spec: ResourceSpec) -> str:
        """Generate SQL for an RPC function."""
        func_name = spec.name
        params = spec.config.get("params", [])
        returns = spec.config.get("returns", "JSONB")
        body = spec.config.get("body", "BEGIN RETURN '{}'; END;")
        
        param_str = ", ".join([
            f"{p['name']} {p.get('type', 'TEXT')}"
            for p in params
        ])
        
        return f"""
CREATE OR REPLACE FUNCTION {func_name}({param_str})
RETURNS {returns}
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
{body}
$$;
"""


class GitHubGenerator:
    """Generate GitHub resources from manifest."""
    
    def __init__(self, token: str = ""):
        self.token = token or os.getenv("GITHUB_TOKEN", "")
    
    def generate_repo_config(self, spec: ResourceSpec) -> Dict:
        """Generate GitHub repo creation config."""
        config = spec.config
        
        return {
            "name": spec.name,
            "description": config.get("description", ""),
            "private": config.get("private", True),
            "auto_init": config.get("auto_init", True),
            "default_branch": config.get("default_branch", "main"),
            "has_issues": config.get("has_issues", True),
            "has_projects": config.get("has_projects", False),
            "has_wiki": config.get("has_wiki", False),
            "topics": config.get("topics", [])
        }
    
    def generate_workflow_yaml(self, spec: ResourceSpec) -> str:
        """Generate GitHub Actions workflow YAML."""
        config = spec.config
        workflow_type = config.get("workflow_type", "deploy")
        
        if workflow_type == "deploy":
            return self._deploy_workflow(spec.name, config)
        elif workflow_type == "test":
            return self._test_workflow(spec.name, config)
        else:
            return self._basic_workflow(spec.name, config)
    
    def _deploy_workflow(self, name: str, config: dict) -> str:
        target = config.get("deploy_target", "cloudflare")
        
        return f"""name: Deploy {name}

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Build
        run: npm run build
        
      - name: Deploy to {target.title()}
        env:
          DEPLOY_TOKEN: ${{{{ secrets.DEPLOY_TOKEN }}}}
        run: npm run deploy
"""
    
    def _test_workflow(self, name: str, config: dict) -> str:
        return f"""name: Test {name}

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          
      - name: Install
        run: npm ci
        
      - name: Test
        run: npm test
"""
    
    def _basic_workflow(self, name: str, config: dict) -> str:
        return f"""name: {name}

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Workflow triggered"
"""


class CloudflareGenerator:
    """Generate Cloudflare resources from manifest."""
    
    def __init__(self, account_id: str = "", api_token: str = ""):
        self.account_id = account_id or os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
        self.api_token = api_token or os.getenv("CLOUDFLARE_API_TOKEN", "")
    
    def generate_wrangler_toml(self, spec: ResourceSpec) -> str:
        """Generate wrangler.toml for Cloudflare Pages."""
        config = spec.config
        
        return f"""name = "{spec.name}"
compatibility_date = "{datetime.now().strftime('%Y-%m-%d')}"

[site]
bucket = "{config.get('build_output', './dist')}"

[env.production]
name = "{spec.name}-prod"

[env.preview]
name = "{spec.name}-preview"
"""
    
    def generate_pages_config(self, spec: ResourceSpec) -> Dict:
        """Generate Cloudflare Pages project config."""
        config = spec.config
        
        return {
            "name": spec.name,
            "production_branch": config.get("production_branch", "main"),
            "build_config": {
                "build_command": config.get("build_command", "npm run build"),
                "destination_dir": config.get("build_output", "dist"),
                "root_dir": config.get("root_dir", "/")
            }
        }


class RenderGenerator:
    """Generate Render resources from manifest."""
    
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.getenv("RENDER_API_KEY", "")
    
    def generate_render_yaml(self, spec: ResourceSpec) -> str:
        """Generate render.yaml service definition."""
        config = spec.config
        service_type = config.get("service_type", "web")
        
        return f"""services:
  - type: {service_type}
    name: {spec.name}
    env: python
    region: oregon
    plan: {config.get('plan', 'starter')}
    buildCommand: {config.get('build_command', 'pip install -r requirements.txt')}
    startCommand: {config.get('start_command', 'python main.py')}
    envVars:
      - key: PYTHON_VERSION
        value: "3.11"
"""
    
    def generate_service_config(self, spec: ResourceSpec) -> Dict:
        """Generate Render service creation config."""
        config = spec.config
        
        return {
            "type": config.get("service_type", "web_service"),
            "name": spec.name,
            "runtime": config.get("runtime", "python"),
            "plan": config.get("plan", "starter"),
            "region": config.get("region", "oregon"),
            "repo": config.get("repo", ""),
            "branch": config.get("branch", "main"),
            "build_command": config.get("build_command", "pip install -r requirements.txt"),
            "start_command": config.get("start_command", "python main.py"),
            "env_vars": config.get("env_vars", {})
        }


# ═══════════════════════════════════════════════════════════════
# INFRA PROVISIONER
# ═══════════════════════════════════════════════════════════════

class InfraProvisioner:
    """
    Provisions infrastructure from manifest.
    
    Orchestrates:
    - Resource dependency resolution
    - Generator invocation
    - File output
    - API calls (when connected)
    """
    
    def __init__(self, realm_path: Path):
        self.realm_path = realm_path
        self.generated_path = realm_path / ".generated"
        
        # Initialize generators
        self.supabase = SupabaseGenerator()
        self.github = GitHubGenerator()
        self.cloudflare = CloudflareGenerator()
        self.render = RenderGenerator()
    
    def load_manifest(self) -> Optional[InfraManifest]:
        """Load infra.yaml from realm."""
        import yaml
        
        manifest_path = self.realm_path / "mauri" / "infra.yaml"
        if not manifest_path.exists():
            return None
        
        with open(manifest_path, "r") as f:
            data = yaml.safe_load(f)
        
        return InfraManifest.from_dict(data)
    
    def resolve_dependencies(self, resources: List[ResourceSpec]) -> List[ResourceSpec]:
        """Order resources by dependencies."""
        resolved = []
        pending = list(resources)
        resolved_names = set()
        
        while pending:
            for resource in list(pending):
                deps_met = all(
                    dep in resolved_names 
                    for dep in resource.depends_on
                )
                
                if deps_met:
                    resolved.append(resource)
                    resolved_names.add(resource.name)
                    pending.remove(resource)
        
        return resolved
    
    def provision(self, manifest: InfraManifest, dry_run: bool = True) -> List[ProvisionResult]:
        """
        Provision all resources from manifest.
        
        Args:
            manifest: The infrastructure manifest
            dry_run: If True, only generate files without making API calls
        
        Returns:
            List of provision results
        """
        results = []
        
        # Ensure generated directory exists
        self.generated_path.mkdir(parents=True, exist_ok=True)
        
        # Resolve dependencies
        ordered_resources = self.resolve_dependencies(manifest.resources)
        
        for resource in ordered_resources:
            result = self._provision_resource(resource, dry_run)
            results.append(result)
        
        # Generate combined outputs
        self._generate_combined_outputs(manifest, results)
        
        return results
    
    def _provision_resource(self, spec: ResourceSpec, dry_run: bool) -> ProvisionResult:
        """Provision a single resource."""
        try:
            if spec.service == ServiceType.SUPABASE:
                return self._provision_supabase(spec, dry_run)
            elif spec.service == ServiceType.GITHUB:
                return self._provision_github(spec, dry_run)
            elif spec.service == ServiceType.CLOUDFLARE:
                return self._provision_cloudflare(spec, dry_run)
            elif spec.service == ServiceType.RENDER:
                return self._provision_render(spec, dry_run)
            else:
                return ProvisionResult(
                    resource_name=spec.name,
                    resource_type=spec.type,
                    success=False,
                    message=f"Unknown service: {spec.service}"
                )
        
        except Exception as e:
            return ProvisionResult(
                resource_name=spec.name,
                resource_type=spec.type,
                success=False,
                message=str(e)
            )
    
    def _provision_supabase(self, spec: ResourceSpec, dry_run: bool) -> ProvisionResult:
        """Provision Supabase resource."""
        sql_dir = self.generated_path / "supabase"
        sql_dir.mkdir(exist_ok=True)
        
        if spec.type == ResourceType.DATABASE_TABLE:
            sql = self.supabase.generate_table_sql(spec)
            output_file = sql_dir / f"{spec.name}.sql"
        elif spec.type == ResourceType.STORAGE_BUCKET:
            sql = self.supabase.generate_bucket_sql(spec)
            output_file = sql_dir / f"bucket_{spec.name}.sql"
        elif spec.type == ResourceType.EDGE_FUNCTION:
            sql = self.supabase.generate_function_sql(spec)
            output_file = sql_dir / f"function_{spec.name}.sql"
        else:
            return ProvisionResult(
                resource_name=spec.name,
                resource_type=spec.type,
                success=False,
                message=f"Unknown Supabase resource type: {spec.type}"
            )
        
        output_file.write_text(sql)
        
        return ProvisionResult(
            resource_name=spec.name,
            resource_type=spec.type,
            success=True,
            message=f"Generated SQL: {output_file}",
            outputs={"sql_file": str(output_file)}
        )
    
    def _provision_github(self, spec: ResourceSpec, dry_run: bool) -> ProvisionResult:
        """Provision GitHub resource."""
        gh_dir = self.generated_path / "github"
        gh_dir.mkdir(exist_ok=True)
        
        if spec.type == ResourceType.GITHUB_REPO:
            config = self.github.generate_repo_config(spec)
            output_file = gh_dir / f"{spec.name}_repo.json"
            output_file.write_text(json.dumps(config, indent=2))
            
            # Also generate workflow if configured
            if spec.config.get("workflow"):
                workflow = self.github.generate_workflow_yaml(spec)
                workflow_dir = gh_dir / "workflows"
                workflow_dir.mkdir(exist_ok=True)
                (workflow_dir / f"{spec.name}.yml").write_text(workflow)
            
            return ProvisionResult(
                resource_name=spec.name,
                resource_type=spec.type,
                success=True,
                message=f"Generated repo config: {output_file}",
                outputs={"config_file": str(output_file)}
            )
        
        return ProvisionResult(
            resource_name=spec.name,
            resource_type=spec.type,
            success=False,
            message=f"Unknown GitHub resource type: {spec.type}"
        )
    
    def _provision_cloudflare(self, spec: ResourceSpec, dry_run: bool) -> ProvisionResult:
        """Provision Cloudflare resource."""
        cf_dir = self.generated_path / "cloudflare"
        cf_dir.mkdir(exist_ok=True)
        
        if spec.type == ResourceType.PAGES_PROJECT:
            # Generate wrangler.toml
            wrangler = self.cloudflare.generate_wrangler_toml(spec)
            (cf_dir / f"{spec.name}_wrangler.toml").write_text(wrangler)
            
            # Generate config JSON
            config = self.cloudflare.generate_pages_config(spec)
            output_file = cf_dir / f"{spec.name}_pages.json"
            output_file.write_text(json.dumps(config, indent=2))
            
            return ProvisionResult(
                resource_name=spec.name,
                resource_type=spec.type,
                success=True,
                message=f"Generated Cloudflare Pages config: {output_file}",
                outputs={"config_file": str(output_file)}
            )
        
        return ProvisionResult(
            resource_name=spec.name,
            resource_type=spec.type,
            success=False,
            message=f"Unknown Cloudflare resource type: {spec.type}"
        )
    
    def _provision_render(self, spec: ResourceSpec, dry_run: bool) -> ProvisionResult:
        """Provision Render resource."""
        render_dir = self.generated_path / "render"
        render_dir.mkdir(exist_ok=True)
        
        if spec.type == ResourceType.RENDER_SERVICE:
            # Generate render.yaml
            render_yaml = self.render.generate_render_yaml(spec)
            (render_dir / f"{spec.name}_render.yaml").write_text(render_yaml)
            
            # Generate config JSON
            config = self.render.generate_service_config(spec)
            output_file = render_dir / f"{spec.name}_service.json"
            output_file.write_text(json.dumps(config, indent=2))
            
            return ProvisionResult(
                resource_name=spec.name,
                resource_type=spec.type,
                success=True,
                message=f"Generated Render config: {output_file}",
                outputs={"config_file": str(output_file)}
            )
        
        return ProvisionResult(
            resource_name=spec.name,
            resource_type=spec.type,
            success=False,
            message=f"Unknown Render resource type: {spec.type}"
        )
    
    def _generate_combined_outputs(self, manifest: InfraManifest, results: List[ProvisionResult]):
        """Generate combined output files."""
        
        # Combined SQL migrations
        sql_files = list((self.generated_path / "supabase").glob("*.sql")) if (self.generated_path / "supabase").exists() else []
        if sql_files:
            combined = "\n\n-- ═══════════════════════════════════════\n\n".join(
                f.read_text() for f in sorted(sql_files)
            )
            (self.generated_path / "combined_migration.sql").write_text(combined)
        
        # Provision summary
        summary = {
            "realm_id": manifest.realm_id,
            "version": manifest.version,
            "provisioned_at": datetime.utcnow().isoformat(),
            "results": [
                {
                    "resource": r.resource_name,
                    "type": r.resource_type.value,
                    "success": r.success,
                    "message": r.message
                }
                for r in results
            ]
        }
        
        (self.generated_path / "provision_summary.json").write_text(
            json.dumps(summary, indent=2)
        )


# ═══════════════════════════════════════════════════════════════
# MANIFEST BUILDER
# ═══════════════════════════════════════════════════════════════

class ManifestBuilder:
    """Fluent builder for infrastructure manifests."""
    
    def __init__(self, realm_id: str):
        self.manifest = InfraManifest(realm_id=realm_id)
    
    def description(self, desc: str) -> "ManifestBuilder":
        self.manifest.description = desc
        return self
    
    def add_table(
        self, 
        name: str, 
        columns: List[Dict],
        enable_rls: bool = True,
        timestamps: bool = True
    ) -> "ManifestBuilder":
        """Add a Supabase table."""
        self.manifest.resources.append(ResourceSpec(
            name=name,
            type=ResourceType.DATABASE_TABLE,
            service=ServiceType.SUPABASE,
            config={
                "columns": columns,
                "enable_rls": enable_rls,
                "timestamps": timestamps
            }
        ))
        return self
    
    def add_bucket(self, name: str, public: bool = False) -> "ManifestBuilder":
        """Add a storage bucket."""
        self.manifest.resources.append(ResourceSpec(
            name=name,
            type=ResourceType.STORAGE_BUCKET,
            service=ServiceType.SUPABASE,
            config={"public": public}
        ))
        return self
    
    def add_github_repo(
        self,
        name: str,
        description: str = "",
        private: bool = True,
        with_deploy_workflow: bool = False
    ) -> "ManifestBuilder":
        """Add a GitHub repository."""
        self.manifest.resources.append(ResourceSpec(
            name=name,
            type=ResourceType.GITHUB_REPO,
            service=ServiceType.GITHUB,
            config={
                "description": description,
                "private": private,
                "workflow": with_deploy_workflow,
                "workflow_type": "deploy" if with_deploy_workflow else None
            }
        ))
        return self
    
    def add_pages_project(
        self,
        name: str,
        build_command: str = "npm run build",
        build_output: str = "dist"
    ) -> "ManifestBuilder":
        """Add a Cloudflare Pages project."""
        self.manifest.resources.append(ResourceSpec(
            name=name,
            type=ResourceType.PAGES_PROJECT,
            service=ServiceType.CLOUDFLARE,
            config={
                "build_command": build_command,
                "build_output": build_output
            }
        ))
        return self
    
    def add_render_service(
        self,
        name: str,
        service_type: str = "web",
        plan: str = "starter",
        start_command: str = "python main.py"
    ) -> "ManifestBuilder":
        """Add a Render service."""
        self.manifest.resources.append(ResourceSpec(
            name=name,
            type=ResourceType.RENDER_SERVICE,
            service=ServiceType.RENDER,
            config={
                "service_type": service_type,
                "plan": plan,
                "start_command": start_command
            }
        ))
        return self
    
    def env(self, key: str, value: str) -> "ManifestBuilder":
        """Add an environment variable."""
        self.manifest.environment[key] = value
        return self
    
    def secret(self, name: str) -> "ManifestBuilder":
        """Add a required secret."""
        self.manifest.secrets.append(name)
        return self
    
    def frontend(self, url: str) -> "ManifestBuilder":
        self.manifest.frontend_url = url
        return self
    
    def backend(self, url: str) -> "ManifestBuilder":
        self.manifest.backend_url = url
        return self
    
    def build(self) -> InfraManifest:
        return self.manifest
    
    def write(self, path: Path) -> Path:
        """Write manifest to YAML file."""
        import yaml
        
        output = path / "mauri" / "infra.yaml"
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, "w") as f:
            yaml.safe_dump(self.manifest.to_dict(), f, default_flow_style=False)
        
        return output


# ═══════════════════════════════════════════════════════════════
# EXAMPLE MANIFEST
# ═══════════════════════════════════════════════════════════════

def create_example_manifest(realm_id: str) -> InfraManifest:
    """Create an example infrastructure manifest."""
    
    return (
        ManifestBuilder(realm_id)
        .description(f"Infrastructure for {realm_id} realm")
        
        # Database tables
        .add_table("documents", [
            {"name": "id", "type": "UUID", "default": "gen_random_uuid()"},
            {"name": "title", "type": "TEXT", "nullable": False},
            {"name": "content", "type": "TEXT"},
            {"name": "embedding", "type": "VECTOR(1536)"},
            {"name": "metadata", "type": "JSONB", "default": "'{}'::jsonb"},
            {"name": "realm_id", "type": "TEXT", "nullable": False}
        ])
        
        .add_table("memories", [
            {"name": "id", "type": "UUID", "default": "gen_random_uuid()"},
            {"name": "user_message", "type": "TEXT"},
            {"name": "assistant_response", "type": "TEXT"},
            {"name": "embedding", "type": "VECTOR(1536)"},
            {"name": "kaitiaki", "type": "TEXT"},
            {"name": "realm_id", "type": "TEXT", "nullable": False}
        ])
        
        # Storage
        .add_bucket(f"{realm_id}_assets", public=True)
        .add_bucket(f"{realm_id}_uploads", public=False)
        
        # GitHub
        .add_github_repo(
            f"{realm_id}-frontend",
            description=f"Frontend for {realm_id}",
            with_deploy_workflow=True
        )
        
        # Cloudflare
        .add_pages_project(f"{realm_id}-site")
        
        # Render
        .add_render_service(f"{realm_id}-api", plan="starter")
        
        # Secrets
        .secret("SUPABASE_URL")
        .secret("SUPABASE_KEY")
        .secret("OPENAI_API_KEY")
        
        # URLs
        .frontend(f"https://{realm_id}.pages.dev")
        .backend(f"https://{realm_id}-api.onrender.com")
        
        .build()
    )
