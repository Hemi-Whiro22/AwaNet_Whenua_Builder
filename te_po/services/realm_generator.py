"""
Realm Generator Service

Spawns new realms from te_hau/project_template into /realms/
Creates OpenAI assistant + vector store for each realm
"""

import os
import json
import shutil
import re
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import uuid

# OpenAI client
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class RealmGenerator:
    """Generate new realms from template"""
    
    def __init__(self, base_path: Optional[str] = None):
        self.base_path = Path(base_path or os.environ.get("WORKSPACE_ROOT", "/workspaces/The_Awa_Network"))
        self.template_path = self.base_path / "te_hau" / "project_template"
        self.realms_path = self.base_path / "realms"
        self.client = None
        
        if OPENAI_AVAILABLE and os.environ.get("OPENAI_API_KEY"):
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    def generate_realm(
        self,
        realm_name: str,
        kaitiaki_name: str,
        description: str = "",
        cloudflare_hostname: Optional[str] = None,
        pages_project: Optional[str] = None,
        backend_url: Optional[str] = None
    ) -> Dict:
        """
        Generate a new realm from template
        
        Args:
            realm_name: Name of the realm (e.g., te_wai)
            kaitiaki_name: Name of the guardian (e.g., Te Taniwha)
            description: Description for the realm
            cloudflare_hostname: Optional custom hostname
            pages_project: Optional Cloudflare Pages project name
            backend_url: Optional custom backend URL
        
        Returns:
            Dict with realm info including assistant_id and vector_store_id
        """
        # Normalize realm name (lowercase, underscores)
        realm_slug = re.sub(r'[^a-z0-9_]', '_', realm_name.lower())
        realm_path = self.realms_path / realm_slug
        
        # Check if realm already exists
        if realm_path.exists():
            return {
                "success": False,
                "error": f"Realm '{realm_slug}' already exists at {realm_path}"
            }
        
        # Step 1: Create OpenAI resources
        openai_result = self._create_openai_resources(realm_slug, kaitiaki_name, description)
        
        # Step 2: Copy template
        try:
            self._copy_template(realm_path)
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to copy template: {e}"
            }
        
        # Step 3: Replace placeholders
        replacements = {
            "TemplateRealm": realm_name,
            "kitenga-template.example.com": cloudflare_hostname or f"{realm_slug}.den-of-the-pack.com",
            "te-ao-template": pages_project or f"te-ao-{realm_slug}",
            "https://te-po-template.example.com": backend_url or f"https://{realm_slug}-backend.onrender.com"
        }
        
        self._replace_placeholders(realm_path, replacements)
        
        # Step 4: Create realm config
        realm_config = {
            "realm_name": realm_name,
            "realm_slug": realm_slug,
            "kaitiaki": kaitiaki_name,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "openai": openai_result.get("openai", {}),
            "urls": {
                "cloudflare": replacements["kitenga-template.example.com"],
                "pages": replacements["te-ao-template"],
                "backend": replacements["https://te-po-template.example.com"]
            }
        }
        
        # Write realm config
        config_path = realm_path / "realm.config.json"
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(realm_config, f, indent=2)
        
        # Step 5: Create initial README
        self._create_realm_readme(realm_path, realm_config)
        
        return {
            "success": True,
            "realm_path": str(realm_path),
            "config": realm_config
        }
    
    def _create_openai_resources(self, realm_slug: str, kaitiaki_name: str, description: str) -> Dict:
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
            
            # Create assistant with file_search tool
            assistant = self.client.beta.assistants.create(
                name=f"Kaitiaki: {kaitiaki_name}",
                instructions=f"""You are {kaitiaki_name}, the guardian (kaitiaki) of the {realm_slug} realm.

{description or f"You protect and guide the {realm_slug} realm, answering questions and providing wisdom from your vector store."}

When answering questions:
1. First search your vector store for relevant context
2. Ground your answers in the retrieved knowledge
3. Be helpful but maintain your role as guardian
4. If you don't have relevant information, say so clearly

Tū māia, tū kaha - Stand with courage, stand with strength.""",
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
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template not found at {self.template_path}")
        
        # Copy entire template
        shutil.copytree(
            self.template_path,
            dest_path,
            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git')
        )
        
        # Rename .env.template to .env
        env_template = dest_path / ".env.template"
        env_file = dest_path / ".env"
        if env_template.exists():
            shutil.copy(env_template, env_file)
    
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
    
    def list_realms(self) -> list:
        """List all spawned realms"""
        realms = []
        if not self.realms_path.exists():
            return realms
        
        for item in self.realms_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                config_path = item / "realm.config.json"
                if config_path.exists():
                    try:
                        with open(config_path, 'r', encoding='utf-8') as f:
                            config = json.load(f)
                        realms.append({
                            "path": str(item),
                            "config": config
                        })
                    except json.JSONDecodeError:
                        realms.append({
                            "path": str(item),
                            "config": None,
                            "error": "Invalid config"
                        })
                else:
                    realms.append({
                        "path": str(item),
                        "config": None
                    })
        
        return realms
    
    def get_realm(self, realm_slug: str) -> Optional[Dict]:
        """Get a specific realm by slug"""
        realm_path = self.realms_path / realm_slug
        if not realm_path.exists():
            return None
        
        config_path = realm_path / "realm.config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"error": "Invalid config"}
        
        return {"path": str(realm_path), "config": None}


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
