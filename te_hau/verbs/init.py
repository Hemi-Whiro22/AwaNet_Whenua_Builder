"""
Te Hau Init Command

Initialize the Te Hau environment and user configuration.
"""

import click
from pathlib import Path
from datetime import datetime

from te_hau.core.fs import ensure_directory, write_json, get_user_config_path


@click.command()
def cmd_init():
    """Initialize Te Hau environment.
    
    Creates ~/.awanet configuration directory and initial state.
    """
    config_path = get_user_config_path()
    
    click.echo("🌊 Initializing Te Hau environment...")
    
    # Create config directories
    ensure_directory(config_path)
    ensure_directory(config_path / "logs")
    ensure_directory(config_path / "cache")
    
    # Create initial config
    config_file = config_path / "config.json"
    
    if not config_file.exists():
        initial_config = {
            "version": "0.1.0",
            "initialized_at": datetime.utcnow().isoformat() + 'Z',
            "active_realm": None,
            "backend_url": None,
            "default_glyph_color": None,
            "settings": {
                "auto_seal": True,
                "verbose": False
            }
        }
        write_json(config_file, initial_config)
        click.echo(f"  ✓ Created config at {config_file}")
    else:
        click.echo(f"  → Config already exists at {config_file}")
    
    # Create mauri seed
    mauri_file = config_path / "mauri.json"
    
    if not mauri_file.exists():
        import uuid
        mauri_seed = {
            "global_id": str(uuid.uuid4()),
            "state": "initialized",
            "created_at": datetime.utcnow().isoformat() + 'Z'
        }
        write_json(mauri_file, mauri_seed)
        click.echo(f"  ✓ Created mauri seed")
    
    click.echo("")
    click.echo("✓ Te Hau initialized. Mauri anchored.")
    click.echo("")
    click.echo("Next steps:")
    click.echo("  tehau new <realm_name>    Create a new realm")
    click.echo("  tehau --help              Show all commands")
