"""
Te Hau Context Command

Manage context and realm switching.
"""

import click
import json
from pathlib import Path
from datetime import datetime

from te_hau.core.fs import get_awanet_path, get_projects_path, realm_exists


@click.command()
@click.argument('realm_name', required=False)
@click.option('--list', '-l', 'list_realms', is_flag=True, help='List all realms')
@click.option('--current', '-c', is_flag=True, help='Show current context')
@click.option('--global', '-g', 'use_global', is_flag=True, help='Switch to global context')
@click.option('--export', '-e', 'export_path', type=click.Path(), help='Export context to file')
@click.option('--format', 'export_format', type=click.Choice(['json', 'yaml', 'markdown']),
              default='json', help='Export format')
def cmd_context(realm_name: str, list_realms: bool, current: bool, use_global: bool,
                export_path: str, export_format: str):
    """Switch context between realms.
    
    REALM_NAME: Name of the realm to switch to (optional)
    """
    awanet_path = get_awanet_path()
    context_file = awanet_path / "current_context.json"
    
    if current:
        show_current_context(context_file)
        return
    
    if list_realms:
        list_all_realms()
        return
    
    if use_global:
        switch_to_global(context_file)
        return
    
    if export_path:
        export_context(realm_name, export_path, export_format)
        return
    
    if realm_name:
        switch_to_realm(realm_name, context_file)
        return
    
    # Default: show current context
    show_current_context(context_file)


def show_current_context(context_file: Path):
    """Display current context information."""
    
    click.echo("🎯 Current Context")
    click.echo("")
    
    if not context_file.exists():
        click.echo("No context set. Operating in global mode.")
        click.echo("")
        click.echo("Switch to a realm:")
        click.echo("  tehau context <realm_name>")
        return
    
    with open(context_file) as f:
        ctx = json.load(f)
    
    if ctx.get('type') == 'global':
        click.echo("Mode: Global (awanet)")
        click.echo("Vector namespace: global::awanet")
    else:
        realm = ctx.get('realm')
        click.echo(f"Mode: Realm")
        click.echo(f"Realm: {realm}")
        click.echo(f"Vector namespace: realm::{realm}")
        
        if 'switched_at' in ctx:
            click.echo(f"Since: {ctx['switched_at'][:19]}")
        
        # Show realm info
        project_path = get_projects_path() / realm
        realm_lock = project_path / "mauri" / "realm_lock.json"
        
        if realm_lock.exists():
            with open(realm_lock) as f:
                lock = json.load(f)
            
            if lock.get('seal'):
                click.echo("Status: 🔏 Sealed")
            else:
                click.echo("Status: 🔓 Unsealed")
            
            if lock.get('kaitiaki'):
                click.echo(f"Kaitiaki: {lock['kaitiaki']}")


def list_all_realms():
    """List all available realms."""
    
    click.echo("📂 Available Realms")
    click.echo("")
    
    projects_path = get_projects_path()
    
    if not projects_path.exists():
        click.echo("No realms found.")
        click.echo("Create one with: tehau new <realm_name>")
        return
    
    realms = []
    for d in projects_path.iterdir():
        if d.is_dir():
            realm_lock = d / "mauri" / "realm_lock.json"
            if realm_lock.exists():
                with open(realm_lock) as f:
                    lock = json.load(f)
                realms.append({
                    'name': d.name,
                    'sealed': bool(lock.get('seal')),
                    'kaitiaki': lock.get('kaitiaki', ''),
                    'created': lock.get('created_at', '')
                })
            else:
                realms.append({
                    'name': d.name,
                    'sealed': False,
                    'kaitiaki': '',
                    'created': ''
                })
    
    if not realms:
        click.echo("No realms found.")
        return
    
    # Current context
    awanet_path = get_awanet_path()
    context_file = awanet_path / "current_context.json"
    current_realm = None
    
    if context_file.exists():
        with open(context_file) as f:
            ctx = json.load(f)
        current_realm = ctx.get('realm')
    
    for realm in sorted(realms, key=lambda r: r['name']):
        marker = "●" if realm['name'] == current_realm else "○"
        seal = "🔏" if realm['sealed'] else "🔓"
        
        line = f"  {marker} {realm['name']} {seal}"
        
        if realm['kaitiaki']:
            line += f" ({realm['kaitiaki']})"
        
        click.echo(line)
    
    click.echo("")
    click.echo("● = active context")


