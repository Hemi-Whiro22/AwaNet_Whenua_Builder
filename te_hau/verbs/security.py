"""
Te Hau Security Command

Manage tapu (restrictions) and mana (permissions).
"""

import click
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional

from te_hau.core.fs import get_projects_path, realm_exists
from te_hau.core.security import (
    SecurityManager,
    TapuLevel,
    ManaType,
    apply_default_tapu
)


@click.group()
def cmd_security():
    """Security management - tapu and mana."""
    pass


@cmd_security.command("init")
@click.argument('realm_name')
@click.option('--defaults', is_flag=True, default=True, help='Apply default tapu')
def cmd_security_init(realm_name: str, defaults: bool):
    """Initialize security for a realm.
    
    REALM_NAME: Name of the realm
    
    Examples:
        tehau security init my-project
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    manager = SecurityManager(project_path)
    
    if defaults:
        apply_default_tapu(manager)
        click.echo("✅ Applied default tapu declarations")
    
    manager.save()
    click.echo(f"🔐 Security initialized for '{realm_name}'")


@cmd_security.command("tapu")
@click.argument('realm_name')
@click.argument('resource_path')
@click.option('--level', '-l', type=click.Choice(['noa', 'ahi', 'tapu', 'whakahaere']),
              default='tapu', help='Tapu level')
@click.option('--reason', '-r', help='Reason for tapu')
@click.option('--lift', is_flag=True, help='Lift existing tapu')
def cmd_tapu(
    realm_name: str,
    resource_path: str,
    level: str,
    reason: Optional[str],
    lift: bool
):
    """Declare or lift tapu on a resource.
    
    REALM_NAME: Name of the realm
    RESOURCE_PATH: Path to the resource
    
    Tapu levels:
        noa - Unrestricted access
        ahi - Basic restriction
        tapu - Sacred/restricted
        whakahaere - Administrative only
    
    Examples:
        tehau security tapu my-project secrets/ --level whakahaere
        tehau security tapu my-project data.json --level tapu --reason "Sensitive data"
        tehau security tapu my-project public/ --lift
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    manager = SecurityManager(project_path)
    
    if lift:
        manager.lift_tapu(resource_path)
        click.echo(f"✅ Tapu lifted from '{resource_path}'")
        return
    
    level_map = {
        'noa': TapuLevel.NOA,
        'ahi': TapuLevel.AHI,
        'tapu': TapuLevel.TAPU,
        'whakahaere': TapuLevel.WHAKAHAERE
    }
    
    tapu_level = level_map[level]
    manager.declare_tapu(resource_path, tapu_level, reason=reason)
    
    click.echo(f"🔐 Declared {level.upper()} on '{resource_path}'")


@cmd_security.command("mana")
@click.argument('realm_name')
@click.argument('entity_id')
@click.option('--type', 'mana_type', type=click.Choice(['whenua', 'tangata', 'atua']),
              default='tangata', help='Type of mana')
@click.option('--permission', '-p', multiple=True, help='Permissions to grant')
@click.option('--expires', type=int, help='Expiry in days')
@click.option('--revoke', is_flag=True, help='Revoke mana')
def cmd_mana(
    realm_name: str,
    entity_id: str,
    mana_type: str,
    permission: tuple,
    expires: Optional[int],
    revoke: bool
):
    """Grant or revoke mana (authority) to an entity.
    
    REALM_NAME: Name of the realm
    ENTITY_ID: User or service identifier
    
    Mana types:
        whenua - Realm authority (realm admins)
        tangata - User authority (regular users)
        atua - System authority (services/automation)
    
    Examples:
        tehau security mana my-project user@example.com --type tangata -p read -p write
        tehau security mana my-project ci-bot --type atua -p deploy
        tehau security mana my-project user@example.com --revoke
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    manager = SecurityManager(project_path)
    
    type_map = {
        'whenua': ManaType.WHENUA,
        'tangata': ManaType.TANGATA,
        'atua': ManaType.ATUA
    }
    
    if revoke:
        manager.revoke_mana(entity_id, type_map.get(mana_type))
        click.echo(f"✅ Mana revoked from '{entity_id}'")
        return
    
    # Grant mana
    permissions = set(permission) if permission else {'*'}
    expires_at = None
    if expires:
        expires_at = datetime.utcnow() + timedelta(days=expires)
    
    manager.grant_mana(
        entity_id=entity_id,
        mana_type=type_map[mana_type],
        permissions=permissions,
        realm=realm_name,
        expires_at=expires_at
    )
    
    click.echo(f"✅ Granted {mana_type.upper()} mana to '{entity_id}'")
    if permission:
        click.echo(f"   Permissions: {', '.join(permission)}")
    else:
        click.echo("   Permissions: all (*)")
    if expires:
        click.echo(f"   Expires: {expires} days")


@cmd_security.command("check")
@click.argument('realm_name')
@click.argument('entity_id')
@click.argument('resource_path')
def cmd_check(realm_name: str, entity_id: str, resource_path: str):
    """Check if an entity can access a resource.
    
    REALM_NAME: Name of the realm
    ENTITY_ID: User or service identifier
    RESOURCE_PATH: Path to check access for
    
    Examples:
        tehau security check my-project user@example.com secrets/api.key
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    manager = SecurityManager(project_path)
    
    allowed, reason = manager.check_access(entity_id, resource_path, realm_name)
    
    if allowed:
        click.echo(f"✅ Access ALLOWED for '{entity_id}' to '{resource_path}'")
    else:
        click.echo(f"❌ Access DENIED for '{entity_id}' to '{resource_path}'")
        click.echo(f"   Reason: {reason}")


