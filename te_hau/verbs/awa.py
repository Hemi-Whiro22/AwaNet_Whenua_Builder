"""
Te Hau Awa Command

Inter-realm communication and whakapapa management.
"""

import click
import json
import asyncio
from pathlib import Path
from typing import Optional

from te_hau.core.fs import get_projects_path, realm_exists
from te_hau.awa.whakapapa import get_whakapapa_graph


@click.group()
def cmd_awa():
    """Inter-realm communication (Awa - the river)."""
    pass


@cmd_awa.command("register")
@click.argument('realm_name')
@click.option('--parent', '-p', help='Parent realm')
@click.option('--color', '-c', help='Glyph color')
def cmd_register(realm_name: str, parent: Optional[str], color: Optional[str]):
    """Register a realm in the whakapapa graph.
    
    REALM_NAME: Name of the realm to register
    
    Examples:
        tehau awa register my-project
        tehau awa register child-project --parent my-project
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    # Load realm glyph color if not specified
    if not color:
        glyph_path = get_projects_path() / realm_name / "mauri" / "glyph_manifest.json"
        if glyph_path.exists():
            with open(glyph_path) as f:
                glyph = json.load(f)
            color = glyph.get('primary', '#888888')
        else:
            color = '#888888'
    
    graph = get_whakapapa_graph()
    
    # Validate parent
    parent_id = None
    if parent:
        if parent not in graph.nodes:
            raise click.ClickException(f"Parent realm '{parent}' not registered")
        parent_id = parent
    
    try:
        node = graph.add_realm(
            realm_id=realm_name,
            realm_name=realm_name,
            parent_id=parent_id,
            glyph_color=color
        )
        
        click.echo(f"✅ Registered '{realm_name}' in whakapapa")
        if parent:
            click.echo(f"   Parent: {parent}")
        click.echo(f"   Glyph: {color}")
        
    except ValueError as e:
        raise click.ClickException(str(e))


@cmd_awa.command("link")
@click.argument('source_realm')
@click.argument('target_realm')
@click.option('--type', 'link_type', type=click.Choice(['fork', 'merge', 'reference', 'trust']),
              default='reference', help='Link type')
@click.option('--permission', '-p', multiple=True, help='Permissions')
@click.option('--bidirectional', '-b', is_flag=True, help='Bidirectional link')
def cmd_link(
    source_realm: str,
    target_realm: str,
    link_type: str,
    permission: tuple,
    bidirectional: bool
):
    """Create a link between realms.
    
    SOURCE_REALM: Source realm
    TARGET_REALM: Target realm
    
    Link types:
        fork - Source forked from target
        merge - Source merged with target
        reference - Source references target
        trust - Source trusts target (grants access)
    
    Examples:
        tehau awa link my-project other-project --type reference
        tehau awa link my-project trusted-project --type trust -p read -p query
    """
    graph = get_whakapapa_graph()
    
    if source_realm not in graph.nodes:
        raise click.ClickException(f"Source realm '{source_realm}' not registered")
    if target_realm not in graph.nodes:
        raise click.ClickException(f"Target realm '{target_realm}' not registered")
    
    permissions = set(permission) if permission else {'*'}
    
    try:
        link = graph.add_link(
            source_id=source_realm,
            target_id=target_realm,
            link_type=link_type,
            permissions=permissions,
            bidirectional=bidirectional
        )
        
        direction = "⟷" if bidirectional else "→"
        click.echo(f"✅ Linked: {source_realm} {direction} {target_realm}")
        click.echo(f"   Type: {link_type}")
        click.echo(f"   Permissions: {', '.join(permissions)}")
        
    except ValueError as e:
        raise click.ClickException(str(e))


@cmd_awa.command("unlink")
@click.argument('source_realm')
@click.argument('target_realm')
@click.option('--type', 'link_type', help='Link type to remove (all if not specified)')
def cmd_unlink(source_realm: str, target_realm: str, link_type: Optional[str]):
    """Remove a link between realms.
    
    Examples:
        tehau awa unlink my-project other-project
        tehau awa unlink my-project other-project --type trust
    """
    graph = get_whakapapa_graph()
    graph.remove_link(source_realm, target_realm, link_type)
    
    click.echo(f"✅ Removed link: {source_realm} → {target_realm}")


@cmd_awa.command("tree")
@click.option('--root', '-r', help='Root realm to start from')
@click.option('--json-output', 'json_out', is_flag=True, help='Output as JSON')
def cmd_tree(root: Optional[str], json_out: bool):
    """Show the realm whakapapa tree.
    
    Examples:
        tehau awa tree
        tehau awa tree --root my-project
        tehau awa tree --json-output
    """
    graph = get_whakapapa_graph()
    
    if json_out:
        tree = graph.get_tree(root)
        click.echo(json.dumps(tree, indent=2))
        return
    
    click.echo("🌳 Whakapapa Tree")
    click.echo("")
    
    if not graph.nodes:
        click.echo("   (no realms registered)")
        click.echo("")
        click.echo("Register a realm:")
        click.echo("   tehau awa register <realm>")
        return
    
    click.echo(graph.visualize())


@cmd_awa.command("info")
@click.argument('realm_name')
def cmd_info(realm_name: str):
    """Show information about a realm in the whakapapa.
    
    REALM_NAME: Name of the realm
    
    Examples:
        tehau awa info my-project
    """
    graph = get_whakapapa_graph()
    
    if realm_name not in graph.nodes:
        raise click.ClickException(f"Realm '{realm_name}' not registered")
    
    node = graph.nodes[realm_name]
    
    click.echo(f"🌿 {node.realm_name}")
    click.echo("")
    click.echo(f"   ID: {node.realm_id}")
    click.echo(f"   Glyph: {node.glyph_color}")
    click.echo(f"   Created: {node.created_at.strftime('%Y-%m-%d %H:%M')}")
    
    # Parent
    parent = graph.get_parent(realm_name)
    if parent:
        click.echo(f"   Parent: {parent.realm_name}")
    
    # Children
    children = graph.get_children(realm_name)
    if children:
        click.echo(f"   Children: {', '.join(c.realm_name for c in children)}")
    
    # Siblings
    siblings = graph.get_siblings(realm_name)
    if siblings:
        click.echo(f"   Siblings: {', '.join(s.realm_name for s in siblings)}")
    
    # Links
    linked = graph.get_linked(realm_name)
    if linked:
        click.echo("")
        click.echo("   Links:")
        for link in graph.links:
            if link.source_id == realm_name:
                direction = "⟷" if link.bidirectional else "→"
                click.echo(f"      {direction} {link.target_id} ({link.link_type})")


@cmd_awa.command("check-access")
@click.argument('source_realm')
@click.argument('target_realm')
@click.option('--permission', '-p', help='Specific permission to check')
def cmd_check_access(source_realm: str, target_realm: str, permission: Optional[str]):
    """Check if one realm can access another.
    
    Examples:
        tehau awa check-access my-project other-project
        tehau awa check-access my-project other-project -p read
    """
    graph = get_whakapapa_graph()
    
    if source_realm not in graph.nodes:
        raise click.ClickException(f"Realm '{source_realm}' not registered")
    if target_realm not in graph.nodes:
        raise click.ClickException(f"Realm '{target_realm}' not registered")
    
    can_access = graph.can_access(source_realm, target_realm, permission)
    
    if can_access:
        click.echo(f"✅ '{source_realm}' CAN access '{target_realm}'")
        if permission:
            click.echo(f"   Permission: {permission}")
    else:
        click.echo(f"❌ '{source_realm}' CANNOT access '{target_realm}'")
        if permission:
            click.echo(f"   Missing permission: {permission}")


@cmd_awa.command("ancestors")
@click.argument('realm_name')
def cmd_ancestors(realm_name: str):
    """Show ancestors of a realm.
    
    Examples:
        tehau awa ancestors child-project
    """
    graph = get_whakapapa_graph()
    
    if realm_name not in graph.nodes:
        raise click.ClickException(f"Realm '{realm_name}' not registered")
    
    ancestors = graph.get_ancestors(realm_name)
    
    click.echo(f"🌳 Ancestors of {realm_name}")
    click.echo("")
    
    if not ancestors:
        click.echo("   (no ancestors - this is a root realm)")
        return
    
    for i, ancestor in enumerate(ancestors):
        indent = "   " * (i + 1)
        click.echo(f"{indent}↑ {ancestor.realm_name} ({ancestor.glyph_color})")


@cmd_awa.command("descendants")
@click.argument('realm_name')
def cmd_descendants(realm_name: str):
    """Show descendants of a realm.
    
    Examples:
        tehau awa descendants parent-project
    """
    graph = get_whakapapa_graph()
    
    if realm_name not in graph.nodes:
        raise click.ClickException(f"Realm '{realm_name}' not registered")
    
    descendants = graph.get_descendants(realm_name)
    
    click.echo(f"🌱 Descendants of {realm_name}")
    click.echo("")
    
    if not descendants:
        click.echo("   (no descendants)")
        return
    
    for desc in descendants:
        depth = len(graph.get_ancestors(desc.realm_id))
        indent = "   " * depth
        click.echo(f"{indent}↓ {desc.realm_name} ({desc.glyph_color})")
