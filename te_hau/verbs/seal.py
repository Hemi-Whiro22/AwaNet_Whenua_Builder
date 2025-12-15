"""
Te Hau Seal Command

Compute and verify realm seals for integrity.
"""

import click
from pathlib import Path

from te_hau.core.fs import get_projects_path, realm_exists
from te_hau.mauri.seal import seal_realm, verify_realm_seal, compute_seal


@click.command()
@click.argument('realm_name')
@click.option('--verify', is_flag=True, help='Verify existing seal')
@click.option('--force', '-f', is_flag=True, help='Force re-seal')
@click.option('--verbose', '-v', is_flag=True, help='Show seal details')
def cmd_seal(realm_name: str, verify: bool, force: bool, verbose: bool):
    """Seal a realm to preserve its mauri (integrity).
    
    REALM_NAME: Name of the realm to seal
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    
    if verify:
        # Verify mode
        click.echo(f"🔍 Verifying seal for: {realm_name}")
        
        result = verify_realm_seal(project_path)
        
        if result['valid']:
            click.echo("")
            click.echo("✓ Seal valid - realm integrity preserved")
            
            if verbose:
                click.echo("")
                click.echo(f"  Seal: {result['stored_seal'][:16]}...")
                click.echo(f"  Computed: {result['computed_seal'][:16]}...")
        else:
            click.echo("")
            click.echo("✗ Seal broken - realm has been modified")
            click.echo("")
            click.echo(f"  Expected: {result['stored_seal'][:16]}...")
            click.echo(f"  Computed: {result['computed_seal'][:16]}...")
            click.echo("")
            click.echo("Run 'tehau seal {realm_name}' to reseal after review")
            raise click.ClickException("Seal verification failed")
    
    else:
        # Seal mode
        click.echo(f"🔏 Sealing realm: {realm_name}")
        
        # Check for existing seal
        realm_lock = project_path / "mauri" / "realm_lock.json"
        
        if realm_lock.exists() and not force:
            import json
            with open(realm_lock) as f:
                data = json.load(f)
            
            if 'seal' in data and data['seal']:
                click.echo("")
                click.echo("⚠ Realm already sealed")
                click.echo("  Use --force to reseal")
                return
        
        seal = seal_realm(project_path)
        
        click.echo("")
        click.echo("✓ Realm sealed")
        
        if verbose:
            click.echo(f"  Seal: {seal[:32]}...")
        
        click.echo("")
        click.echo("The seal captures current realm state.")
        click.echo("Any modification will break the seal.")


@click.command()
@click.argument('realm_name')
@click.option('--confirm', is_flag=True, help='Confirm unseal')
def cmd_unseal(realm_name: str, confirm: bool):
    """Remove seal from a realm to allow modifications.
    
    REALM_NAME: Name of the realm to unseal
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    if not confirm:
        click.echo("⚠ Unsealing removes integrity protection")
        click.echo("")
        click.echo("This allows:")
        click.echo("  • File modifications")
        click.echo("  • Template updates")
        click.echo("  • Schema changes")
        click.echo("")
        click.echo(f"Run with --confirm to proceed:")
        click.echo(f"  tehau unseal {realm_name} --confirm")
        return
    
    project_path = get_projects_path() / realm_name
    realm_lock = project_path / "mauri" / "realm_lock.json"
    
    if not realm_lock.exists():
        raise click.ClickException("No realm_lock.json found")
    
    import json
    
    with open(realm_lock) as f:
        data = json.load(f)
    
    if not data.get('seal'):
        click.echo("ℹ Realm is not currently sealed")
        return
    
    # Remove seal
    data['seal'] = None
    data['sealed_at'] = None
    
    with open(realm_lock, 'w') as f:
        json.dump(data, f, indent=2)
    
    click.echo(f"🔓 Realm '{realm_name}' unsealed")
    click.echo("")
    click.echo("You may now modify realm files.")
    click.echo("Remember to reseal after changes:")
    click.echo(f"  tehau seal {realm_name}")
