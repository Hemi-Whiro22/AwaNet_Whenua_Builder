"""
Te Hau Kaitiaki Command

Invoke and manage AI guardians.
"""

import click
import json
from pathlib import Path

from te_hau.core.fs import get_projects_path, realm_exists
from te_hau.core.kaitiaki import (
    get_kaitiaki, 
    list_kaitiaki, 
    invoke_kaitiaki,
    CORE_KAITIAKI
)


@click.command('kaitiaki')
@click.argument('action', type=click.Choice(['list', 'invoke', 'info', 'chat']))
@click.argument('name', required=False)
@click.option('--realm', '-r', help='Realm context')
@click.option('--prompt', '-p', help='Prompt for invoke action')
@click.option('--context-file', '-c', type=click.Path(exists=True), help='Context file (JSON)')
def cmd_kaitiaki(action: str, name: str, realm: str, prompt: str, context_file: str):
    """Manage and invoke kaitiaki (AI guardians).
    
    Actions:
      list   - List available kaitiaki
      invoke - Send a single prompt to a kaitiaki
      info   - Show kaitiaki details
      chat   - Start interactive chat with a kaitiaki
    
    Examples:
      tehau kaitiaki list
      tehau kaitiaki info kitenga_whiro
      tehau kaitiaki invoke ruru --prompt "Summarize this document"
      tehau kaitiaki chat kitenga_whiro --realm my_project
    """
    if action == 'list':
        _list_kaitiaki(realm)
    elif action == 'info':
        if not name:
            raise click.ClickException("Name required for info action")
        _show_info(name)
    elif action == 'invoke':
        if not name:
            raise click.ClickException("Name required for invoke action")
        if not prompt:
            raise click.ClickException("Prompt required for invoke action (--prompt)")
        _invoke(name, prompt, realm, context_file)
    elif action == 'chat':
        if not name:
            raise click.ClickException("Name required for chat action")
        _chat(name, realm)


def _list_kaitiaki(realm: str = None):
    """List available kaitiaki."""
    click.echo("🛡️  Available Kaitiaki")
    click.echo("")
    
    kaitiaki = list_kaitiaki(realm)
    
    # Group by source
    core = [k for k in kaitiaki if k['source'] == 'core']
    realm_specific = [k for k in kaitiaki if k['source'] == 'realm']
    
    click.echo("Core Kaitiaki:")
    for k in core:
        click.echo(f"  • {k['display_name']} ({k['name']})")
        click.echo(f"    Role: {k['role']}")
        click.echo(f"    {k['description']}")
        click.echo("")
    
    if realm_specific:
        click.echo("Realm Kaitiaki:")
        for k in realm_specific:
            click.echo(f"  • {k['display_name']} ({k['name']})")
            click.echo(f"    Role: {k['role']}")
            click.echo("")


def _show_info(name: str):
    """Show detailed kaitiaki information."""
    try:
        kaitiaki = get_kaitiaki(name)
        config = kaitiaki.config
        
        click.echo(f"🛡️  {config.get('name', name)}")
        click.echo(f"   Role: {config.get('role', 'Unknown')}")
        click.echo("")
        
        if 'description' in config:
            click.echo(f"Description:")
            click.echo(f"  {config['description']}")
            click.echo("")
        
        click.echo(f"Model: {config.get('model', 'gpt-4o-mini')}")
        click.echo(f"Temperature: {config.get('temperature', 0.7)}")
        click.echo("")
        
        if 'tools' in config:
            click.echo("Tools:")
            for tool in config['tools']:
                click.echo(f"  • {tool}")
            click.echo("")
        
        if 'system_prompt' in config:
            click.echo("System Prompt Preview:")
            preview = config['system_prompt'][:300]
            if len(config['system_prompt']) > 300:
                preview += "..."
            click.echo(f"  {preview}")
            
    except ValueError as e:
        raise click.ClickException(str(e))


def _invoke(name: str, prompt: str, realm: str = None, context_file: str = None):
    """Invoke a kaitiaki with a prompt."""
    context = None
    if context_file:
        with open(context_file) as f:
            context = json.load(f)
    
    click.echo(f"🛡️  Invoking {name}...")
    click.echo("")
    
    try:
        response = invoke_kaitiaki(
            name=name,
            prompt=prompt,
            realm_name=realm,
            context=context
        )
        
        click.echo("Response:")
        click.echo("")
        click.echo(response)
        
    except Exception as e:
        raise click.ClickException(f"Invocation failed: {e}")


def _chat(name: str, realm: str = None):
    """Interactive chat with a kaitiaki."""
    try:
        kaitiaki = get_kaitiaki(name, realm)
        config = kaitiaki.config
        
        click.echo(f"🛡️  Chat with {config.get('name', name)}")
        click.echo(f"   Role: {config.get('role', 'Assistant')}")
        if realm:
            click.echo(f"   Realm: {realm}")
        click.echo("")
        click.echo("Type 'exit' or 'quit' to end, 'clear' to reset history")
        click.echo("-" * 50)
        click.echo("")
        
        while True:
            try:
                user_input = click.prompt("You", prompt_suffix=": ")
            except click.Abort:
                break
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                click.echo("")
                click.echo("Haere rā! (Goodbye)")
                break
            
            if user_input.lower() == 'clear':
                kaitiaki.reset_conversation()
                click.echo("(Conversation cleared)")
                click.echo("")
                continue
            
            if not user_input.strip():
                continue
            
            try:
                response = kaitiaki.invoke(user_input)
                click.echo("")
                click.echo(f"{config.get('name', name)}: {response}")
                click.echo("")
            except Exception as e:
                click.echo(f"Error: {e}")
                click.echo("")
                
    except ValueError as e:
        raise click.ClickException(str(e))


@click.command('kaitiaki-list')
@click.option('--realm', '-r', help='Realm context')
def cmd_kaitiaki_list(realm: str):
    """List available kaitiaki."""
    _list_kaitiaki(realm)
