"""
Te Hau — Infrastructure Commands
================================
CLI commands for infrastructure provisioning and management.

Commands:
    tehau infra plan <realm>      Plan infrastructure changes (dry run)
    tehau infra apply <realm>     Apply infrastructure changes
    tehau infra status <realm>    Show current infrastructure status
    tehau infra gen <realm>       Generate infra.yaml template
"""

import click
import json
from pathlib import Path

from te_hau.core import (
    get_awaos_root,
    get_projects_path,
    realm_exists,
)


@click.group()
def cmd_infra():
    """Infrastructure provisioning and management."""
    pass


@cmd_infra.command("plan")
@click.argument("realm_name")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def infra_plan(realm_name: str, verbose: bool):
    """Plan infrastructure changes (dry run)."""
    from te_hau.core import get_infra_provisioner
    
    realm_path = get_projects_path() / realm_name
    if not realm_exists(realm_name):
        click.secho(f"Realm not found: {realm_name}", fg="red")
        raise SystemExit(1)
    
    provisioner = get_infra_provisioner(str(realm_path))
    manifest = provisioner.load_manifest()
    
    if not manifest:
        click.secho("No infra.yaml found in mauri/", fg="yellow")
        click.echo("Run 'tehau infra gen' to create one.")
        raise SystemExit(1)
    
    click.secho(f"\n📋 Infrastructure Plan for {realm_name}", fg="cyan", bold=True)
    click.echo("═" * 50)
    
    # Show what would be created
    click.echo(f"\nRealm ID: {manifest.realm_id}")
    click.echo(f"Version: {manifest.version}")
    click.echo(f"Resources: {len(manifest.resources)}")
    
    click.echo("\nResources to provision:")
    for res in manifest.resources:
        icon = {
            "database_table": "🗄️",
            "storage_bucket": "📦",
            "edge_function": "⚡",
            "github_repo": "🐙",
            "pages_project": "☁️",
            "render_service": "🚀",
        }.get(res.type.value, "📌")
        
        click.echo(f"  {icon} {res.name} ({res.service.value}/{res.type.value})")
        
        if verbose and res.depends_on:
            click.echo(f"      └─ depends on: {', '.join(res.depends_on)}")
    
    # Show secrets needed
    if manifest.secrets:
        click.echo("\nSecrets required:")
        for secret in manifest.secrets:
            click.echo(f"  🔐 {secret}")
    
    click.secho("\n✅ Plan complete. Run 'tehau infra apply' to generate files.", fg="green")


@cmd_infra.command("apply")
@click.argument("realm_name")
@click.option("--dry-run", is_flag=True, help="Only generate files, don't call APIs")
def infra_apply(realm_name: str, dry_run: bool):
    """Apply infrastructure changes."""
    from te_hau.core import get_infra_provisioner
    
    realm_path = get_projects_path() / realm_name
    if not realm_exists(realm_name):
        click.secho(f"Realm not found: {realm_name}", fg="red")
        raise SystemExit(1)
    
    provisioner = get_infra_provisioner(str(realm_path))
    manifest = provisioner.load_manifest()
    
    if not manifest:
        click.secho("No infra.yaml found", fg="red")
        raise SystemExit(1)
    
    click.secho(f"\n🚀 Provisioning infrastructure for {realm_name}...", fg="cyan")
    
    results = provisioner.provision(manifest, dry_run=dry_run)
    
    click.echo("\nResults:")
    success_count = 0
    fail_count = 0
    
    for result in results:
        if result.success:
            success_count += 1
            click.secho(f"  ✓ {result.resource_name}: {result.message}", fg="green")
        else:
            fail_count += 1
            click.secho(f"  ✗ {result.resource_name}: {result.message}", fg="red")
    
    click.echo(f"\n{success_count} succeeded, {fail_count} failed")
    
    if success_count > 0:
        click.echo(f"\nGenerated files in: {realm_path}/.generated/")


@cmd_infra.command("status")
@click.argument("realm_name")
def infra_status(realm_name: str):
    """Show current infrastructure status."""
    from te_hau.core import get_infra_provisioner
    
    realm_path = get_projects_path() / realm_name
    if not realm_exists(realm_name):
        click.secho(f"Realm not found: {realm_name}", fg="red")
        raise SystemExit(1)
    
    provisioner = get_infra_provisioner(str(realm_path))
    generated_path = provisioner.generated_path
    
    click.secho(f"\n📊 Infrastructure Status: {realm_name}", fg="cyan", bold=True)
    click.echo("═" * 50)
    
    # Check manifest
    manifest = provisioner.load_manifest()
    if manifest:
        click.secho("✓ infra.yaml found", fg="green")
    else:
        click.secho("✗ No infra.yaml", fg="yellow")
        return
    
    # Check generated files
    if generated_path.exists():
        click.secho("✓ .generated/ directory exists", fg="green")
        
        # List generated files
        for subdir in ["supabase", "github", "cloudflare", "render"]:
            subpath = generated_path / subdir
            if subpath.exists():
                files = list(subpath.glob("*"))
                click.echo(f"  └─ {subdir}/: {len(files)} file(s)")
        
        # Check summary
        summary_path = generated_path / "provision_summary.json"
        if summary_path.exists():
            with open(summary_path) as f:
                summary = json.load(f)
            click.echo(f"\nLast provisioned: {summary.get('provisioned_at', 'unknown')}")
    else:
        click.secho("✗ Not yet provisioned", fg="yellow")


@cmd_infra.command("gen")
@click.argument("realm_name")
@click.option("--force", "-f", is_flag=True, help="Overwrite existing")
def infra_gen(realm_name: str, force: bool):
    """Generate infra.yaml template for a realm."""
    from te_hau.core.infra import create_example_manifest
    
    realm_path = get_projects_path() / realm_name
    if not realm_exists(realm_name):
        click.secho(f"Realm not found: {realm_name}", fg="red")
        raise SystemExit(1)
    
    manifest_path = realm_path / "mauri" / "infra.yaml"
    
    if manifest_path.exists() and not force:
        click.secho("infra.yaml already exists. Use --force to overwrite.", fg="yellow")
        raise SystemExit(1)
    
    # Generate example manifest
    manifest = create_example_manifest(realm_name)
    
    # Write to YAML
    import yaml
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(manifest_path, "w") as f:
        yaml.safe_dump(manifest.to_dict(), f, default_flow_style=False, sort_keys=False)
    
    click.secho(f"✓ Generated {manifest_path}", fg="green")
    click.echo("\nEdit the manifest, then run:")
    click.echo(f"  tehau infra plan {realm_name}")
    click.echo(f"  tehau infra apply {realm_name}")
