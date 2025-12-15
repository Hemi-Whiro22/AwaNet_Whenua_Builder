"""
Te Hau Branch Command

Manage seeds and branches for realm evolution.
"""

import click
import json
from pathlib import Path
from typing import Optional

from te_hau.core.fs import get_projects_path, realm_exists
from te_hau.core.branching import (
    SeedRegistry,
    BranchManager,
    clone_seed,
    promote_to_seed,
    get_lineage
)


@click.group()
def cmd_branch():
    """Seed and branch management for realm evolution."""
    pass


@cmd_branch.command("seeds")
@click.option('--json-output', 'json_out', is_flag=True, help='Output as JSON')
def cmd_list_seeds(json_out: bool):
    """List all registered seeds.
    
    Examples:
        tehau branch seeds
        tehau branch seeds --json-output
    """
    registry = SeedRegistry()
    seeds = registry.list_seeds()
    
    if json_out:
        click.echo(json.dumps([s.to_dict() for s in seeds], indent=2))
        return
    
    click.echo("🌱 Registered Seeds:")
    click.echo("")
    
    if not seeds:
        click.echo("   (none)")
        click.echo("")
        click.echo("Create a seed from an existing realm:")
        click.echo("   tehau branch promote <realm> --name <seed_name>")
        return
    
    for seed in seeds:
        click.echo(f"   • {seed.seed_name} v{seed.version}")
        if seed.description:
            click.echo(f"     {seed.description}")
        click.echo(f"     Files: {len(seed.files)}, Placeholders: {len(seed.placeholders)}")
        click.echo("")


@cmd_branch.command("clone")
@click.argument('seed_name')
@click.argument('realm_name')
@click.option('--var', '-v', multiple=True, help='Variable in KEY=VALUE format')
def cmd_clone_seed(seed_name: str, realm_name: str, var: tuple):
    """Clone a seed to create a new realm.
    
    SEED_NAME: Name of the seed to clone
    REALM_NAME: Name for the new realm
    
    Examples:
        tehau branch clone seed_realm_v1 my-project
        tehau branch clone seed_realm_v1 my-project -v GLYPH_COLOR=#1d64f2
    """
    registry = SeedRegistry()
    seed = registry.get(seed_name)
    
    if not seed:
        raise click.ClickException(f"Seed '{seed_name}' not found")
    
    target_path = get_projects_path() / realm_name
    
    if target_path.exists():
        raise click.ClickException(f"Realm '{realm_name}' already exists")
    
    # Parse variables
    variables = {'REALM_NAME': realm_name}
    for v in var:
        if '=' in v:
            key, value = v.split('=', 1)
            variables[key] = value
    
    # Clone
    click.echo(f"🌱 Cloning seed '{seed_name}'...")
    
    branch = clone_seed(seed_name, target_path, variables, registry)
    
    click.echo(f"✅ Created realm '{realm_name}' from seed")
    click.echo(f"   Branch: {branch.branch_name}")
    click.echo(f"   Location: {target_path}")


@cmd_branch.command("info")
@click.argument('realm_name')
def cmd_branch_info(realm_name: str):
    """Show branch information for a realm.
    
    REALM_NAME: Name of the realm
    
    Examples:
        tehau branch info my-project
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    branch_manager = BranchManager(project_path)
    
    if not branch_manager.branch:
        click.echo(f"🌿 Realm '{realm_name}' has no branch information")
        click.echo("")
        click.echo("This realm may have been created without seed tracking.")
        return
    
    branch = branch_manager.branch
    
    click.echo(f"🌿 Branch: {branch.branch_name}")
    click.echo("")
    click.echo(f"   Parent seed: {branch.parent_seed}")
    click.echo(f"   Realm: {branch.realm_name}")
    click.echo(f"   Created: {branch.created_at.strftime('%Y-%m-%d %H:%M')}")
    click.echo(f"   Glyph: {branch.glyph_at_creation}")
    
    if branch.added_capabilities:
        click.echo("")
        click.echo("   Capabilities:")
        for cap in branch.added_capabilities:
            click.echo(f"      + {cap}")
    
    if branch.env_overrides:
        click.echo("")
        click.echo("   Environment overrides:")
        for key, val in branch.env_overrides.items():
            click.echo(f"      {key}={val}")
    
    if branch.toolchain_map:
        click.echo("")
        click.echo("   Toolchain:")
        for tool, impl in branch.toolchain_map.items():
            click.echo(f"      {tool} → {impl}")
    
    if branch.promoted_to:
        click.echo("")
        click.echo(f"   ⭐ Promoted to seed: {branch.promoted_to}")


@cmd_branch.command("promote")
@click.argument('realm_name')
@click.option('--name', '-n', required=True, help='Name for the new seed')
@click.option('--version', '-v', default='1.0.0', help='Seed version')
@click.option('--description', '-d', help='Seed description')
def cmd_promote(realm_name: str, name: str, version: str, description: Optional[str]):
    """Promote a realm to a new seed.
    
    REALM_NAME: Name of the realm to promote
    
    The realm must be sealed before promotion.
    
    Examples:
        tehau branch promote my-project --name seed_my_project_v1
        tehau branch promote my-project -n seed_my_v1 -v 2.0.0 -d "Production ready"
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    
    click.echo(f"⭐ Promoting '{realm_name}' to seed '{name}'...")
    
    try:
        seed = promote_to_seed(
            project_path,
            name,
            version=version,
            description=description
        )
        
        click.echo(f"✅ Created seed '{seed.seed_name}' v{seed.version}")
        click.echo(f"   Files: {len(seed.files)}")
        click.echo(f"   Checksum: {seed.checksum[:16]}...")
        
    except ValueError as e:
        raise click.ClickException(str(e))