@cmd_security.command("show")
@click.argument('realm_name')
@click.option('--tapu', 'show_tapu', is_flag=True, help='Show tapu declarations')
@click.option('--mana', 'show_mana', is_flag=True, help='Show mana grants')
def cmd_show(realm_name: str, show_tapu: bool, show_mana: bool):
    """Show security configuration for a realm.
    
    REALM_NAME: Name of the realm
    
    Examples:
        tehau security show my-project
        tehau security show my-project --tapu
        tehau security show my-project --mana
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    manager = SecurityManager(project_path)
    
    # Default to showing both
    if not show_tapu and not show_mana:
        show_tapu = show_mana = True
    
    click.echo(f"🔐 Security: {realm_name}")
    click.echo("")
    
    if show_tapu:
        click.echo("📜 Tapu Declarations:")
        if not manager.tapu_declarations:
            click.echo("   (none)")
        else:
            for path, decl in sorted(manager.tapu_declarations.items()):
                level_emoji = {
                    TapuLevel.NOA: "🟢",
                    TapuLevel.AHI: "🟡",
                    TapuLevel.TAPU: "🔴",
                    TapuLevel.WHAKAHAERE: "⚫"
                }
                emoji = level_emoji.get(decl.tapu_level, "⬜")
                click.echo(f"   {emoji} {path}: {decl.tapu_level.name}")
                if decl.reason:
                    click.echo(f"      Reason: {decl.reason}")
        click.echo("")
    
    if show_mana:
        click.echo("👑 Mana Grants:")
        if not manager.mana_grants:
            click.echo("   (none)")
        else:
            for entity, grants in sorted(manager.mana_grants.items()):
                click.echo(f"   {entity}:")
                for grant in grants:
                    valid = "✓" if grant.is_valid() else "✗"
                    perms = ", ".join(grant.permissions) if grant.permissions else "*"
                    click.echo(f"      [{valid}] {grant.mana_type.value}: {perms}")
                    if grant.expires_at:
                        click.echo(f"          Expires: {grant.expires_at.isoformat()}")


@cmd_security.command("audit")
@click.argument('realm_name')
@click.option('--output', '-o', type=click.Path(), help='Output file')
def cmd_audit(realm_name: str, output: Optional[str]):
    """Generate security audit for a realm.
    
    REALM_NAME: Name of the realm
    
    Examples:
        tehau security audit my-project
        tehau security audit my-project --output audit.json
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    manager = SecurityManager(project_path)
    
    audit = {
        'realm': realm_name,
        'timestamp': datetime.utcnow().isoformat(),
        'summary': {
            'tapu_declarations': len(manager.tapu_declarations),
            'mana_grants': sum(len(g) for g in manager.mana_grants.values()),
            'entities_with_mana': len(manager.mana_grants)
        },
        'tapu_by_level': {},
        'mana_by_type': {},
        'issues': []
    }
    
    # Count tapu by level
    for decl in manager.tapu_declarations.values():
        level = decl.tapu_level.name
        audit['tapu_by_level'][level] = audit['tapu_by_level'].get(level, 0) + 1
    
    # Count mana by type
    for grants in manager.mana_grants.values():
        for grant in grants:
            mtype = grant.mana_type.value
            audit['mana_by_type'][mtype] = audit['mana_by_type'].get(mtype, 0) + 1
    
    # Check for issues
    for grants in manager.mana_grants.values():
        for grant in grants:
            if not grant.is_valid():
                audit['issues'].append({
                    'type': 'expired_grant',
                    'entity': grant.entity_id,
                    'mana_type': grant.mana_type.value
                })
            if '*' in grant.permissions:
                audit['issues'].append({
                    'type': 'wildcard_permission',
                    'entity': grant.entity_id,
                    'mana_type': grant.mana_type.value
                })
    
    if output:
        with open(output, 'w') as f:
            json.dump(audit, f, indent=2)
        click.echo(f"✅ Audit saved to {output}")
    else:
        click.echo(f"🔍 Security Audit: {realm_name}")
        click.echo("")
        click.echo(f"Tapu declarations: {audit['summary']['tapu_declarations']}")
        click.echo(f"Mana grants: {audit['summary']['mana_grants']}")
        click.echo(f"Entities with mana: {audit['summary']['entities_with_mana']}")
        click.echo("")
        
        if audit['issues']:
            click.echo(f"⚠️  Issues found: {len(audit['issues'])}")
            for issue in audit['issues']:
                click.echo(f"   - {issue['type']}: {issue['entity']}")
        else:
            click.echo("✅ No issues found")
