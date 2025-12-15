"""
Te Hau — Orchestrator Commands
==============================
CLI commands for kaitiaki orchestration and multi-agent management.

Commands:
    tehau cluster status          Show cluster status
    tehau cluster list            List all kaitiaki
    tehau cluster route <task>    Show routing for a task type
    tehau cluster handoff         Perform a kaitiaki handoff
"""

import click
import json
from pathlib import Path

from te_hau.core import get_orchestrator


@click.group()
def cmd_cluster():
    """Kaitiaki cluster management."""
    pass


@cmd_cluster.command("status")
def cluster_status():
    """Show kaitiaki cluster status."""
    orchestrator = get_orchestrator()
    
    click.secho("\n🌐 Kaitiaki Cluster Status", fg="cyan", bold=True)
    click.echo("═" * 50)
    
    kaitiaki_list = orchestrator.kaitiaki
    
    click.echo(f"\nTotal kaitiaki: {len(kaitiaki_list)}")
    click.echo(f"Root: {orchestrator.lineage.root or 'none'}")
    
    # Show by type
    global_count = sum(1 for k in kaitiaki_list.values() if k.kaitiaki_type.value == "global")
    realm_count = sum(1 for k in kaitiaki_list.values() if k.kaitiaki_type.value == "realm")
    specialist_count = sum(1 for k in kaitiaki_list.values() if k.kaitiaki_type.value == "specialist")
    
    click.echo(f"\nBy type:")
    click.echo(f"  Global: {global_count}")
    click.echo(f"  Realm: {realm_count}")
    click.echo(f"  Specialist: {specialist_count}")
    
    # Show routing
    click.echo("\nRouting table:")
    for task_type, kaitiaki in orchestrator.routing.items():
        if kaitiaki:
            click.echo(f"  {task_type.value:12} → {kaitiaki}")


@cmd_cluster.command("list")
@click.option("--verbose", "-v", is_flag=True, help="Show details")
def cluster_list(verbose: bool):
    """List all registered kaitiaki."""
    orchestrator = get_orchestrator()
    
    click.secho("\n👥 Registered Kaitiaki", fg="cyan", bold=True)
    click.echo("═" * 50)
    
    for name, manifest in orchestrator.kaitiaki.items():
        glyph_icon = {
            "koru_purple": "🟣",
            "koru_blue": "🔵",
            "koru_green": "🟢",
            "koru_orange": "🟠",
            "koru_teal": "🩵",
        }.get(manifest.glyph, "⚪")
        
        click.echo(f"\n{glyph_icon} {name}")
        click.echo(f"   Role: {manifest.role}")
        click.echo(f"   Type: {manifest.kaitiaki_type.value}")
        
        if verbose:
            click.echo(f"   Lineage: {manifest.lineage}")
            click.echo(f"   Purpose: {', '.join(manifest.purpose[:2])}")
            if manifest.capabilities:
                caps = [c.value for c in manifest.capabilities]
                click.echo(f"   Capabilities: {', '.join(caps)}")
            if manifest.tools:
                click.echo(f"   Tools: {', '.join(manifest.tools[:3])}")


@cmd_cluster.command("route")
@click.argument("task_type")
def cluster_route(task_type: str):
    """Show which kaitiaki handles a task type."""
    from te_hau.core.orchestrator import TaskType
    
    orchestrator = get_orchestrator()
    
    # Try to match task type
    try:
        tt = TaskType(task_type.lower())
    except ValueError:
        click.secho(f"Unknown task type: {task_type}", fg="red")
        click.echo("\nAvailable types:")
        for t in TaskType:
            click.echo(f"  • {t.value}")
        raise SystemExit(1)
    
    target = orchestrator.routing.get(tt)
    
    click.secho(f"\n📍 Routing: {task_type}", fg="cyan", bold=True)
    
    if target:
        manifest = orchestrator.kaitiaki.get(target)
        if manifest:
            click.echo(f"\nRoutes to: {target}")
            click.echo(f"Role: {manifest.role}")
            click.echo(f"Lineage: {manifest.lineage}")
        else:
            click.echo(f"\nRoutes to: {target} (not registered)")
    else:
        click.echo("\nNo specific routing - defaults to realm kaitiaki or Whiro")


