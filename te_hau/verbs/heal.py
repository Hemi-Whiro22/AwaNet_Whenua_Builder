"""
Te Hau — Healing Commands
=========================
CLI commands for self-healing and drift detection.

Commands:
    tehau heal diagnose <realm>   Diagnose realm health
    tehau heal repair <realm>     Attempt automatic repair
    tehau heal status <realm>     Show healing status
"""

import click
import asyncio
from pathlib import Path

from te_hau.core import (
    get_projects_path,
    realm_exists,
)


@click.group()
def cmd_heal():
    """Self-healing and drift detection."""
    pass


@cmd_heal.command("diagnose")
@click.argument("realm_name")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def heal_diagnose(realm_name: str, verbose: bool):
    """Diagnose realm health - check for drift and issues."""
    from te_hau.core import get_healing_engine
    
    realm_path = get_projects_path() / realm_name
    if not realm_exists(realm_name):
        click.secho(f"Realm not found: {realm_name}", fg="red")
        raise SystemExit(1)
    
    click.secho(f"\n🔍 Diagnosing {realm_name}...", fg="cyan", bold=True)
    click.echo("═" * 50)
    
    engine = get_healing_engine(str(realm_path))
    
    # Run diagnosis
    diagnosis = asyncio.run(engine.diagnose())
    
    # Display results
    click.echo(f"\nRealm: {diagnosis['realm_path']}")
    click.echo(f"Diagnosed at: {diagnosis['timestamp']}")
    
    # File drift
    drift = diagnosis.get("drift", {})
    modified = drift.get("modified_files", [])
    missing = drift.get("missing_files", [])
    new_files = drift.get("new_files", [])
    
    if modified or missing or new_files:
        click.secho("\n📂 File Drift Detected:", fg="yellow")
        if modified:
            click.echo(f"  Modified: {len(modified)} files")
            if verbose:
                for f in modified[:5]:
                    click.echo(f"    • {f}")
        if missing:
            click.secho(f"  Missing: {len(missing)} files", fg="red")
            if verbose:
                for f in missing[:5]:
                    click.echo(f"    • {f}")
        if new_files:
            click.echo(f"  New: {len(new_files)} files")
    else:
        click.secho("\n✓ No file drift detected", fg="green")
    
    # Env drift
    env_drift = drift.get("env_drift", {})
    if any(env_drift.values()):
        click.secho("\n🔐 Environment Drift:", fg="yellow")
        for key, changes in env_drift.items():
            if changes:
                click.echo(f"  {key}: {len(changes)} changes")
    
    # Mauri validation
    mauri = diagnosis.get("mauri", {})
    mauri_issues = []
    
    if not mauri.get("seal_valid", True):
        mauri_issues.append("Invalid seal")
    if not mauri.get("glyph_valid", True):
        mauri_issues.append("Invalid glyph")
    if not mauri.get("lineage_valid", True):
        mauri_issues.append("Invalid lineage")
    
    if mauri_issues:
        click.secho(f"\n⚠️ Mauri Issues: {', '.join(mauri_issues)}", fg="yellow")
    else:
        click.secho("\n✓ Mauri valid", fg="green")
    
    # Overall health
    is_healthy = diagnosis.get("healthy", False)
    if is_healthy:
        click.secho("\n✅ Realm is healthy", fg="green", bold=True)
    else:
        click.secho("\n⚠️ Realm needs attention", fg="yellow", bold=True)
        click.echo("Run 'tehau heal repair' to attempt automatic fixes.")


@cmd_heal.command("repair")
@click.argument("realm_name")
@click.option("--dry-run", is_flag=True, help="Show what would be fixed")
@click.option("--force", "-f", is_flag=True, help="Force repair without confirmation")
def heal_repair(realm_name: str, dry_run: bool, force: bool):
    """Attempt automatic repair of realm issues."""
    from te_hau.core import get_healing_engine
    
    realm_path = get_projects_path() / realm_name
    if not realm_exists(realm_name):
        click.secho(f"Realm not found: {realm_name}", fg="red")
        raise SystemExit(1)
    
    engine = get_healing_engine(str(realm_path))
    
    # First diagnose
    click.secho(f"\n🔧 Preparing repair for {realm_name}...", fg="cyan")
    diagnosis = asyncio.run(engine.diagnose())
    
    if diagnosis.get("healthy", False):
        click.secho("✓ Realm is already healthy, no repairs needed", fg="green")
        return
    
    # Show what will be repaired
    click.echo("\nIssues to repair:")
    
    drift = diagnosis.get("drift", {})
    repairs_needed = []
    
    if drift.get("missing_files"):
        repairs_needed.append(f"  • Restore {len(drift['missing_files'])} missing files")
    if drift.get("env_drift"):
        repairs_needed.append("  • Sync environment variables")
    if not diagnosis.get("mauri", {}).get("seal_valid", True):
        repairs_needed.append("  • Re-seal mauri")
    
    for repair in repairs_needed:
        click.echo(repair)
    
    if dry_run:
        click.secho("\n(Dry run - no changes made)", fg="yellow")
        return
    
    if not force:
        if not click.confirm("\nProceed with repair?"):
            click.echo("Cancelled")
            return
    
    # Execute repair
    click.secho("\n🔧 Repairing...", fg="cyan")
    result = asyncio.run(engine.heal())
    
    if result.get("success"):
        click.secho("✅ Repair complete", fg="green", bold=True)
        
        repairs = result.get("repairs", [])
        for repair in repairs:
            click.echo(f"  ✓ {repair}")
    else:
        click.secho("⚠️ Repair partially failed", fg="yellow")
        for error in result.get("errors", []):
            click.secho(f"  ✗ {error}", fg="red")


@cmd_heal.command("status")
@click.argument("realm_name")
def heal_status(realm_name: str):
    """Show healing status and history."""
    from te_hau.core import get_healing_engine
    
    realm_path = get_projects_path() / realm_name
    if not realm_exists(realm_name):
        click.secho(f"Realm not found: {realm_name}", fg="red")
        raise SystemExit(1)
    
    click.secho(f"\n📊 Healing Status: {realm_name}", fg="cyan", bold=True)
    click.echo("═" * 50)
    
    # Check for healing state file
    state_file = realm_path / ".healing" / "state.json"
    
    if state_file.exists():
        import json
        with open(state_file) as f:
            state = json.load(f)
        
        click.echo(f"\nLast check: {state.get('last_check', 'never')}")
        click.echo(f"Last repair: {state.get('last_repair', 'never')}")
        click.echo(f"Tracked files: {state.get('tracked_files', 0)}")
    else:
        click.echo("\nNo healing history found.")
        click.echo("Run 'tehau heal diagnose' to start tracking.")
