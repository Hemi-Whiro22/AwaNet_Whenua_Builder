#!/usr/bin/env python3
"""
Realm Generator - Create new specialized realms from template.

This generates a new realm (e.g., Cards Realm, Translator Realm) by:
1. Cloning from project_template
2. Customizing configs
3. Generating realm-specific Kaitiaki using SDK
4. Creating context docs for that Kaitiaki
5. (Optional) Pushing to git as new project

Usage:
    python te_hau/scripts/generate_realm.py \\
        --name "Cards Realm" \\
        --slug cards \\
        --kaitiaki-name "katu" \\
        --kaitiaki-role "cards_oracle" \\
        --description "Oracle for card cataloging and search" \\
        [--push-to-git https://github.com/org/cards-realm.git]
"""

import json
import yaml
import shutil
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import argparse
import subprocess


class RealmGenerator:
    """Generate new specialized realms from template."""

    def __init__(self, project_root: Path = None):
        """Initialize with project root.

        Args:
            project_root: Path to The_Awa_Network project (for template/sdk)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.template_dir = project_root / "te_hau" / "project_template"
        self.sdk_dir = project_root / "te_hau" / "sdk"

    def generate(
        self,
        name: str,
        slug: str,
        kaitiaki_name: str,
        kaitiaki_role: str,
        description: str,
        push_to_git: Optional[str] = None,
    ) -> bool:
        """Generate a new realm."""
        print(f"\n🏔️  Realm Generator - {name}")
        print("=" * 60)

        realm_dir = self.project_root / slug

        # Step 1: Clone template
        print(f"\n1️⃣  Cloning template to {realm_dir}...")
        if not self._clone_template(realm_dir):
            return False

        # Step 2: Customize configs
        print(f"\n2️⃣  Customizing configs...")
        if not self._customize_configs(realm_dir, name, slug):
            return False

        # Step 3: Generate Kaitiaki
        print(f"\n3️⃣  Generating Kaitiaki '{kaitiaki_name}'...")
        if not self._generate_kaitiaki(realm_dir, kaitiaki_name, kaitiaki_role, description):
            return False

        # Step 4: Create context docs
        print(f"\n4️⃣  Creating context documentation...")
        if not self._create_context_docs(realm_dir, kaitiaki_name, kaitiaki_role, description):
            return False

        # Step 5: (Optional) Push to git
        if push_to_git:
            print(f"\n5️⃣  Pushing to git {push_to_git}...")
            if not self._push_to_git(realm_dir, push_to_git, name):
                print("⚠️  Git push failed - realm generated but not pushed")

        print(f"\n✅ Realm '{name}' generated successfully!")
        print(f"   Location: {realm_dir}")
        print(f"   Kaitiaki: {kaitiaki_name}")
        return True

    def _clone_template(self, target_dir: Path) -> bool:
        """Clone template directory."""
        try:
            if target_dir.exists():
                print(
                    f"⚠️  Directory {target_dir} already exists, skipping clone")
                return True

            shutil.copytree(self.template_dir, target_dir,
                            ignore=shutil.ignore_patterns('.git'))
            print(f"✅ Template cloned to {target_dir}")
            return True
        except Exception as e:
            print(f"❌ Failed to clone template: {e}")
            return False

    def _customize_configs(self, realm_dir: Path, name: str, slug: str) -> bool:
        """Customize realm configs."""
        try:
            # Update .env
            env_file = realm_dir / ".env"
            if env_file.exists():
                env_content = env_file.read_text()
                env_content = env_content.replace("TemplateRealm", name)
                env_content = env_content.replace(
                    "te-ao-template", f"te-ao-{slug}")
                env_file.write_text(env_content)

            # Update config files
            for config_file in realm_dir.glob("config/*.json"):
                content = config_file.read_text()
                content = content.replace("TemplateRealm", name)
                config_file.write_text(content)

            print(f"✅ Configs customized")
            return True
        except Exception as e:
            print(f"❌ Failed to customize configs: {e}")
            return False

    def _generate_kaitiaki(
        self,
        realm_dir: Path,
        kaitiaki_name: str,
        kaitiaki_role: str,
        description: str,
    ) -> bool:
        """Generate Kaitiaki using SDK."""
        try:
            # Create mauri/kaitiaki_templates directory
            templates_dir = realm_dir / "mauri" / "kaitiaki_templates"
            templates_dir.mkdir(parents=True, exist_ok=True)

            # Create Kaitiaki YAML template with isolation rules
            kaitiaki_yaml = {
                "metadata": {
                    "name": kaitiaki_name,
                    "role": kaitiaki_role,
                    "purpose": description,
                    "version": "1.0.0",
                    "realm_slug": slug,
                    "created_at": datetime.now().isoformat() + "Z",
                    "isolated": True,
                },
                "isolation": {
                    "level": "strict",
                    "description": "This Kaitiaki is completely isolated to prevent context bleed",
                    "aware_of": [
                        "own_realm_files",
                        "own_realm_config",
                        "own_realm_state",
                        "local_te_po_proxy"
                    ],
                    "not_aware_of": [
                        "The_Awa_Network_context",
                        "sibling_realm_data",
                        "main_Te_Po_state",
                        "main_Te_Ao_frontend"
                    ],
                    "access_control": {
                        "allow_parent_traversal": False,
                        "allow_workspaces_access": False,
                        "allow_sibling_realms": False,
                        "allow_main_awa_network": False
                    }
                },
                "identity": {
                    "glyph": "🔮",
                    "korowai": "te_po_proxy",
                    "knowledge_domain": "this_realm_only",
                    "visibility_scope": "realm_local",
                },
                "backend": {
                    "proxy": {
                        "url": "http://localhost:8001",
                        "type": "te_po_proxy",
                        "description": "Local realm backend - DO NOT PROXY TO MAIN AWA NETWORK"
                    },
                    "forbidden_targets": [
                        "https://main-te-po.example.com",
                        "main_te_po",
                        "te_po"
                    ]
                },
                "state": {
                    "carving_log": f"kaitiaki/{kaitiaki_name}/{kaitiaki_name}_carving_log.jsonl",
                    "state_file": f"kaitiaki/{kaitiaki_name}/{kaitiaki_name}_state.json",
                },
                "context": {
                    "paths": {
                        "realm_root": ".",
                        "knowledge_base": "./mauri",
                        "config": "./config",
                        "kaitiaki_dir": "./kaitiaki"
                    },
                    "forbidden_paths": [
                        "../",
                        "../../",
                        "/workspaces/",
                        "/home/"
                    ]
                },
            }

            # Write YAML template
            yaml_file = templates_dir / f"{kaitiaki_name}.yaml"
            with open(yaml_file, 'w') as f:
                yaml.dump(kaitiaki_yaml, f, default_flow_style=False)

            print(f"✅ Kaitiaki template: {yaml_file}")

            # Create kaitiaki output directory
            kaitiaki_dir = realm_dir / "kaitiaki" / kaitiaki_name
            kaitiaki_dir.mkdir(parents=True, exist_ok=True)

            # Create initial manifest
            manifest = {
                "name": kaitiaki_name,
                "role": kaitiaki_role,
                "purpose": description,
                "version": "1.0.0",
                "created_at": datetime.now().isoformat() + "Z",
                "state_file": f"kaitiaki/{kaitiaki_name}/{kaitiaki_name}_state.json",
                "carving_log": f"kaitiaki/{kaitiaki_name}/{kaitiaki_name}_carving_log.jsonl",
            }

            manifest_file = kaitiaki_dir / f"{kaitiaki_name}_manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)

            print(f"✅ Kaitiaki manifest: {manifest_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to generate Kaitiaki: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _create_context_docs(
        self,
        realm_dir: Path,
        kaitiaki_name: str,
        kaitiaki_role: str,
        description: str,
    ) -> bool:
        """Create context documentation for Kaitiaki."""
        try:
            docs_dir = realm_dir / "kaitiaki" / kaitiaki_name / "docs"
            docs_dir.mkdir(parents=True, exist_ok=True)

            # Create README
            readme_content = f"""# {kaitiaki_name.title()} Kaitiaki