@cmd_cluster.command("lineage")
@click.argument("kaitiaki_name", required=False)
def cluster_lineage(kaitiaki_name: str):
    """Show kaitiaki lineage tree."""
    orchestrator = get_orchestrator()
    
    click.secho("\n🌳 Kaitiaki Lineage", fg="cyan", bold=True)
    click.echo("═" * 50)
    
    if kaitiaki_name:
        # Show specific lineage
        lineage = orchestrator.lineage.get_lineage_string(kaitiaki_name)
        click.echo(f"\n{kaitiaki_name}: {lineage}")
    else:
        # Show full tree
        def print_tree(name: str, prefix: str = ""):
            node = orchestrator.lineage.nodes.get(name)
            if not node:
                return
            
            manifest = orchestrator.kaitiaki.get(name)
            role = manifest.role if manifest else "unknown"
            
            click.echo(f"{prefix}{name} ({role})")
            
            for i, child in enumerate(node.children):
                is_last = i == len(node.children) - 1
                child_prefix = prefix + ("    " if is_last else "│   ")
                connector = "└── " if is_last else "├── "
                
                child_manifest = orchestrator.kaitiaki.get(child)
                child_role = child_manifest.role if child_manifest else "unknown"
                click.echo(f"{prefix}{connector}{child} ({child_role})")
                
                # Recurse for grandchildren
                child_node = orchestrator.lineage.nodes.get(child)
                if child_node and child_node.children:
                    for gc in child_node.children:
                        gc_manifest = orchestrator.kaitiaki.get(gc)
                        gc_role = gc_manifest.role if gc_manifest else "unknown"
                        click.echo(f"{child_prefix}    └── {gc} ({gc_role})")
        
        root = orchestrator.lineage.root
        if root:
            print_tree(root)
        else:
            click.echo("No root kaitiaki defined")


@cmd_cluster.command("memory")
@click.option("--kaitiaki", "-k", help="Show memory for specific kaitiaki")
def cluster_memory(kaitiaki: str):
    """Show shared memory bus status."""
    orchestrator = get_orchestrator()
    
    click.secho("\n💾 Shared Memory Bus", fg="cyan", bold=True)
    click.echo("═" * 50)
    
    memory = orchestrator.memory
    
    # Global memory
    global_count = len(memory._global_cache)
    click.echo(f"\nGlobal memory: {global_count} entries")
    
    # Local memories
    click.echo(f"\nLocal memories:")
    for name in orchestrator.kaitiaki.keys():
        local = memory._local_cache.get(name, {})
        count = len(local)
        if kaitiaki and name != kaitiaki:
            continue
        click.echo(f"  {name}: {count} entries")


@cmd_cluster.command("context")
@click.argument("kaitiaki_name")
@click.option("--include-global/--no-global", default=True)
@click.option("--include-lineage/--no-lineage", default=True)
def cluster_context(kaitiaki_name: str, include_global: bool, include_lineage: bool):
    """Get fused context for a kaitiaki."""
    orchestrator = get_orchestrator()
    
    if kaitiaki_name not in orchestrator.kaitiaki:
        click.secho(f"Unknown kaitiaki: {kaitiaki_name}", fg="red")
        raise SystemExit(1)
    
    context = orchestrator.fuse_context(
        realm_id="global",
        kaitiaki=kaitiaki_name,
        include_global=include_global,
        include_lineage=include_lineage
    )
    
    click.secho(f"\n📋 Context for {kaitiaki_name}", fg="cyan", bold=True)
    click.echo("═" * 50)
    
    click.echo(f"\nRealm: {context.get('realm_id')}")
    click.echo(f"Timestamp: {context.get('timestamp')}")
    
    if context.get("lineage"):
        click.echo(f"Lineage: {context.get('lineage')}")
    
    if context.get("purpose"):
        click.echo(f"\nPurpose:")
        for p in context.get("purpose", []):
            click.echo(f"  • {p}")
    
    if context.get("tools"):
        click.echo(f"\nTools: {', '.join(context.get('tools', []))}")
    
    if context.get("glyph"):
        click.echo(f"Glyph: {context.get('glyph')}")
