"""
Te Hau Glyph Command

Manage realm glyphs and visual identity.
"""

import click
import json
from pathlib import Path
from datetime import datetime

from te_hau.core.fs import get_projects_path, realm_exists
from te_hau.mauri.glyph import (
    generate_glyph_color,
    generate_glyph_manifest,
    create_glyph_svg,
    derive_lineage_colors
)


@click.command()
@click.argument('realm_name')
@click.option('--color', '-c', help='Hex color for glyph')
@click.option('--regenerate', '-r', is_flag=True, help='Regenerate glyph')
@click.option('--svg', is_flag=True, help='Generate SVG file')
@click.option('--show', is_flag=True, help='Show current glyph')
def cmd_glyph(realm_name: str, color: str, regenerate: bool, svg: bool, show: bool):
    """Manage a realm's visual glyph.
    
    REALM_NAME: Name of the realm
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    mauri_dir = project_path / "mauri"
    glyph_path = mauri_dir / "glyph_manifest.json"
    
    if show:
        show_glyph(glyph_path, realm_name)
        return
    
    if svg:
        generate_svg_file(project_path, realm_name, glyph_path)
        return
    
    if regenerate or not glyph_path.exists():
        generate_new_glyph(project_path, realm_name, color)
        return
    
    if color:
        update_glyph_color(glyph_path, color)
        return
    
    # Default: show glyph
    show_glyph(glyph_path, realm_name)


def show_glyph(glyph_path: Path, realm_name: str):
    """Display current glyph information."""
    
    click.echo(f"🎨 Glyph: {realm_name}")
    click.echo("")
    
    if not glyph_path.exists():
        click.echo("No glyph configured.")
        click.echo("")
        click.echo("Generate one:")
        click.echo(f"  tehau glyph {realm_name} --regenerate")
        return
    
    with open(glyph_path) as f:
        glyph = json.load(f)
    
    primary = glyph.get('primary', '#888888')
    click.echo(f"Primary color: {primary}")
    
    # Show color preview (using ANSI if terminal supports it)
    try:
        r, g, b = int(primary[1:3], 16), int(primary[3:5], 16), int(primary[5:7], 16)
        click.echo(f"Preview: \033[48;2;{r};{g};{b}m     \033[0m")
    except:
        pass
    
    if 'derived' in glyph:
        click.echo("")
        click.echo("Derived colors:")
        for name, hex_color in glyph['derived'].items():
            click.echo(f"  {name}: {hex_color}")
    
    if 'parent' in glyph:
        click.echo("")
        click.echo(f"Parent glyph: {glyph['parent']}")
    
    if 'generated_at' in glyph:
        click.echo("")
        click.echo(f"Generated: {glyph['generated_at'][:10]}")


def generate_new_glyph(project_path: Path, realm_name: str, color: str = None):
    """Generate a new glyph for the realm."""
    
    click.echo(f"✨ Generating glyph for: {realm_name}")
    click.echo("")
    
    # Get or generate color
    if not color:
        color = generate_glyph_color(realm_name)
        click.echo(f"Generated color: {color}")
    else:
        # Validate color
        if not color.startswith('#') or len(color) != 7:
            raise click.ClickException(
                "Color must be hex format (#RRGGBB)"
            )
        click.echo(f"Using color: {color}")
    
    # Check for parent realm (lineage)
    parent_glyph = None
    realm_lock = project_path / "mauri" / "realm_lock.json"
    
    if realm_lock.exists():
        with open(realm_lock) as f:
            lock = json.load(f)
        
        parent_realm = lock.get('parent_realm')
        if parent_realm:
            parent_path = get_projects_path() / parent_realm / "mauri" / "glyph_manifest.json"
            if parent_path.exists():
                with open(parent_path) as f:
                    parent_glyph = json.load(f).get('primary')
                click.echo(f"Inheriting from parent: {parent_realm}")
    
    # Generate manifest
    manifest = generate_glyph_manifest(realm_name, color, parent_glyph)
    
    # Save
    glyph_path = project_path / "mauri" / "glyph_manifest.json"
    with open(glyph_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    click.echo("")
    click.echo("✓ Glyph manifest saved")
    
    # Show preview
    try:
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        click.echo(f"Preview: \033[48;2;{r};{g};{b}m     \033[0m")
    except:
        pass


def update_glyph_color(glyph_path: Path, color: str):
    """Update glyph color."""
    
    if not color.startswith('#') or len(color) != 7:
        raise click.ClickException("Color must be hex format (#RRGGBB)")
    
    if not glyph_path.exists():
        raise click.ClickException("No glyph exists. Use --regenerate first")
    
    with open(glyph_path) as f:
        glyph = json.load(f)
    
    old_color = glyph.get('primary', '')
    glyph['primary'] = color
    glyph['derived'] = derive_lineage_colors(color)
    glyph['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    
    with open(glyph_path, 'w') as f:
        json.dump(glyph, f, indent=2)
    
    click.echo(f"✓ Updated glyph color: {old_color} → {color}")


def generate_svg_file(project_path: Path, realm_name: str, glyph_path: Path):
    """Generate SVG file for the glyph."""
    
    if not glyph_path.exists():
        raise click.ClickException("No glyph configured. Run with --regenerate first")
    
    with open(glyph_path) as f:
        glyph = json.load(f)
    
    color = glyph.get('primary', '#888888')
    
    # Generate SVG
    svg_content = create_glyph_svg(realm_name, color)
    
    # Save
    assets_dir = project_path / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    svg_path = assets_dir / f"{realm_name}_glyph.svg"
    with open(svg_path, 'w') as f:
        f.write(svg_content)
    
    click.echo(f"✓ SVG saved to: {svg_path}")


@click.command()
@click.argument('parent_realm')
@click.argument('child_realm')
def cmd_glyph_inherit(parent_realm: str, child_realm: str):
    """Inherit glyph lineage from parent realm.
    
    PARENT_REALM: Name of the parent realm
    CHILD_REALM: Name of the child realm
    """
    if not realm_exists(parent_realm):
        raise click.ClickException(f"Parent realm '{parent_realm}' not found")
    
    if not realm_exists(child_realm):
        raise click.ClickException(f"Child realm '{child_realm}' not found")
    
    parent_path = get_projects_path() / parent_realm / "mauri" / "glyph_manifest.json"
    child_path = get_projects_path() / child_realm / "mauri" / "glyph_manifest.json"
    
    if not parent_path.exists():
        raise click.ClickException(f"Parent realm has no glyph")
    
    with open(parent_path) as f:
        parent_glyph = json.load(f)
    
    parent_color = parent_glyph.get('primary', '#888888')
    
    # Generate child glyph with parent lineage
    child_manifest = generate_glyph_manifest(child_realm, None, parent_color)
    child_manifest['parent'] = parent_realm
    child_manifest['parent_color'] = parent_color
    
    child_path.parent.mkdir(parents=True, exist_ok=True)
    with open(child_path, 'w') as f:
        json.dump(child_manifest, f, indent=2)
    
    click.echo(f"✓ {child_realm} glyph inherits from {parent_realm}")
    click.echo(f"  Parent: {parent_color}")
    click.echo(f"  Child: {child_manifest['primary']}")
