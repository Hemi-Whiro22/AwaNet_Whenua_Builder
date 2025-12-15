"""
Te Hau Evolve Command

Manage kaitiaki evolution stages.
"""

import click
import json
from pathlib import Path
from datetime import datetime

from te_hau.core.fs import get_projects_path, realm_exists
from te_hau.mauri.seal import is_sealed, unseal_realm, seal_realm, verify_seal
from te_hau.core.kaitiaki import get_kaitiaki_evolution_status, EVOLUTION_THRESHOLDS


# Evolution stages in order (SDK stages)
EVOLUTION_STAGES = [
    ('seed', 'Learning, observing, no agentic tools'),
    ('worker', 'Can use safe tools under supervision (100+ invocations)'),
    ('specialist', 'Independent tool use within realm (500+ invocations)'),
    ('guardian', 'Full autonomy, can teach other agents (2000+ invocations)'),
]

# Legacy stage mapping to SDK stages
LEGACY_STAGE_MAP = {
    'pēpi': 'seed',
    'tamariki': 'seed',  
    'rangatahi': 'worker',
    'pakeke': 'specialist',
    'kaumātua': 'guardian',
}


@click.command()
@click.argument('realm_name')
@click.argument('kaitiaki_name')
@click.option('--to', 'target_stage', help='Target evolution stage')
@click.option('--status', is_flag=True, help='Show current evolution status')
@click.option('--force', '-f', is_flag=True, help='Skip evolution checks')
@click.option('--auto-reseal', is_flag=True, default=True, help='Automatically reseal after evolution')
def cmd_evolve(realm_name: str, kaitiaki_name: str, target_stage: str, 
               status: bool, force: bool, auto_reseal: bool):
    """Evolve a kaitiaki to a new stage.
    
    REALM_NAME: Name of the realm
    KAITIAKI_NAME: Name of the kaitiaki to evolve
    
    The realm must be unsealed before evolution. If sealed, this command
    will unseal, evolve, then reseal automatically (unless --no-auto-reseal).
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    kaitiaki_dir = project_path / ".kaitiaki"
    
    if not kaitiaki_dir.exists():
        raise click.ClickException("No .kaitiaki directory found")
    
    # Check seal status
    was_sealed = is_sealed(project_path)
    seal_passphrase = None
    
    if was_sealed and not status:
        click.echo("🔒 Realm is sealed. Unsealing for evolution...")
        seal_passphrase = click.prompt("Enter seal passphrase", hide_input=True)
        
        try:
            unseal_realm(project_path, seal_passphrase)
            click.echo("✓ Unsealed")
        except Exception as e:
            raise click.ClickException(f"Failed to unseal: {e}")
    
    # Find kaitiaki manifest
    manifest_path = kaitiaki_dir / f"{kaitiaki_name}.json"
    
    if not manifest_path.exists():
        # Try finding by partial match
        matches = list(kaitiaki_dir.glob(f"*{kaitiaki_name}*.json"))
        if not matches:
            raise click.ClickException(f"Kaitiaki '{kaitiaki_name}' not found")
        manifest_path = matches[0]
    
    # Load manifest
    with open(manifest_path) as f:
        manifest = json.load(f)
    
    current_stage = manifest.get('stage', 'seed')
    
    # Map legacy stages
    if current_stage in LEGACY_STAGE_MAP:
        current_stage = LEGACY_STAGE_MAP[current_stage]
    
    if status:
        show_evolution_status(manifest, kaitiaki_name, realm_name)
        return
    
    if not target_stage:
        # Show current and next stage
        click.echo(f"🌱 {manifest.get('name', kaitiaki_name)}")
        click.echo("")
        click.echo(f"Current stage: {current_stage}")
        
        current_idx = get_stage_index(current_stage)
        if current_idx < len(EVOLUTION_STAGES) - 1:
            next_stage, next_desc = EVOLUTION_STAGES[current_idx + 1]
            click.echo(f"Next stage: {next_stage} - {next_desc}")
            click.echo("")
            click.echo(f"To evolve: tehau evolve {realm_name} {kaitiaki_name} --to {next_stage}")
        else:
            click.echo("This kaitiaki has reached kaumātua (highest stage)")
        return
    
    # Validate target stage
    valid_stages = [s[0] for s in EVOLUTION_STAGES]
    if target_stage not in valid_stages:
        raise click.ClickException(
            f"Invalid stage '{target_stage}'. Valid stages: {', '.join(valid_stages)}"
        )
    
    current_idx = get_stage_index(current_stage)
    target_idx = get_stage_index(target_stage)
    
    if target_idx <= current_idx and not force:
        raise click.ClickException(
            f"Cannot evolve backwards from {current_stage} to {target_stage}. "
            "Use --force to override."
        )
    
    if target_idx > current_idx + 1 and not force:
        raise click.ClickException(
            f"Cannot skip stages. Current: {current_stage}, "
            f"next should be: {EVOLUTION_STAGES[current_idx + 1][0]}. "
            "Use --force to override."
        )
    
    # Perform evolution
    click.echo(f"✨ Evolving {manifest.get('name', kaitiaki_name)}")
    click.echo(f"   {current_stage} → {target_stage}")
    click.echo("")
    
    # Update manifest
    manifest['stage'] = target_stage
    
    # Add evolution history
    if 'evolution_history' not in manifest:
        manifest['evolution_history'] = []
    
    manifest['evolution_history'].append({
        'from': current_stage,
        'to': target_stage,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'forced': force
    })
    
    # Update tools based on stage
    update_kaitiaki_permissions(manifest, target_stage)
    
    # Save manifest
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    stage_desc = dict(EVOLUTION_STAGES)[target_stage]
    click.echo(f"✓ Evolution complete")
    click.echo(f"  Stage: {target_stage}")
    click.echo(f"  Abilities: {stage_desc}")
    
    # Reseal if was sealed
    if was_sealed and auto_reseal and seal_passphrase:
        click.echo("")
        click.echo("🔒 Resealing realm...")
        try:
            seal_realm(project_path, seal_passphrase)
            click.echo("✓ Realm resealed")
        except Exception as e:
            click.echo(f"⚠ Warning: Failed to reseal: {e}")
            click.echo("  Run 'tehau seal {realm_name}' manually to reseal")


def get_stage_index(stage: str) -> int:
    """Get the index of an evolution stage."""
    for i, (name, _) in enumerate(EVOLUTION_STAGES):
        if name == stage:
            return i
    return 0


def show_evolution_status(manifest: dict, kaitiaki_name: str, realm_name: str = None):
    """Display detailed evolution status with real metrics."""
    click.echo(f"📊 Evolution Status: {manifest.get('name', kaitiaki_name)}")
    click.echo("")
    
    # Get real metrics from tracking system
    real_status = get_kaitiaki_evolution_status(kaitiaki_name, realm_name)
    
    # Use real stage from tracking, fall back to manifest
    current_stage = real_status.get('stage', manifest.get('stage', 'seed'))
    
    # Map legacy stages if needed
    if current_stage in LEGACY_STAGE_MAP:
        current_stage = LEGACY_STAGE_MAP[current_stage]
    
    current_idx = get_stage_index(current_stage)
    
    click.echo("Stages:")
    for i, (stage, desc) in enumerate(EVOLUTION_STAGES):
        threshold = EVOLUTION_THRESHOLDS.get(stage, {}).get('min_invocations', 0)
        if i < current_idx:
            marker = "✓"
        elif i == current_idx:
            marker = "●"
        else:
            marker = "○"
        threshold_str = f" ({threshold}+ invocations)" if threshold > 0 else ""
        click.echo(f"  {marker} {stage}: {desc}{threshold_str}")
    
    click.echo("")
    
    # Show real metrics
    invocations = real_status.get('invocation_count', 0)
    pipelines = real_status.get('successful_pipelines', 0)
    next_stage = real_status.get('next_stage')
    to_next = real_status.get('invocations_to_next', 0)
    
    click.echo("📈 Metrics:")
    click.echo(f"  Total invocations: {invocations}")
    click.echo(f"  Successful pipelines: {pipelines}")
    
    if real_status.get('first_invoked'):
        click.echo(f"  First invoked: {real_status['first_invoked'][:10]}")
    if real_status.get('last_invoked'):
        click.echo(f"  Last invoked: {real_status['last_invoked'][:10]}")
    
    click.echo("")
    
    if next_stage:
        click.echo(f"🎯 Progress to {next_stage}:")
        next_threshold = EVOLUTION_THRESHOLDS.get(next_stage, {}).get('min_invocations', 0)
        progress = min(100, int((invocations / next_threshold) * 100)) if next_threshold > 0 else 100
        bar = "█" * (progress // 10) + "░" * (10 - progress // 10)
        click.echo(f"  [{bar}] {progress}% ({invocations}/{next_threshold})")
        click.echo(f"  {to_next} more invocations needed")
    else:
        click.echo("🌟 Maximum evolution stage reached!")
    
    click.echo("")
    
    # Show history from manifest
    history = manifest.get('evolution_history', [])
    if history:
        click.echo("Evolution History:")
        for entry in history[-5:]:  # Last 5 evolutions
            click.echo(f"  {entry['from']} → {entry['to']} ({entry['timestamp'][:10]})")
    
    # Show current tools
    tools = manifest.get('tools', [])
    if tools:
        click.echo("")
        click.echo(f"Available Tools: {len(tools)}")
        for tool in tools[:5]:
            click.echo(f"  • {tool}")
        if len(tools) > 5:
            click.echo(f"  ... and {len(tools) - 5} more")


def update_kaitiaki_permissions(manifest: dict, stage: str):
    """Update kaitiaki tool permissions based on stage."""
    
    # Base tools available to all
    base_tools = ['read', 'observe', 'report']
    
    # Tools by stage
    stage_tools = {
        'pēpi': base_tools,
        'tamariki': base_tools + ['suggest', 'draft', 'summarize'],
        'rangatahi': base_tools + ['suggest', 'draft', 'summarize', 
                                   'edit', 'create', 'search'],
        'pakeke': base_tools + ['suggest', 'draft', 'summarize',
                               'edit', 'create', 'search', 
                               'execute', 'deploy', 'teach'],
        'kaumātua': base_tools + ['suggest', 'draft', 'summarize',
                                 'edit', 'create', 'search',
                                 'execute', 'deploy', 'teach',
                                 'evolve', 'architect', 'bless']
    }
    
    manifest['tools'] = stage_tools.get(stage, base_tools)