@cmd_branch.command("add-capability")
@click.argument('realm_name')
@click.argument('capability')
def cmd_add_capability(realm_name: str, capability: str):
    """Add a capability to a realm branch.
    
    REALM_NAME: Name of the realm
    CAPABILITY: Capability identifier
    
    Examples:
        tehau branch add-capability my-project translator_module
        tehau branch add-capability my-project research_tools
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    branch_manager = BranchManager(project_path)
    
    if not branch_manager.branch:
        raise click.ClickException("Realm has no branch information")
    
    branch_manager.add_capability(capability)
    
    click.echo(f"✅ Added capability: {capability}")


@cmd_branch.command("set-toolchain")
@click.argument('realm_name')
@click.argument('tool')
@click.argument('implementation')
def cmd_set_toolchain(realm_name: str, tool: str, implementation: str):
    """Set a toolchain implementation for a realm.
    
    REALM_NAME: Name of the realm
    TOOL: Tool name (e.g., ocr, embedding)
    IMPLEMENTATION: Implementation to use
    
    Examples:
        tehau branch set-toolchain my-project ocr ruru
        tehau branch set-toolchain my-project embedding openai_3_large
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    branch_manager = BranchManager(project_path)
    
    if not branch_manager.branch:
        raise click.ClickException("Realm has no branch information")
    
    branch_manager.set_toolchain(tool, implementation)
    
    click.echo(f"✅ Set toolchain: {tool} → {implementation}")


@cmd_branch.command("lineage")
@click.argument('realm_name')
def cmd_lineage(realm_name: str):
    """Show the lineage (ancestry) of a realm.
    
    REALM_NAME: Name of the realm
    
    Examples:
        tehau branch lineage my-project
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    lineage = get_lineage(project_path)
    
    click.echo(f"🌳 Lineage: {realm_name}")
    click.echo("")
    
    if not lineage:
        click.echo("   (no lineage information)")
        return
    
    for i, entry in enumerate(lineage):
        prefix = "└──" if i == len(lineage) - 1 else "├──"
        indent = "   " * i
        
        if entry['type'] == 'branch':
            click.echo(f"{indent}{prefix} 🌿 {entry['name']}")
            click.echo(f"{indent}    Created: {entry['created_at'][:10]}")
            click.echo(f"{indent}    Glyph: {entry['glyph']}")
        else:
            click.echo(f"{indent}{prefix} 🌱 {entry['name']} v{entry.get('version', '?')}")
            click.echo(f"{indent}    Created: {entry['created_at'][:10]}")


@cmd_branch.command("history")
@click.argument('realm_name')
@click.option('--limit', '-n', type=int, default=10, help='Number of mutations to show')
def cmd_history(realm_name: str, limit: int):
    """Show mutation history for a realm branch.
    
    REALM_NAME: Name of the realm
    
    Examples:
        tehau branch history my-project
        tehau branch history my-project --limit 20
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    branch_manager = BranchManager(project_path)
    
    if not branch_manager.branch:
        raise click.ClickException("Realm has no branch information")
    
    mutations = branch_manager.branch.mutations[-limit:]
    
    click.echo(f"📜 Mutation History: {realm_name}")
    click.echo("")
    
    if not mutations:
        click.echo("   (no mutations)")
        return
    
    for mutation in reversed(mutations):
        timestamp = mutation.get('timestamp', '')[:16]
        mtype = mutation.get('type', 'unknown')
        desc = mutation.get('description', '')
        
        type_emoji = {
            'capability_added': '➕',
            'env_override': '⚙️',
            'toolchain_change': '🔧'
        }.get(mtype, '📝')
        
        click.echo(f"   {type_emoji} [{timestamp}] {desc}")