**Role:** {kaitiaki_role}
**Purpose:** {description}

## Overview

This is a realm-specific Kaitiaki that operates within this project and communicates with the main Te Pō backend.

## Configuration

- **Manifest:** `kaitiaki/{kaitiaki_name}/{kaitiaki_name}_manifest.json`
- **Template:** `mauri/kaitiaki_templates/{kaitiaki_name}.yaml`
- **State:** `kaitiaki/{kaitiaki_name}/{kaitiaki_name}_state.json`
- **Log:** `kaitiaki/{kaitiaki_name}/{kaitiaki_name}_carving_log.jsonl`

## Compilation

To recompile the Kaitiaki after editing the YAML template:

```bash
python mauri/scripts/compile_kaitiaki.py --agent {kaitiaki_name}
```

## Backend Integration

This Kaitiaki talks to the main Te Pō backend at `{kaitiaki_role}`.

Configure the backend URL in `.env`:
```
TE_PO_BASE_URL=https://[main-te-po-backend]
```

## Capabilities

- Vector search against main Te Pō
- Pipeline integration
- Document processing
- Session management

## Development

See `docs/` folder for detailed guides.
"""

            readme_file = docs_dir / "README.md"
            readme_file.write_text(readme_content)
            print(f"✅ Documentation: {readme_file}")

            # Create CONTEXT.md
            context_content = f"""# {kaitiaki_name.title()} - Context for Development

