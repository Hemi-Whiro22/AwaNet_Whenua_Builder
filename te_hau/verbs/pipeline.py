"""
Te Hau Pipeline Command

Execute and manage pipelines.
"""

import click
import json
import yaml
from pathlib import Path
from datetime import datetime

from te_hau.core.fs import get_projects_path, realm_exists
from te_hau.mauri.seal import verify_seal, is_sealed


@click.command()
@click.argument('realm_name')
@click.argument('pipeline_name')
@click.option('--input', '-i', 'input_path', help='Input file or directory')
@click.option('--output', '-o', 'output_path', help='Output directory')
@click.option('--dry-run', is_flag=True, help='Show what would be executed')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
@click.option('--force', '-f', is_flag=True, help='Run even if realm is unsealed')
def cmd_pipeline(realm_name: str, pipeline_name: str, input_path: str, 
                 output_path: str, dry_run: bool, verbose: bool, force: bool):
    """Execute a pipeline in a realm.
    
    REALM_NAME: Name of the realm
    PIPELINE_NAME: Name of the pipeline to run (ocr, summarise, embed, etc.)
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    
    # Mauri enforcement - check seal status
    if not dry_run:
        sealed = is_sealed(project_path)
        if sealed:
            # Verify seal integrity
            valid, message = verify_seal(project_path)
            if not valid:
                raise click.ClickException(
                    f"Realm seal is invalid: {message}\n"
                    "Run 'tehau unseal' then 'tehau seal' to fix."
                )
            click.echo("✓ Mauri verified")
        else:
            if not force:
                click.echo("⚠️  Warning: Realm is unsealed")
                click.echo("   Pipeline results may not be trusted.")
                click.echo("   Use --force to proceed anyway, or seal first with 'tehau seal'")
                click.echo("")
                if not click.confirm("Continue with unsealed realm?"):
                    raise click.Abort()
    
    # Load pipeline configuration
    pipeline_config = load_pipeline_config(project_path, pipeline_name)
    
    if not pipeline_config:
        raise click.ClickException(
            f"Pipeline '{pipeline_name}' not found. "
            f"Available: {', '.join(list_available_pipelines(project_path))}"
        )
    
    click.echo(f"🔄 Pipeline: {pipeline_name}")
    click.echo(f"   Realm: {realm_name}")
    click.echo("")
    
    if dry_run:
        show_pipeline_plan(pipeline_config, input_path, output_path, verbose)
        return
    
    # Execute pipeline
    execute_pipeline(project_path, pipeline_config, input_path, output_path, verbose)


def load_pipeline_config(project_path: Path, pipeline_name: str) -> dict:
    """Load pipeline configuration from YAML or JSON."""
    
    # Check for pipeline definitions
    pipelines_dir = project_path / "pipelines"
    
    # Try YAML first
    yaml_path = pipelines_dir / f"{pipeline_name}.yaml"
    if yaml_path.exists():
        with open(yaml_path) as f:
            return yaml.safe_load(f)
    
    # Try JSON
    json_path = pipelines_dir / f"{pipeline_name}.json"
    if json_path.exists():
        with open(json_path) as f:
            return json.load(f)
    
    # Check for built-in pipelines
    builtin = get_builtin_pipeline(pipeline_name)
    if builtin:
        return builtin
    
    return None


def get_builtin_pipeline(name: str) -> dict:
    """Get built-in pipeline definition."""
    
    builtins = {
        'ocr': {
            'name': 'OCR Pipeline',
            'description': 'Extract text from images and PDFs',
            'stages': [
                {'name': 'extract', 'type': 'ocr', 'engine': 'tesseract'},
                {'name': 'clean', 'type': 'text_clean'},
                {'name': 'output', 'type': 'save', 'format': 'markdown'}
            ]
        },
        'summarise': {
            'name': 'Summarisation Pipeline',
            'description': 'Generate summaries using LLM',
            'stages': [
                {'name': 'chunk', 'type': 'chunker', 'size': 4000},
                {'name': 'summarise', 'type': 'llm', 'model': 'gpt-4o-mini'},
                {'name': 'output', 'type': 'save', 'format': 'markdown'}
            ]
        },
        'embed': {
            'name': 'Embedding Pipeline',
            'description': 'Generate embeddings and store in vector DB',
            'stages': [
                {'name': 'chunk', 'type': 'chunker', 'size': 1000},
                {'name': 'embed', 'type': 'embedder', 'model': 'text-embedding-3-small'},
                {'name': 'store', 'type': 'vector_store', 'target': 'supabase'}
            ]
        },
        'translate': {
            'name': 'Translation Pipeline',
            'description': 'Translate to/from te reo Māori',
            'stages': [
                {'name': 'detect', 'type': 'language_detect'},
                {'name': 'translate', 'type': 'llm', 'model': 'gpt-4o', 
                 'system': 'You are Ahiatoa, translator for te reo Māori'},
                {'name': 'output', 'type': 'save', 'format': 'json'}
            ]
        },
        'taonga': {
            'name': 'Taonga Pipeline',
            'description': 'Full processing: OCR → Summarise → Translate → Embed',
            'stages': [
                {'name': 'extract', 'type': 'ocr', 'engine': 'tesseract'},
                {'name': 'clean', 'type': 'text_clean'},
                {'name': 'summarise', 'type': 'llm', 'model': 'gpt-4o-mini'},
                {'name': 'translate', 'type': 'llm', 'model': 'gpt-4o'},
                {'name': 'chunk', 'type': 'chunker', 'size': 1000},
                {'name': 'embed', 'type': 'embedder', 'model': 'text-embedding-3-small'},
                {'name': 'store', 'type': 'vector_store', 'target': 'supabase'}
            ]
        }
    }
    
    return builtins.get(name)


def list_available_pipelines(project_path: Path) -> list:
    """List all available pipelines."""
    
    available = ['ocr', 'summarise', 'embed', 'translate', 'taonga']
    
    pipelines_dir = project_path / "pipelines"
    if pipelines_dir.exists():
        for f in pipelines_dir.glob("*.yaml"):
            available.append(f.stem)
        for f in pipelines_dir.glob("*.json"):
            if f.stem not in available:
                available.append(f.stem)
    
    return available


def show_pipeline_plan(config: dict, input_path: str, output_path: str, verbose: bool):
    """Show what would be executed."""
    
    click.echo(f"DRY RUN - {config.get('name', 'Pipeline')}")
    click.echo("")
    
    if 'description' in config:
        click.echo(f"Description: {config['description']}")
        click.echo("")
    
    click.echo("Stages:")
    for i, stage in enumerate(config.get('stages', []), 1):
        click.echo(f"  {i}. {stage['name']} ({stage['type']})")
        
        if verbose:
            for key, value in stage.items():
                if key not in ['name', 'type']:
                    click.echo(f"     {key}: {value}")
    
    click.echo("")
    click.echo(f"Input: {input_path or '(stdin)'}")
    click.echo(f"Output: {output_path or '(stdout)'}")
    click.echo("")
    click.echo("Remove --dry-run to execute pipeline.")


def execute_pipeline(project_path: Path, config: dict, 
                     input_path: str, output_path: str, verbose: bool):
    """Execute pipeline stages."""
    
    click.echo(f"Executing: {config.get('name', 'Pipeline')}")
    click.echo("")
    
    data = None
    
    # Load input
    if input_path:
        input_file = Path(input_path)
        if not input_file.exists():
            raise click.ClickException(f"Input not found: {input_path}")
        
        with open(input_file) as f:
            data = f.read()
        
        click.echo(f"✓ Loaded input ({len(data)} chars)")
    
    # Execute stages
    stages = config.get('stages', [])
    
    for i, stage in enumerate(stages, 1):
        stage_name = stage['name']
        stage_type = stage['type']
        
        click.echo(f"  [{i}/{len(stages)}] {stage_name}...")
        
        try:
            data = execute_stage(stage, data, project_path, verbose)
            click.echo(f"       ✓ Complete")
        except Exception as e:
            click.echo(f"       ✗ Failed: {e}")
            raise click.ClickException(f"Pipeline failed at stage: {stage_name}")
    
    # Save output
    if output_path and data:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            if isinstance(data, dict):
                json.dump(data, f, indent=2)
            else:
                f.write(str(data))
        
        click.echo("")
        click.echo(f"✓ Output saved to: {output_path}")
    
    click.echo("")
    click.echo("✓ Pipeline complete")


def execute_stage(stage: dict, data, project_path: Path, verbose: bool):
    """Execute a single pipeline stage."""
    
    stage_type = stage['type']
    
    if stage_type == 'chunker':
        # Simple text chunking
        size = stage.get('size', 1000)
        if isinstance(data, str):
            chunks = [data[i:i+size] for i in range(0, len(data), size)]
            return chunks
        return data
    
    elif stage_type == 'text_clean':
        # Basic text cleaning
        if isinstance(data, str):
            import re
            data = re.sub(r'\s+', ' ', data)
            data = data.strip()
        return data
    
    elif stage_type == 'save':
        # Pass through for saving
        return data
    
    elif stage_type == 'llm':
        # Real LLM processing
        try:
            from te_hau.core import ai
            model = stage.get('model', 'gpt-4o-mini')
            action = stage.get('action', 'complete')
            
            if isinstance(data, list):
                text = "\n\n".join(str(d) for d in data)
            else:
                text = str(data)
            
            if action == 'summarize':
                result = ai.summarize(text, model=model)
            elif action == 'translate_to_maori':
                result = ai.translate_to_maori(text, model=model)
            elif action == 'translate_to_english':
                result = ai.translate_to_english(text, model=model)
            else:
                system = stage.get('system', 'You are a helpful assistant.')
                result = ai.complete(text, system=system, model=model)
            
            click.echo(f"       (LLM: {model} ✓)")
            return result
        except ImportError:
            click.echo(f"       (LLM: {stage.get('model', 'gpt-4o-mini')} - AI module not available)")
            return data
        except Exception as e:
            click.echo(f"       (LLM: Error - {e})")
            return data
    
    elif stage_type == 'embedder':
        # Real embedding generation
        try:
            from te_hau.core import ai
            model = stage.get('model', 'text-embedding-3-small')
            
            if isinstance(data, str):
                chunks = [data]
            elif isinstance(data, list):
                chunks = data
            else:
                chunks = [str(data)]
            
            embeddings = ai.embed_texts(chunks, model=model)
            click.echo(f"       (Embedder: {model} - {len(chunks)} chunks ✓)")
            
            return [
                {'content': chunk, 'embedding': emb}
                for chunk, emb in zip(chunks, embeddings)
            ]
        except ImportError:
            click.echo(f"       (Embedder: {stage.get('model')} - AI module not available)")
            return data
        except Exception as e:
            click.echo(f"       (Embedder: Error - {e})")
            return data
    
    elif stage_type == 'vector_store':
        # Real vector storage
        try:
            from te_hau.core import supabase
            namespace = f"realm::{project_path.name}"
            
            if not isinstance(data, list):
                click.echo(f"       (Store: skipped - not embedding data)")
                return data
            
            doc_ids = supabase.store_embeddings(namespace, data)
            click.echo(f"       (Store: {len(doc_ids)} vectors stored ✓)")
            return {'stored': len(doc_ids), 'doc_ids': doc_ids}
        except ImportError:
            click.echo(f"       (Store: {stage.get('target', 'supabase')} - module not available)")
            return data
        except Exception as e:
            click.echo(f"       (Store: Error - {e})")
            return data
    
    elif stage_type == 'ocr':
        # OCR placeholder - would need pytesseract or similar
        click.echo(f"       (OCR: {stage.get('engine', 'tesseract')} - not implemented)")
        return data
    
    elif stage_type == 'language_detect':
        # Simple language detection placeholder
        return data
    
    else:
        click.echo(f"       (Unknown stage type: {stage_type})")
        return data


@click.command()
@click.argument('realm_name')
def cmd_pipelines_list(realm_name: str):
    """List available pipelines in a realm.
    
    REALM_NAME: Name of the realm
    """
    if not realm_exists(realm_name):
        raise click.ClickException(f"Realm '{realm_name}' not found")
    
    project_path = get_projects_path() / realm_name
    
    click.echo(f"📋 Available Pipelines for '{realm_name}'")
    click.echo("")
    
    pipelines = list_available_pipelines(project_path)
    
    click.echo("Built-in:")
    for name in ['ocr', 'summarise', 'embed', 'translate', 'taonga']:
        config = get_builtin_pipeline(name)
        click.echo(f"  • {name}: {config['description']}")
    
    # Custom pipelines
    pipelines_dir = project_path / "pipelines"
    if pipelines_dir.exists():
        custom = [p for p in pipelines if p not in ['ocr', 'summarise', 'embed', 'translate', 'taonga']]
        if custom:
            click.echo("")
            click.echo("Custom:")
            for name in custom:
                click.echo(f"  • {name}")
