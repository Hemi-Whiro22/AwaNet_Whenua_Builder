"""
Te Hau New Command

Create a new realm from the project template.
"""

import click
from pathlib import Path
from datetime import datetime

from te_hau.core.fs import (
    copy_tree, write_json, write_env, 
    get_template_path, get_projects_path, realm_exists, ensure_directory
)
from te_hau.core.renderer import render_directory
from te_hau.core.secrets import generate_bearer_token, generate_realm_id
from te_hau.mauri.glyph import generate_glyph_color, generate_glyph_manifest
from te_hau.mauri.seal import seal_realm


@click.command()
@click.argument('realm_name')
@click.option('--glyph', '-g', help='Hex color for realm glyph')
@click.option('--no-seal', is_flag=True, help='Skip sealing (development mode)')
@click.option('--template', '-t', default='default', help='Template to use')
def cmd_new(realm_name: str, glyph: str, no_seal: bool, template: str):
    """Create a new realm project.
    
    REALM_NAME: Name for the new realm (lowercase, underscores)
    """
    # Validate name
    import re
    if not re.match(r'^[a-z][a-z0-9_]{2,31}$', realm_name):
        raise click.ClickException(
            "Realm name must be lowercase, start with letter, "
            "3-32 chars, only letters/numbers/underscores"
        )
    
    # Check if exists
    if realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' already exists")
    
    click.echo(f"🌊 Creating new realm: {realm_name}")
    
    # Generate identifiers
    realm_id = generate_realm_id()
    bearer_token, bearer_hash = generate_bearer_token()
    glyph_color = glyph or generate_glyph_color(realm_name)
    
    click.echo(f"  → Realm ID: {realm_id}")
    click.echo(f"  → Glyph: {glyph_color}")
    
    # Setup paths
    template_path = get_template_path()
    project_path = get_projects_path() / realm_name
    
    # Ensure template exists
    if not template_path.exists():
        click.echo("  ⚠ Template not found, creating minimal structure...")
        create_minimal_realm(project_path, realm_name, realm_id, glyph_color, bearer_token)
    else:
        # Copy and render template
        click.echo("  → Copying template...")
        ensure_directory(project_path)
        
        # Render context
        context = {
            "REALM_NAME": realm_name,
            "REALM_ID": realm_id,
            "BEARER_KEY": bearer_token,
            "GLYPH_COLOR": glyph_color,
            "CREATED_AT": datetime.utcnow().isoformat() + 'Z',
        }
        
        render_directory(template_path, project_path, context)
    
    # Create realm_lock.json
    click.echo("  → Creating mauri files...")
    mauri_path = project_path / "mauri"
    ensure_directory(mauri_path)
    
    realm_lock = {
        "realm_name": realm_name,
        "realm_id": realm_id,
        "locked_kaitiaki": f"{realm_name}_kaitiaki",
        "glyph": glyph_color,
        "origin_seed": "seed_realm_v1",
        "created_at": datetime.utcnow().isoformat() + 'Z',
        "permissions": {
            "vector_access": True,
            "supabase_access": True,
            "translator_module": False,
            "ocr_module": False,
            "cross_realm_query": False
        }
    }
    write_json(mauri_path / "realm_lock.json", realm_lock)
    
    # Create den_manifest.json
    den_manifest = {
        "capabilities": {
            "translation": False,
            "ocr": False,
            "embedding": True,
            "offline_mode": False
        },
        "encoding": {
            "mi_NZ": True,
            "utf8": True,
            "macron_rules": "default"
        },
        "pipelines": {
            "allowed": ["embed"],
            "restricted": ["admin"]
        }
    }
    write_json(mauri_path / "den_manifest.json", den_manifest)
    
    # Create glyph manifest
    glyph_manifest = generate_glyph_manifest(realm_name, glyph_color)
    write_json(mauri_path / "glyph.json", glyph_manifest)
    
    # Create state directory
    ensure_directory(mauri_path / "state")
    
    # Create .env file
    click.echo("  → Creating environment file...")
    env_vars = {
        "REALM_NAME": realm_name,
        "REALM_ID": realm_id,
        "REALM_BEARER_KEY": bearer_token,
        "REALM_GLYPH": glyph_color,
        "# Supabase (fill in)": "",
        "SUPABASE_URL": "",
        "SUPABASE_ANON_KEY": "",
        "# OpenAI (fill in)": "",
        "OPENAI_API_KEY": "",
    }
    write_env(project_path / ".env", env_vars)
    
    # Create config
    config_path = project_path / "config"
    ensure_directory(config_path)
    
    realm_config = {
        "realm_name": realm_name,
        "realm_id": realm_id,
        "glyph_color": glyph_color,
        "version": "1.0.0",
        "vector_namespace": f"realm::{realm_name}",
        "kaitiaki": {
            "name": f"{realm_name}_kaitiaki",
            "evolution_stage": "seed"
        },
        "deployment": {
            "frontend": "cloudflare_pages",
            "backend": "render"
        }
    }
    write_json(config_path / "realm.json", realm_config)
    
    # Seal if requested
    if not no_seal:
        click.echo("  → Sealing realm...")
        seal = seal_realm(project_path)
        click.echo(f"  → Seal: {seal[:32]}...")
    
    click.echo("")
    click.echo(f"✓ Realm '{realm_name}' created successfully!")
    click.echo("")
    click.echo(f"  Location: {project_path}")
    click.echo(f"  Bearer:   {bearer_token[:16]}... (saved in .env)")
    click.echo("")
    click.echo("Next steps:")
    click.echo(f"  cd {project_path}")
    click.echo("  # Edit .env with your Supabase/OpenAI keys")
    click.echo(f"  tehau deploy {realm_name}")


def create_minimal_realm(
    project_path: Path, 
    realm_name: str, 
    realm_id: str,
    glyph_color: str,
    bearer_token: str
):
    """Create minimal realm structure without template."""
    ensure_directory(project_path / "te_ao" / "src")
    ensure_directory(project_path / "te_ao" / "public")
    ensure_directory(project_path / "mini_te_po")
    ensure_directory(project_path / "mauri" / "state")
    ensure_directory(project_path / "config")
    ensure_directory(project_path / "scripts")
    ensure_directory(project_path / "docs")
    
    # Create minimal files
    (project_path / "te_ao" / "src" / ".gitkeep").touch()
    (project_path / "mini_te_po" / "__init__.py").touch()
    
    # Create README
    readme = f"""# {realm_name}

AwaOS Realm created {datetime.utcnow().isoformat()}

## Structure

- `te_ao/` - Frontend UI
- `mini_te_po/` - Backend proxy
- `mauri/` - Identity and state
- `config/` - Configuration
- `scripts/` - Automation scripts
- `docs/` - Documentation

## Getting Started

1. Edit `.env` with your API keys
2. Run `tehau deploy {realm_name}`
"""
    (project_path / "README.md").write_text(readme)
