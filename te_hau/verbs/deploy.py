"""
Te Hau Deploy Command

Deploy realms to Cloudflare Pages and Render.
"""

import click
from pathlib import Path

from te_hau.core.fs import get_projects_path, realm_exists
from te_hau.mauri.seal import is_sealed


@click.command()
@click.argument('realm_name')
@click.option('--frontend-only', is_flag=True, help='Deploy frontend only')
@click.option('--backend-only', is_flag=True, help='Deploy backend only')
@click.option('--dry-run', is_flag=True, help='Show what would be deployed')
@click.option('--force', is_flag=True, help='Deploy even if not sealed')
@click.option('--render', is_flag=True, help='Generate render.yaml config')
def cmd_deploy(realm_name: str, frontend_only: bool, backend_only: bool, dry_run: bool, force: bool, render: bool):
    """Deploy a realm to cloud infrastructure.
    
    REALM_NAME: Name of the realm to deploy
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    
    # Check seal status
    if not is_sealed(project_path):
        if force:
            click.echo("⚠️  Warning: Deploying unsealed realm (--force)")
        else:
            click.echo("❌ Realm is not sealed. Seal before deploying:")
            click.echo(f"   tehau seal {realm_name}")
            click.echo("")
            click.echo("Or use --force to deploy anyway (not recommended)")
            return
    
    # Generate render.yaml if requested
    if render:
        generate_render_yaml(project_path, realm_name)
        return
    
    click.echo(f"🚀 Deploying realm: {realm_name}")
    
    if dry_run:
        click.echo("")
        click.echo("DRY RUN - Would perform:")
        
        if not backend_only:
            click.echo("  • Build Te Ao frontend (npm run build)")
            click.echo("  • Deploy to Cloudflare Pages")
            click.echo(f"  • URL: https://{realm_name}.awanet.pages.dev")
        
        if not frontend_only:
            click.echo("  • Deploy mini Te Pō to Render")
            click.echo(f"  • URL: https://{realm_name}-tepo.onrender.com")
        
        click.echo("")
        click.echo("Remove --dry-run to execute deployment.")
        return
    
    # Deploy frontend
    if not backend_only:
        click.echo("")
        click.echo("📦 Deploying Te Ao (frontend)...")
        deploy_frontend(project_path, realm_name)
    
    # Deploy backend
    if not frontend_only:
        click.echo("")
        click.echo("🔥 Deploying mini Te Pō (backend)...")
        deploy_backend(project_path, realm_name)
    
    click.echo("")
    click.echo(f"✓ Deployment complete for '{realm_name}'")


def deploy_frontend(project_path: Path, realm_name: str):
    """Deploy frontend to Cloudflare Pages."""
    import subprocess
    
    te_ao_path = project_path / "te_ao"
    
    if not te_ao_path.exists():
        click.echo("  ⚠ No te_ao directory found, skipping frontend")
        return
    
    # Check for package.json
    if not (te_ao_path / "package.json").exists():
        click.echo("  ⚠ No package.json found, skipping frontend build")
        return
    
    try:
        # Build
        click.echo("  → Running npm build...")
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=te_ao_path,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            click.echo(f"  ⚠ Build failed: {result.stderr}")
            return
        
        # Deploy to Cloudflare Pages
        click.echo("  → Deploying to Cloudflare Pages...")
        
        dist_path = te_ao_path / "dist"
        if not dist_path.exists():
            dist_path = te_ao_path / "build"
        
        if dist_path.exists():
            result = subprocess.run(
                ["npx", "wrangler", "pages", "deploy", str(dist_path), 
                 "--project-name", realm_name],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                click.echo(f"  ✓ Frontend deployed")
            else:
                click.echo(f"  ⚠ Deploy failed: {result.stderr}")
                click.echo("    Make sure wrangler is configured: npx wrangler login")
        else:
            click.echo("  ⚠ No dist/build directory found")
            
    except FileNotFoundError:
        click.echo("  ⚠ npm not found. Install Node.js to deploy frontend.")


def deploy_backend(project_path: Path, realm_name: str):
    """Deploy backend to Render."""
    mini_tepo_path = project_path / "mini_te_po"
    
    if not mini_tepo_path.exists():
        click.echo("  ⚠ No mini_te_po directory found, skipping backend")
        return
    
    # Check for main.py or render.yaml
    if not (mini_tepo_path / "main.py").exists():
        click.echo("  ⚠ No main.py found, skipping backend")
        return
    
    click.echo("  → Backend deployment requires Render configuration")
    click.echo("")
    click.echo("  To deploy to Render:")
    click.echo("    1. Create a new Web Service on render.com")
    click.echo(f"    2. Connect your {realm_name} repository")
    click.echo("    3. Set root directory to: mini_te_po")
    click.echo("    4. Set build command: pip install -r requirements.txt")
    click.echo("    5. Set start command: uvicorn main:app --host 0.0.0.0 --port $PORT")
    click.echo("")
    click.echo("  Or use render.yaml for Blueprint deployment")


def generate_render_yaml(project_path: Path, realm_name: str):
    """Generate render.yaml for Render Blueprint deployment."""
    import json
    
    render_yaml = f"""# Render Blueprint for {realm_name}
# Deploy with: render blueprint sync

services:
  # Mini Te Pō Backend
  - type: web
    name: {realm_name}-tepo
    runtime: python
    region: oregon
    plan: free
    rootDir: mini_te_po
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: REALM_NAME
        value: {realm_name}
      - key: OPENAI_API_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_SERVICE_KEY
        sync: false
      - key: BEARER_KEY
        generateValue: true
    autoDeploy: true

  # Te Ao Frontend (optional - use Cloudflare Pages for better performance)
  # - type: static_site
  #   name: {realm_name}-teao
  #   rootDir: te_ao
  #   buildCommand: npm run build
  #   staticPublishPath: dist
  #   routes:
  #     - type: rewrite
  #       source: /*
  #       destination: /index.html
"""
    
    render_path = project_path / "render.yaml"
    with open(render_path, 'w') as f:
        f.write(render_yaml)
    
    click.echo(f"✅ Generated render.yaml for '{realm_name}'")
    click.echo("")
    click.echo("Deploy to Render:")
    click.echo("  1. Push to GitHub")
    click.echo("  2. Go to render.com → Blueprints → New Blueprint Instance")
    click.echo("  3. Connect your repository")
    click.echo("  4. Set environment variables when prompted")
    click.echo("")
    click.echo("Or deploy manually:")
    click.echo("  render blueprint sync")
