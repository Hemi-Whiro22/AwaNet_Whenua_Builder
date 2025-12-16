"""
Realm Generator Service

Spawns new realms from te_hau/project_template into /realms/
Creates OpenAI assistant + vector store for each realm
Can push to GitHub as its own repository
"""

import os
import json
import shutil
import re
import subprocess
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import uuid

# OpenAI client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Supabase client
try:
    from te_po.utils.supabase_client import get_client as get_supabase
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def is_cloud_environment() -> bool:
    """Check if running in cloud (Render) vs local development"""
    return os.environ.get("RENDER", "") == "true" or os.environ.get("RENDER_ENV") == "production"


class RealmGenerator:
    """Generate new realms from template"""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or os.environ.get("WORKSPACE_ROOT", "/workspaces/The_Awa_Network"))
        self.template_path = self.base_path / "te_hau" / "project_template"
        
        # Realms directory - inside the project for now (permission issues with /workspaces root)
        # Each realm gets its own git repo and can be opened as standalone project
        self.realms_path = self.base_path / "realms"
        self.realms_path.mkdir(exist_ok=True)
        
        # For cloud deployments (Render), use templates folder in te_po
        self.cloud_template_path = Path(__file__).parent.parent / "templates" / "realm_template"
        
        # Check if we're in cloud environment
        self.is_cloud = is_cloud_environment()
        
        self.client = None
        self.supabase = None
        
        if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        if SUPABASE_AVAILABLE:
            self.supabase = get_supabase()
    
    def generate_realm(
        self,
        realm_name: str,
        kaitiaki_name: str = "",
        kaitiaki_role: str = "",
        kaitiaki_instructions: str = "",
        description: str = "",
        selected_apis: Optional[list] = None,
        template: str = "basic",
        cloudflare_hostname: Optional[str] = None,
        pages_project: Optional[str] = None,
        backend_url: Optional[str] = None,
        github_org: Optional[str] = None
    ) -> Dict:
        """
        Generate a new realm from template
        
        Creates realm as sibling to The_Awa_Network at /workspaces/{realm_name}
        Initializes git repo - user pushes to GitHub when ready
        
        Args:
            realm_name: Name of the realm (e.g., te_wai)
            kaitiaki_name: Name of the guardian (e.g., Te Taniwha)
            kaitiaki_role: Role description for the guardian
            kaitiaki_instructions: Custom instructions for the AI assistant
            description: Description for the realm
            selected_apis: List of APIs to enable (vector, memory, assistant, etc.)
            template: Template type (basic, with-kaitiaki, with-storage, full)
            cloudflare_hostname: Optional custom hostname
            pages_project: Optional Cloudflare Pages project name
            backend_url: Optional custom backend URL
        
        Returns:
            Dict with realm info including assistant_id and vector_store_id
        """
        # Normalize realm name (lowercase, underscores for internal, hyphens for git)
        realm_slug = re.sub(r'[^a-z0-9_]', '_', realm_name.lower())
        repo_name = re.sub(r'[^a-z0-9-]', '-', realm_name.lower())  # GitHub-friendly name
        
        # Create realm in /realms/{realm_name}
        # Each realm is its own git repo - can be moved/cloned anywhere
        realm_path = self.realms_path / realm_slug
        
        # Default APIs if none selected
        if selected_apis is None:
            selected_apis = ["vector", "memory", "assistant"]
        
        # Check if realm already exists locally
        if realm_path.exists():
            return {
                "success": False,
                "error": f"Realm '{realm_slug}' already exists at {realm_path}"
            }
        
        # Step 1: Create OpenAI resources (if assistant API is enabled)
        openai_result = {}
        if "assistant" in selected_apis:
            openai_result = self._create_openai_resources(
                realm_slug, 
                kaitiaki_name or f"{realm_name} Guardian",
                kaitiaki_role,
                kaitiaki_instructions,
                description
            )
        
        # Build realm config
        realm_config = {
            "id": str(uuid.uuid4()),
            "realm_name": realm_name,
            "realm_slug": realm_slug,
            "repo_name": repo_name,
            "template": template,
            "kaitiaki": {
                "name": kaitiaki_name,
                "role": kaitiaki_role,
                "instructions": kaitiaki_instructions
            },
            "description": description,
            "selected_apis": selected_apis,
            "created_at": datetime.utcnow().isoformat(),
            "openai": openai_result.get("openai", {}),
            "urls": {
                "cloudflare": cloudflare_hostname or f"{realm_slug}.den-of-the-pack.com",
                "pages": pages_project or f"te-ao-{realm_slug}",
                "backend": backend_url or f"https://{realm_slug}-backend.onrender.com"
            },
            "github": None
        }
        
        # Step 2: Create local filesystem structure (always do this first)
        try:
            self._copy_template(realm_path)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to copy template: {e}"
            }
        
        # Replace placeholders
        replacements = {
            "TemplateRealm": realm_name,
            "template_realm": realm_slug,
            "kitenga-template.example.com": realm_config["urls"]["cloudflare"],
            "te-ao-template": realm_config["urls"]["pages"],
            "https://te-po-template.example.com": realm_config["urls"]["backend"]
        }
        
        self._replace_placeholders(realm_path, replacements)
        
        # Write realm config
        config_path = realm_path / "realm.config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(realm_config, f, indent=2)
        
        # Create initial README
        self._create_realm_readme(realm_path, realm_config)
        
        # Step 3: Initialize git repo (user will push when ready)
        git_result = self._init_git_repo(realm_path, realm_name, kaitiaki_name)
        realm_config["git_initialized"] = git_result.get("success", False)
        
        # Update config
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(realm_config, f, indent=2)
        
        # Step 4: Also store in database if available
        db_result = None
        if self.supabase:
            try:
                db_result = self._save_realm_to_db(realm_config)
            except Exception as e:
                db_result = {"success": False, "error": str(e)}
        
        return {
            "success": True,
            "mode": "local",
            "realm_path": str(realm_path),
            "config": realm_config,
            "git": git_result,
            "database": db_result,
            "next_steps": [
                f"cd {realm_path}",
                "# Open in VS Code and 'Reopen in Container'",
                "git remote add origin https://github.com/YOUR_ORG/{}.git".format(realm_config['repo_name']),
                "git push -u origin main"
            ]
        }
    
    def _init_git_repo(self, realm_path: Path, realm_name: str, kaitiaki_name: str) -> Dict:
        """Initialize git repo with initial commit (user pushes when ready)"""
        try:
            # Initialize git repo
            subprocess.run(
                ["git", "init"],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            
            # Configure git
            subprocess.run(
                ["git", "config", "user.email", "kaitiaki@awa.network"],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Kitenga Whiro"],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            
            # Add all files
            subprocess.run(
                ["git", "add", "."],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            
            # Initial commit
            subprocess.run(
                ["git", "commit", "-m", f"🌊 Initial spawn: {realm_name}\n\nKaitiaki: {kaitiaki_name}\nCreated by Kitenga Whiro realm generator"],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            
            # Rename to main branch
            subprocess.run(
                ["git", "branch", "-M", "main"],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            
            return {
                "success": True,
                "message": "Git repo initialized with initial commit on 'main' branch"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Git command failed: {e.stderr.decode() if e.stderr else str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _push_to_github(
        self,
        realm_path: Path,
        repo_name: str,
        description: str = "",
        github_org: Optional[str] = None,
        private: bool = False
    ) -> Dict:
        """
        Initialize git repo and push to GitHub
        
        Args:
            realm_path: Local path to the realm
            repo_name: Name for the GitHub repository
            description: Repository description
            github_org: GitHub organization (uses personal account if None)
            private: Whether the repo should be private
            
        Returns:
            Dict with repo URL and status
        """
        try:
            # Get GitHub token from environment
            github_token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
            if not github_token:
                return {
                    "success": False,
                    "error": "No GitHub token found. Set GITHUB_TOKEN environment variable."
                }
            
            # Initialize git repo
            subprocess.run(
                ["git", "init"],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            
            # Configure git
            subprocess.run(
                ["git", "config", "user.email", "kaitiaki@awa.network"],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "config", "user.name", "Kitenga Whiro"],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            
            # Add all files
            subprocess.run(
                ["git", "add", "."],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            
            # Initial commit
            subprocess.run(
                ["git", "commit", "-m", f"🌊 Initial spawn: {repo_name}\n\nCreated by Kitenga Whiro realm generator"],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            
            # Create GitHub repo using gh CLI or API
            # Try gh CLI first (simpler)
            create_cmd = ["gh", "repo", "create", repo_name, "--source", str(realm_path), "--push"]
            if github_org:
                create_cmd = ["gh", "repo", "create", f"{github_org}/{repo_name}", "--source", str(realm_path), "--push"]
            
            if private:
                create_cmd.append("--private")
            else:
                create_cmd.append("--public")
            
            if description:
                create_cmd.extend(["--description", description])
            
            result = subprocess.run(
                create_cmd,
                cwd=realm_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Fallback: try creating via API and pushing manually
                return self._push_to_github_api(
                    realm_path, repo_name, description, github_org, private, github_token
                )
            
            # Parse repo URL from output
            repo_url = f"https://github.com/{github_org or 'user'}/{repo_name}"
            
            return {
                "success": True,
                "repo_name": repo_name,
                "repo_url": repo_url,
                "method": "gh_cli"
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": f"Git command failed: {e.stderr.decode() if e.stderr else str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _push_to_github_api(
        self,
        realm_path: Path,
        repo_name: str,
        description: str,
        github_org: Optional[str],
        private: bool,
        github_token: str
    ) -> Dict:
        """Fallback: Create repo via GitHub API and push"""
        import urllib.request
        import urllib.error
        
        try:
            # Create repo via API
            api_url = "https://api.github.com/user/repos"
            if github_org:
                api_url = f"https://api.github.com/orgs/{github_org}/repos"
            
            data = json.dumps({
                "name": repo_name,
                "description": description,
                "private": private,
                "auto_init": False
            }).encode()
            
            req = urllib.request.Request(
                api_url,
                data=data,
                headers={
                    "Authorization": f"token {github_token}",
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            
            with urllib.request.urlopen(req) as response:
                repo_data = json.loads(response.read().decode())
            
            clone_url = repo_data["clone_url"]
            html_url = repo_data["html_url"]
            
            # Add remote and push
            # Use token in URL for auth
            auth_url = clone_url.replace("https://", f"https://{github_token}@")
            
            subprocess.run(
                ["git", "remote", "add", "origin", auth_url],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            
            subprocess.run(
                ["git", "branch", "-M", "main"],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            
            subprocess.run(
                ["git", "push", "-u", "origin", "main"],
                cwd=realm_path,
                check=True,
                capture_output=True
            )
            
            return {
                "success": True,
                "repo_name": repo_name,
                "repo_url": html_url,
                "method": "api"
            }
            
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            return {
                "success": False,
                "error": f"GitHub API error {e.code}: {error_body}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _save_realm_to_db(self, realm_config: Dict) -> Dict:
        """Save realm configuration to Supabase database and create realm-specific tables"""
        if not self.supabase:
            return {"success": False, "error": "Supabase not configured"}
        
        realm_slug = realm_config["realm_slug"]
        
        try:
            # Check if realm already exists in master table
            existing = self.supabase.table("kitenga_realms").select("id").eq("realm_slug", realm_slug).execute()
            if existing.data and len(existing.data) > 0:
                return {"success": False, "error": f"Realm '{realm_slug}' already exists"}
            
            # Step 1: Create realm-specific tables
            tables_result = self._create_realm_tables(realm_config)
            if not tables_result.get("success"):
                return tables_result
            
            # Step 2: Insert into master realms table
            result = self.supabase.table("kitenga_realms").insert({
                "id": realm_config["id"],
                "realm_name": realm_config["realm_name"],
                "realm_slug": realm_slug,
                "template": realm_config["template"],
                "kaitiaki_name": realm_config["kaitiaki"]["name"],
                "kaitiaki_role": realm_config["kaitiaki"]["role"],
                "kaitiaki_instructions": realm_config["kaitiaki"]["instructions"],
                "description": realm_config["description"],
                "selected_apis": realm_config["selected_apis"],
                "openai_assistant_id": realm_config["openai"].get("assistant_id") if realm_config["openai"] else None,
                "openai_vector_store_id": realm_config["openai"].get("vector_store_id") if realm_config["openai"] else None,
                "urls": realm_config["urls"],
                "config": realm_config,
                "created_at": realm_config["created_at"]
            }).execute()
            
            # Step 3: Insert kaitiaki into realm's kaitiaki table
            kaitiaki_result = self._insert_realm_kaitiaki(realm_config)
            
            return {
                "success": True, 
                "data": result.data,
                "tables_created": tables_result.get("tables", []),
                "kaitiaki_inserted": kaitiaki_result.get("success", False)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_realm_tables(self, realm_config: Dict) -> Dict:
        """Create realm-specific tables in Supabase"""
        if not self.supabase:
            return {"success": False, "error": "Supabase not configured"}
        
        realm_slug = realm_config["realm_slug"]
        kaitiaki_name = realm_config["kaitiaki"]["name"]
        
        # Table names for this realm
        config_table = f"{realm_slug}_config"
        kaitiaki_table = f"{realm_slug}_kaitiaki"
        artifacts_table = f"{realm_slug}_artifacts"
        logs_table = f"{realm_slug}_logs"
        
        # Generate SQL for realm tables
        sql = f"""
-- Realm: {realm_config['realm_name']}
-- Kaitiaki: {kaitiaki_name}
-- Created: {realm_config['created_at']}

-- Config table for {realm_slug}
CREATE TABLE IF NOT EXISTS {config_table} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key TEXT UNIQUE NOT NULL,
    value JSONB,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Kaitiaki table for {realm_slug}
CREATE TABLE IF NOT EXISTS {kaitiaki_table} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    role TEXT,
    instructions TEXT,
    assistant_id TEXT,
    vector_store_id TEXT,
    thread_id TEXT,
    mauri_status TEXT DEFAULT 'active',
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Artifacts table for {realm_slug}
CREATE TABLE IF NOT EXISTS {artifacts_table} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    type TEXT NOT NULL,
    name TEXT,
    content TEXT,
    metadata JSONB,
    embedding vector(1536),
    kaitiaki_id UUID REFERENCES {kaitiaki_table}(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Logs table for {realm_slug}
CREATE TABLE IF NOT EXISTS {logs_table} (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event TEXT NOT NULL,
    detail TEXT,
    source TEXT,
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_{realm_slug}_config_key ON {config_table}(key);
CREATE INDEX IF NOT EXISTS idx_{realm_slug}_artifacts_type ON {artifacts_table}(type);
CREATE INDEX IF NOT EXISTS idx_{realm_slug}_logs_event ON {logs_table}(event);
CREATE INDEX IF NOT EXISTS idx_{realm_slug}_logs_created ON {logs_table}(created_at DESC);
"""
        
        try:
            # Execute SQL via Supabase RPC (requires a function to be set up)
            # For now, store the SQL and try to execute basic operations
            
            # Store the migration SQL in the realm config
            realm_config["migration_sql"] = sql
            
            # Try to create tables using raw SQL execution if available
            # This requires the exec_sql RPC function in Supabase
            try:
                self.supabase.rpc("exec_sql", {"sql": sql}).execute()
            except Exception:
                # If RPC not available, we'll store SQL for manual execution
                pass
            
            return {
                "success": True,
                "tables": [config_table, kaitiaki_table, artifacts_table, logs_table],
                "sql": sql
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _insert_realm_kaitiaki(self, realm_config: Dict) -> Dict:
        """Insert kaitiaki record into realm's kaitiaki table"""
        if not self.supabase:
            return {"success": False, "error": "Supabase not configured"}
        
        realm_slug = realm_config["realm_slug"]
        kaitiaki_table = f"{realm_slug}_kaitiaki"
        
        try:
            result = self.supabase.table(kaitiaki_table).insert({
                "name": realm_config["kaitiaki"]["name"],
                "role": realm_config["kaitiaki"]["role"],
                "instructions": realm_config["kaitiaki"]["instructions"],
                "assistant_id": realm_config["openai"].get("assistant_id") if realm_config["openai"] else None,
                "vector_store_id": realm_config["openai"].get("vector_store_id") if realm_config["openai"] else None,
                "mauri_status": "active",
                "metadata": {
                    "realm_id": realm_config["id"],
                    "template": realm_config["template"],
                    "selected_apis": realm_config["selected_apis"]
                }
            }).execute()
            
            return {"success": True, "data": result.data}
        except Exception as e:
            # Table might not exist yet if SQL wasn't executed
            return {"success": False, "error": str(e), "note": "Run migration SQL manually"}
    
    def _create_openai_resources(
        self, 
        realm_slug: str, 
        kaitiaki_name: str, 
        kaitiaki_role: str = "",
        kaitiaki_instructions: str = "",
        description: str = ""
    ) -> Dict:
        """Create OpenAI assistant and vector store for the realm"""
        if not self.client:
            return {"openai": None, "note": "OpenAI not configured"}
        
        try:
            # Create vector store
            vector_store = self.client.vector_stores.create(
                name=f"vs_{realm_slug}",
                metadata={
                    "realm": realm_slug,
                    "kaitiaki": kaitiaki_name,
                    "created_by": "kitenga_whiro"
                }
            )
            
            # Build assistant instructions
            base_instructions = kaitiaki_instructions or f"""You are {kaitiaki_name}, the guardian (kaitiaki) of the {realm_slug} realm.

{kaitiaki_role or f"You protect and guide the {realm_slug} realm, answering questions and providing wisdom from your vector store."}

{description}"""

            full_instructions = f"""{base_instructions}

When answering questions:
1. First search your vector store for relevant context
2. Ground your answers in the retrieved knowledge
3. Be helpful but maintain your role as guardian
4. If you don't have relevant information, say so clearly

Tū māia, tū kaha - Stand with courage, stand with strength."""

            # Create assistant with file_search tool
            assistant = self.client.beta.assistants.create(
                name=f"Kaitiaki: {kaitiaki_name}",
                instructions=full_instructions,
                model="gpt-4o-mini",
                tools=[{"type": "file_search"}],
                tool_resources={
                    "file_search": {
                        "vector_store_ids": [vector_store.id]
                    }
                },
                metadata={
                    "realm": realm_slug,
                    "kaitiaki": kaitiaki_name,
                    "created_by": "kitenga_whiro"
                }
            )
            
            return {
                "openai": {
                    "assistant_id": assistant.id,
                    "assistant_name": assistant.name,
                    "vector_store_id": vector_store.id,
                    "vector_store_name": vector_store.name
                }
            }
        except Exception as e:
            return {
                "openai": None,
                "error": str(e)
            }
    
    def _copy_template(self, dest_path: Path):
        """Copy template directory to destination"""
        # Try multiple template locations
        template = None
        
        # 1. Check local workspace template (dev)
        if self.template_path.exists():
            template = self.template_path
        # 2. Check cloud template in te_po (production)
        elif self.cloud_template_path.exists():
            template = self.cloud_template_path
        # 3. Check templates folder in workspace root
        else:
            root_template = self.base_path / "templates" / "realm_template"
            if root_template.exists():
                template = root_template
        
        if template is None:
            # No template found - create minimal structure instead
            self._create_minimal_realm(dest_path)
            return
        
        # Copy entire template
        shutil.copytree(
            template,
            dest_path,
            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git')
        )
        
        # Rename .env.template to .env
        env_template = dest_path / ".env.template"
        env_file = dest_path / ".env"
        if env_template.exists():
            shutil.copy(env_template, env_file)
    
    def _create_minimal_realm(self, dest_path: Path):
        """Create a minimal realm structure when no template is available"""
        dest_path.mkdir(parents=True, exist_ok=True)
        
        # Create basic directories
        (dest_path / "mauri").mkdir(exist_ok=True)
        (dest_path / "config").mkdir(exist_ok=True)
        (dest_path / "docs").mkdir(exist_ok=True)
        
        # Create basic mauri state
        mauri_state = {
            "realm": dest_path.name,
            "created_at": datetime.utcnow().isoformat(),
            "mauri_status": "active",
            "initialized": True
        }
        (dest_path / "mauri" / "state.json").write_text(
            json.dumps(mauri_state, indent=2), encoding='utf-8'
        )
    
    def _replace_placeholders(self, realm_path: Path, replacements: Dict[str, str]):
        """Replace template placeholders in all files"""
        # Files to process
        text_extensions = {'.json', '.yml', '.yaml', '.md', '.txt', '.env', '.sh', '.py', '.js', '.jsx', '.ts', '.tsx', '.toml', '.html', '.css'}
        
        for file_path in realm_path.rglob('*'):
            if file_path.is_file():
                # Check if it's a text file we should process
                if file_path.suffix.lower() in text_extensions or file_path.name.startswith('.env'):
                    try:
                        content = file_path.read_text(encoding='utf-8')
                        original = content
                        
                        for placeholder, value in replacements.items():
                            content = content.replace(placeholder, value)
                        
                        if content != original:
                            file_path.write_text(content, encoding='utf-8')
                    except (UnicodeDecodeError, PermissionError):
                        continue
    
    def _create_realm_readme(self, realm_path: Path, config: Dict):
        """Create a README for the realm"""
        readme_content = f"""# {config['realm_name']}

**Kaitiaki:** {config['kaitiaki']}
**Created:** {config['created_at']}

{config.get('description', '')}

## Quick Start

### Open in Dev Container

1. Open VS Code
2. File → Open Folder → Select this folder
3. When prompted, "Reopen in Container"

### Manual Start

```bash
# Backend proxy
cd te_po_proxy && python main.py

# Frontend (if applicable)
cd te_ao && npm run dev
```

## OpenAI Resources

- **Assistant ID:** `{config.get('openai', {}).get('assistant_id', 'Not created')}`
- **Vector Store ID:** `{config.get('openai', {}).get('vector_store_id', 'Not created')}`

## URLs

- **Cloudflare:** `{config['urls']['cloudflare']}`
- **Backend:** `{config['urls']['backend']}`
- **Pages Project:** `{config['urls']['pages']}`

## Realm Structure

```
{config['realm_slug']}/
├── .devcontainer/       # VS Code dev container config
├── .env                 # Environment variables
├── kaitiaki/            # Guardian-specific data
├── mauri/               # Realm state
├── te_po_proxy/         # Backend proxy to main te_po
└── te_ao/               # Frontend (if applicable)
```

---
*Generated by Kitenga Whiro - Realm Generator*
"""
        readme_path = realm_path / "README.md"
        readme_path.write_text(readme_content, encoding='utf-8')
    
    def list_realms(self) -> List[Dict]:
        """List all spawned realms from database and/or filesystem"""
        realms = []
        
        # Cloud mode: Query database
        if self.is_cloud and self.supabase:
            try:
                result = self.supabase.table("kitenga_realms").select("*").order("created_at", desc=True).execute()
                for row in result.data or []:
                    realms.append({
                        "id": row.get("id"),
                        "source": "database",
                        "config": row.get("config") or {
                            "realm_name": row.get("realm_name"),
                            "realm_slug": row.get("realm_slug"),
                            "kaitiaki": {
                                "name": row.get("kaitiaki_name"),
                                "role": row.get("kaitiaki_role")
                            },
                            "description": row.get("description"),
                            "selected_apis": row.get("selected_apis"),
                            "openai": {
                                "assistant_id": row.get("openai_assistant_id"),
                                "vector_store_id": row.get("openai_vector_store_id")
                            },
                            "urls": row.get("urls"),
                            "created_at": row.get("created_at")
                        }
                    })
            except Exception as e:
                print(f"Error listing realms from database: {e}")
        
        # Local mode: Also check filesystem
        if self.realms_path.exists():
            for item in self.realms_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    config_path = item / "realm.config.json"
                    if config_path.exists():
                        try:
                            with open(config_path, 'r', encoding='utf-8') as f:
                                config = json.load(f)
                            # Don't duplicate if already in database results
                            slug = config.get("realm_slug", item.name)
                            if not any(r.get("config", {}).get("realm_slug") == slug for r in realms):
                                realms.append({
                                    "path": str(item),
                                    "source": "filesystem",
                                    "config": config
                                })
                        except json.JSONDecodeError:
                            realms.append({
                                "path": str(item),
                                "source": "filesystem",
                                "config": None,
                                "error": "Invalid config"
                            })
        
        return realms
    
    def get_realm(self, realm_slug: str) -> Optional[Dict]:
        """Get a specific realm by slug from database or filesystem"""
        # Cloud mode: Check database first
        if self.is_cloud and self.supabase:
            try:
                result = self.supabase.table("kitenga_realms").select("*").eq("realm_slug", realm_slug).single().execute()
                if result.data:
                    return result.data.get("config") or result.data
            except Exception:
                pass
        
        # Check filesystem
        realm_path = self.realms_path / realm_slug
        if realm_path.exists():
            config_path = realm_path / "realm.config.json"
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except json.JSONDecodeError:
                    return {"error": "Invalid config"}
            return {"path": str(realm_path), "config": None}
        
        return None


# Convenience functions
_generator = None

def get_generator() -> RealmGenerator:
    """Get or create realm generator singleton"""
    global _generator
    if _generator is None:
        _generator = RealmGenerator()
    return _generator

def generate_realm(**kwargs) -> Dict:
    """Generate a new realm"""
    return get_generator().generate_realm(**kwargs)

def list_realms() -> list:
    """List all realms"""
    return get_generator().list_realms()

def get_realm(realm_slug: str) -> Optional[Dict]:
    """Get realm by slug"""
    return get_generator().get_realm(realm_slug)