def switch_to_realm(realm_name: str, context_file: Path):
    """Switch context to a specific realm."""
    
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    realm_lock = project_path / "mauri" / "realm_lock.json"
    
    # Build context
    ctx = {
        'type': 'realm',
        'realm': realm_name,
        'path': str(project_path),
        'vector_namespace': f'realm::{realm_name}',
        'switched_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    if realm_lock.exists():
        with open(realm_lock) as f:
            lock = json.load(f)
        ctx['realm_id'] = lock.get('realm_id')
        ctx['kaitiaki'] = lock.get('kaitiaki')
    
    # Save context
    context_file.parent.mkdir(parents=True, exist_ok=True)
    with open(context_file, 'w') as f:
        json.dump(ctx, f, indent=2)
    
    click.echo(f"✓ Switched to realm: {realm_name}")
    click.echo(f"  Namespace: realm::{realm_name}")


def switch_to_global(context_file: Path):
    """Switch to global context."""
    
    ctx = {
        'type': 'global',
        'realm': None,
        'path': None,
        'vector_namespace': 'global::awanet',
        'switched_at': datetime.utcnow().isoformat() + 'Z'
    }
    
    context_file.parent.mkdir(parents=True, exist_ok=True)
    with open(context_file, 'w') as f:
        json.dump(ctx, f, indent=2)
    
    click.echo("✓ Switched to global context")
    click.echo("  Namespace: global::awanet")


def get_current_context() -> dict:
    """Get the current context (for use by other commands)."""
    
    awanet_path = get_awanet_path()
    context_file = awanet_path / "current_context.json"
    
    if not context_file.exists():
        return {
            'type': 'global',
            'realm': None,
            'vector_namespace': 'global::awanet'
        }
    
    with open(context_file) as f:
        return json.load(f)


def export_context(realm_name: str, export_path: str, export_format: str):
    """Export realm context to file for AI/LLM consumption."""
    
    # Determine realm to export
    if realm_name:
        if not realm_exists(realm_name):
            raise click.ClickException(f"Realm '{realm_name}' not found")
        target_realm = realm_name
    else:
        ctx = get_current_context()
        if ctx.get('type') == 'global' or not ctx.get('realm'):
            raise click.ClickException(
                "No realm specified and not in realm context. "
                "Use: tehau context --export <path> <realm_name>"
            )
        target_realm = ctx['realm']
    
    click.echo(f"📤 Exporting context for realm: {target_realm}")
    
    project_path = get_projects_path() / target_realm
    
    # Gather all context
    context_data = {
        'realm': target_realm,
        'exported_at': datetime.utcnow().isoformat() + 'Z',
        'mauri': {},
        'kaitiaki': [],
        'docs': [],
        'glossary': [],
        'whakapapa': {}
    }
    
    # Load mauri files
    mauri_path = project_path / "mauri"
    if mauri_path.exists():
        for json_file in mauri_path.glob("*.json"):
            try:
                with open(json_file) as f:
                    context_data['mauri'][json_file.stem] = json.load(f)
            except Exception:
                pass
    
    # Load kaitiaki
    kaitiaki_path = project_path / ".kaitiaki"
    if kaitiaki_path.exists():
        for json_file in kaitiaki_path.glob("*.json"):
            try:
                with open(json_file) as f:
                    context_data['kaitiaki'].append(json.load(f))
            except Exception:
                pass
    
    # Load docs
    docs_path = project_path / "docs"
    if docs_path.exists():
        for md_file in docs_path.glob("**/*.md"):
            try:
                content = md_file.read_text()
                context_data['docs'].append({
                    'path': str(md_file.relative_to(project_path)),
                    'content': content[:5000]  # Truncate long docs
                })
            except Exception:
                pass
    
    # Load glossary
    glossary_file = mauri_path / "glossary.json"
    if glossary_file.exists():
        try:
            with open(glossary_file) as f:
                context_data['glossary'] = json.load(f).get('terms', [])
        except Exception:
            pass
    
    # Write export
    export_file = Path(export_path)
    export_file.parent.mkdir(parents=True, exist_ok=True)
    
    if export_format == 'json':
        with open(export_file, 'w') as f:
            json.dump(context_data, f, indent=2)
    
    elif export_format == 'yaml':
        try:
            import yaml
            with open(export_file, 'w') as f:
                yaml.dump(context_data, f, default_flow_style=False)
        except ImportError:
            raise click.ClickException("PyYAML required for YAML export. Install with: pip install pyyaml")
    
    elif export_format == 'markdown':
        md_content = generate_markdown_context(context_data)
        with open(export_file, 'w') as f:
            f.write(md_content)
    
    click.echo(f"✓ Context exported to: {export_path}")
    click.echo(f"  Format: {export_format}")
    click.echo(f"  Kaitiaki: {len(context_data['kaitiaki'])}")
    click.echo(f"  Docs: {len(context_data['docs'])}")
    click.echo(f"  Glossary terms: {len(context_data['glossary'])}")


def generate_markdown_context(context_data: dict) -> str:
    """Generate markdown representation of context."""
    
    lines = [
        f"# Realm Context: {context_data['realm']}",
        "",
        f"Exported: {context_data['exported_at']}",
        "",
        "## Overview",
        ""
    ]
    
    # Realm info
    if 'realm_lock' in context_data['mauri']:
        lock = context_data['mauri']['realm_lock']
        lines.extend([
            f"- **Realm ID**: {lock.get('realm_id', 'N/A')}",
            f"- **Kaitiaki**: {lock.get('kaitiaki', 'N/A')}",
            f"- **Created**: {lock.get('created_at', 'N/A')[:10]}",
            ""
        ])
    
    # Kaitiaki
    if context_data['kaitiaki']:
        lines.extend([
            "## Kaitiaki (Guardians)",
            ""
        ])
        for kai in context_data['kaitiaki']:
            lines.extend([
                f"### {kai.get('name', 'Unknown')}",
                "",
                f"- **Stage**: {kai.get('stage', 'pēpi')}",
                f"- **Purpose**: {kai.get('purpose', 'N/A')}",
                ""
            ])
    
    # Glossary
    if context_data['glossary']:
        lines.extend([
            "## Glossary",
            "",
            "| Term | Translation | Context |",
            "|------|-------------|---------|"
        ])
        for term in context_data['glossary'][:20]:
            lines.append(
                f"| {term.get('maori', '')} | {term.get('english', '')} | {term.get('context', '')} |"
            )
        lines.append("")
    
    # Docs summary
    if context_data['docs']:
        lines.extend([
            "## Documentation",
            ""
        ])
        for doc in context_data['docs'][:10]:
            lines.extend([
                f"### {doc['path']}",
                "",
                doc['content'][:1000] + ("..." if len(doc['content']) > 1000 else ""),
                ""
            ])
    
    return "\n".join(lines)
