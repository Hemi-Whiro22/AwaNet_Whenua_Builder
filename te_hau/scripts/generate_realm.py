#!/usr/bin/env python3
"""
Realm Generator - Create new thin realms from template.

This generates a new realm by:
1. Copying templates/realm_template to the target directory
2. Generating a unique bearer token
3. Writing .env with realm configuration
4. Creating mauri/realm_manifest.json

The resulting realm connects to a main Te Pó backend via proxy (no dependency on Te Pó code).

Usage:
    python te_hau/scripts/generate_realm.py \\
        --realm-id "cards" \\
        --realm-name "Cards Realm" \\
        --te-po-url "https://te-po.example.com" \\
        [--bearer-key "existing-key"]
"""

import json
import sys
import shutil
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional
import argparse
import os


class RealmGenerator:
    """Generate new thin realms from template."""

    def __init__(self, project_root: Path = None):
        """Initialize with project root."""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.template_dir = project_root / "templates" / "realm_template"

    def generate(
        self,
        realm_id: str,
        realm_name: str,
        te_po_url: str,
        bearer_key: Optional[str] = None,
    ) -> bool:
        """Generate a new realm."""
        print(f"\n🌍 Realm Generator - {realm_name}")
        print("=" * 60)

        # Validate template exists
        if not self.template_dir.exists():
            print(f"❌ Template not found: {self.template_dir}")
            return False

        realm_dir = self.project_root / realm_id

        # Step 1: Copy template
        print(f"\n1️⃣  Copying template to {realm_dir}...")
        if not self._copy_template(realm_dir):
            return False

        # Step 2: Generate bearer token if not provided
        if not bearer_key:
            bearer_key = str(uuid.uuid4())
            print(f"   Generated bearer token: {bearer_key}")

        # Step 3: Write .env
        print(f"\n2️⃣  Creating .env...")
        if not self._write_env(realm_dir, realm_id, realm_name, te_po_url, bearer_key):
            return False

        # Step 4: Write realm_manifest.json
        print(f"\n3️⃣  Creating mauri/realm_manifest.json...")
        if not self._write_manifest(realm_dir, realm_id, realm_name, te_po_url):
            return False

        print(f"\n✅ Realm '{realm_name}' generated successfully!")
        print(f"   Location: {realm_dir}")
        print(f"   Realm ID: {realm_id}")
        print(f"   Bearer Key: {bearer_key}")
        print(f"\n📝 Next steps:")
        print(f"   1. cd {realm_dir}")
        print(f"   2. python te_po_proxy/bootstrap.py")
        print(f"   3. python te_po_proxy/main.py")
        return True

    def _copy_template(self, target_dir: Path) -> bool:
        """Copy template directory."""
        try:
            if target_dir.exists():
                print(f"⚠️  Directory {target_dir} already exists")
                response = input("   Overwrite? (y/n): ").strip().lower()
                if response != 'y':
                    return False
                shutil.rmtree(target_dir)

            shutil.copytree(self.template_dir, target_dir)
            print(f"✅ Template copied to {target_dir}")
            return True
        except Exception as e:
            print(f"❌ Failed to copy template: {e}")
            return False

    def _write_env(
        self,
        realm_dir: Path,
        realm_id: str,
        realm_name: str,
        te_po_url: str,
        bearer_key: str,
    ) -> bool:
        """Write .env file."""
        try:
            env_content = f"""# Realm Configuration
REALM_ID={realm_id}
REALM_NAME={realm_name}
TE_PO_URL={te_po_url}
BEARER_KEY={bearer_key}

# Frontend
VITE_API_URL=http://localhost:8000

# Python
PYTHON_VERSION=3.12
"""

            env_file = realm_dir / ".env"
            env_file.write_text(env_content)
            print(f"✅ .env created")
            return True
        except Exception as e:
            print(f"❌ Failed to write .env: {e}")
            return False

    def _write_manifest(
        self,
        realm_dir: Path,
        realm_id: str,
        realm_name: str,
        te_po_url: str,
    ) -> bool:
        """Write realm_manifest.json."""
        try:
            manifest = {
                "realm_id": realm_id,
                "display_name": realm_name,
                "te_po_url": te_po_url,
                "auth_mode": "bearer",
                "features": {
                    "vector_search": True,
                    "pipeline": True,
                    "kaitiaki": False,
                    "memory": True,
                },
                "created_at": datetime.now().isoformat() + "Z",
                "version": "1.0.0",
            }

            manifest_file = realm_dir / "mauri" / "realm_manifest.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)

            print(f"✅ realm_manifest.json created")
            return True
        except Exception as e:
            print(f"❌ Failed to write manifest: {e}")
            return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate a new Awa Network realm"
    )
    parser.add_argument(
        "--realm-id",
        required=True,
        help="Realm ID (e.g., 'cards', 'translator')",
    )
    parser.add_argument(
        "--realm-name",
        required=True,
        help="Display name (e.g., 'Cards Realm')",
    )
    parser.add_argument(
        "--te-po-url",
        required=True,
        help="Main Te Pó backend URL (e.g., 'https://te-po.example.com')",
    )
    parser.add_argument(
        "--bearer-key",
        help="Bearer token (auto-generated if not provided)",
    )

    args = parser.parse_args()

    generator = RealmGenerator()
    success = generator.generate(
        realm_id=args.realm_id,
        realm_name=args.realm_name,
        te_po_url=args.te_po_url,
        bearer_key=args.bearer_key,
    )

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