## Quick Facts

- **Name:** {kaitiaki_name}
- **Role:** {kaitiaki_role}
- **Purpose:** {description}
- **Backend:** Main Te Pō (via {kaitiaki_role})
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Architecture

```
{kaitiaki_name} Kaitiaki
    ↓
This Realm's Te Pō (mini_te_po)
    ↓
Main Te Pō Backend
    ↓
Supabase + Vector Store
```

## Key Files

- `mauri/kaitiaki_templates/{kaitiaki_name}.yaml` - Source definition
- `kaitiaki/{kaitiaki_name}/{kaitiaki_name}_manifest.json` - Runtime manifest
- `kaitiaki/{kaitiaki_name}/{kaitiaki_name}_state.json` - Current state
- `.env` - Backend configuration

## Next Steps

1. Configure backend URL in `.env`
2. Register Kaitiaki with main Te Pō
3. Test communication
4. Deploy realm
"""

            context_file = docs_dir / "CONTEXT.md"
            context_file.write_text(context_content)
            print(f"✅ Context: {context_file}")

            return True
        except Exception as e:
            print(f"❌ Failed to create docs: {e}")
            return False

    def _push_to_git(self, realm_dir: Path, git_url: str, realm_name: str) -> bool:
        """Push realm to git repository."""
        try:
            # Initialize git if needed
            git_dir = realm_dir / ".git"
            if not git_dir.exists():
                subprocess.run(["git", "init"], cwd=realm_dir, check=True)

            # Add and commit
            subprocess.run(["git", "add", "."], cwd=realm_dir, check=True)
            subprocess.run(
                ["git", "commit", "-m", f"Initial commit: {realm_name}"],
                cwd=realm_dir,
                check=True,
            )

            # Add remote and push
            subprocess.run(
                ["git", "remote", "add", "origin", git_url],
                cwd=realm_dir,
                check=False,  # May already exist
            )
            subprocess.run(
                ["git", "branch", "-M", "main"],
                cwd=realm_dir,
                check=True,
            )
            subprocess.run(
                ["git", "push", "-u", "origin", "main"],
                cwd=realm_dir,
                check=True,
            )

            print(f"✅ Pushed to {git_url}")
            return True
        except Exception as e:
            print(f"⚠️  Git push failed: {e}")
            return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate a new Realm")
    parser.add_argument("--name", required=True,
                        help="Realm name (e.g., 'Cards Realm')")
    parser.add_argument("--slug", required=True,
                        help="Realm slug (e.g., 'cards')")
    parser.add_argument("--kaitiaki-name", required=True,
                        help="Kaitiaki name (e.g., 'katu')")
    parser.add_argument("--kaitiaki-role", required=True,
                        help="Kaitiaki role (e.g., 'cards_oracle')")
    parser.add_argument("--description", required=True,
                        help="Realm/Kaitiaki description")
    parser.add_argument("--push-to-git", help="Optional git URL to push to")

    args = parser.parse_args()

    generator = RealmGenerator()
    success = generator.generate(
        name=args.name,
        slug=args.slug,
        kaitiaki_name=args.kaitiaki_name,
        kaitiaki_role=args.kaitiaki_role,
        description=args.description,
        push_to_git=args.push_to_git,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
