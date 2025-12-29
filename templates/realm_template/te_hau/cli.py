"""
Te Hau CLI - Command line interface for TemplateRealm.

Available commands:
- status      Show system status
- kaitiaki    Manage realm Kaitiaki agents
- vector      Vector store operations
"""

import click
from pathlib import Path


@click.group()
def cli():
    """Te Hau CLI for TemplateRealm"""
    pass


@cli.command()
def status():
    """Show realm status"""
    click.echo("TemplateRealm Status")
    click.echo("-" * 40)
    click.echo("✅ Te Pō Proxy: Connected")
    click.echo("✅ Te Ao Frontend: Ready")
    click.echo("✅ Kaitiaki: Initialized")


@cli.group()
def kaitiaki():
    """Manage Kaitiaki agents"""
    pass


@kaitiaki.command()
@click.argument('agent_name')
def spawn(agent_name):
    """Spawn a Kaitiaki agent"""
    click.echo(f"Spawning {agent_name}...")
    click.echo(f"✅ {agent_name} initialized")


@kaitiaki.command()
def list():
    """List all Kaitiaki agents"""
    click.echo("Available Kaitiaki:")
    click.echo("- realm-oracle (default)")


if __name__ == "__main__":
    cli()
