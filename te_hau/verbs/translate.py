"""
Te Hau Translate Command

Cultural-grade translation with Ahiatoa.
"""

import click
import json
import sys
from pathlib import Path
from typing import Optional

from te_hau.core.fs import get_projects_path, realm_exists


@click.group()
def cmd_translate():
    """Translation tools powered by Ahiatoa."""
    pass


@cmd_translate.command("to-maori")
@click.argument('text', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Translate from file')
@click.option('--context', '-c', help='Additional context for translation')
@click.option('--dialect', '-d', help='Preferred dialect')
@click.option('--realm', '-r', help='Use realm glossary')
@click.option('--output', '-o', type=click.Path(), help='Output file')
@click.option('--strict', is_flag=True, default=True, help='Enforce glossary terms')
def cmd_to_maori(
    text: Optional[str],
    file: Optional[str],
    context: Optional[str],
    dialect: Optional[str],
    realm: Optional[str],
    output: Optional[str],
    strict: bool
):
    """Translate English to te reo Māori.
    
    TEXT: Text to translate (or use --file)
    
    Examples:
        tehau translate to-maori "Hello world"
        tehau translate to-maori --file doc.txt --output doc.mi.txt
        tehau translate to-maori "Welcome" --realm my-project
    """
    from te_hau.translator.ahiatoa import get_ahiatoa
    
    # Get text to translate
    if file:
        with open(file, 'r') as f:
            text = f.read()
    elif text is None:
        # Read from stdin
        if not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            raise click.ClickException("Provide text, --file, or pipe input")
    
    # Get Ahiatoa instance
    ahiatoa = get_ahiatoa(realm)
    
    if dialect:
        ahiatoa.set_dialect(dialect)
    
    ahiatoa.strict_glossary = strict
    
    # Load realm glossary if specified
    if realm:
        if not realm_exists(realm):
            raise click.ClickException(f"Realm '{realm}' not found")
        
        glossary_path = get_projects_path() / realm / "mauri" / "glossary.json"
        if glossary_path.exists():
            from te_hau.translator.glossary import Glossary
            realm_glossary = Glossary.from_file(glossary_path)
            ahiatoa.set_glossary(realm_glossary)
            click.echo(f"📚 Using glossary from '{realm}'", err=True)
    
    # Translate
    click.echo("🌿 Translating to te reo Māori...", err=True)
    
    try:
        result = ahiatoa.translate_to_maori(text, context=context)
    except Exception as e:
        raise click.ClickException(f"Translation failed: {e}")
    
    # Output
    if output:
        with open(output, 'w') as f:
            f.write(result)
        click.echo(f"✅ Saved to {output}", err=True)
    else:
        click.echo(result)


@cmd_translate.command("to-english")
@click.argument('text', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Translate from file')
@click.option('--preserve', '-p', is_flag=True, default=True, help='Preserve cultural terms')
@click.option('--realm', '-r', help='Use realm context')
@click.option('--output', '-o', type=click.Path(), help='Output file')
def cmd_to_english(
    text: Optional[str],
    file: Optional[str],
    preserve: bool,
    realm: Optional[str],
    output: Optional[str]
):
    """Translate te reo Māori to English.
    
    TEXT: Text to translate (or use --file)
    
    Examples:
        tehau translate to-english "Kia ora te ao"
        tehau translate to-english --file doc.mi.txt
    """
    from te_hau.translator.ahiatoa import get_ahiatoa
    
    # Get text to translate
    if file:
        with open(file, 'r') as f:
            text = f.read()
    elif text is None:
        if not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            raise click.ClickException("Provide text, --file, or pipe input")
    
    # Get Ahiatoa instance
    ahiatoa = get_ahiatoa(realm)
    
    # Translate
    click.echo("🌿 Translating to English...", err=True)
    
    try:
        result = ahiatoa.translate_to_english(text, preserve_cultural_terms=preserve)
    except Exception as e:
        raise click.ClickException(f"Translation failed: {e}")
    
    # Output
    if output:
        with open(output, 'w') as f:
            f.write(result)
        click.echo(f"✅ Saved to {output}", err=True)
    else:
        click.echo(result)


@cmd_translate.command("validate")
@click.argument('original')
@click.argument('translation')
@click.option('--realm', '-r', help='Use realm glossary')
def cmd_validate(original: str, translation: str, realm: Optional[str]):
    """Validate a translation for quality.
    
    ORIGINAL: Original text
    TRANSLATION: Translated text
    
    Examples:
        tehau translate validate "Hello" "Kia ora"
    """
    from te_hau.translator.ahiatoa import get_ahiatoa
    
    ahiatoa = get_ahiatoa(realm)
    
    report = ahiatoa.validate_translation(original, translation)
    
    if report['valid']:
        click.echo("✅ Translation validated")
    else:
        click.echo("⚠️  Translation has issues:")
        for issue in report['issues']:
            click.echo(f"   - {issue}")
    
    if report['suggestions']:
        click.echo("")
        click.echo("💡 Suggestions:")
        for suggestion in report['suggestions']:
            click.echo(f"   - {suggestion}")


@cmd_translate.command("lookup")
@click.argument('term')
@click.option('--direction', '-d', type=click.Choice(['en-mi', 'mi-en']), default='en-mi',
              help='Translation direction')
@click.option('--realm', '-r', help='Use realm glossary')
def cmd_lookup(term: str, direction: str, realm: Optional[str]):
    """Look up a term in the glossary.
    
    TERM: Term to look up
    
    Examples:
        tehau translate lookup "guardian"
        tehau translate lookup "kaitiaki" --direction mi-en
    """
    from te_hau.translator.ahiatoa import get_ahiatoa
    
    ahiatoa = get_ahiatoa(realm)
    
    dir_code = 'en_to_mi' if direction == 'en-mi' else 'mi_to_en'
    result = ahiatoa.get_term(term, dir_code)
    
    if result:
        arrow = "→" if direction == 'en-mi' else "←"
        click.echo(f"{term} {arrow} {result}")
    else:
        click.echo(f"'{term}' not found in glossary")


@cmd_translate.command("glossary")
@click.option('--realm', '-r', help='Realm to manage glossary for')
@click.option('--show', is_flag=True, help='Show glossary contents')
@click.option('--add', nargs=2, type=str, metavar='ENGLISH MAORI', help='Add term')
@click.option('--remove', type=str, help='Remove term by English key')
@click.option('--export', type=click.Path(), help='Export glossary to file')
@click.option('--import-file', 'import_path', type=click.Path(exists=True), help='Import glossary from file')
def cmd_glossary(
    realm: Optional[str],
    show: bool,
    add: Optional[tuple],
    remove: Optional[str],
    export: Optional[str],
    import_path: Optional[str]
):
    """Manage translation glossary.
    
    Examples:
        tehau translate glossary --show
        tehau translate glossary --add "water" "wai"
        tehau translate glossary --realm my-project --show
    """
    from te_hau.translator.glossary import get_default_glossary, Glossary
    
    # Determine glossary location
    if realm:
        if not realm_exists(realm):
            raise click.ClickException(f"Realm '{realm}' not found")
        glossary_path = get_projects_path() / realm / "mauri" / "glossary.json"
    else:
        # Global glossary
        glossary_path = Path.home() / ".awaos" / "glossary.json"
    
    # Load or create glossary
    if glossary_path.exists():
        glossary = Glossary.from_file(glossary_path)
    else:
        glossary = get_default_glossary()
    
    # Handle operations
    if add:
        english, maori = add
        glossary.add(english, maori)
        glossary_path.parent.mkdir(parents=True, exist_ok=True)
        glossary.save(glossary_path)
        click.echo(f"✅ Added: {english} → {maori}")
        return
    
    if remove:
        if glossary.remove(remove):
            glossary.save(glossary_path)
            click.echo(f"✅ Removed: {remove}")
        else:
            click.echo(f"'{remove}' not found")
        return
    
    if export:
        glossary.save(export)
        click.echo(f"✅ Exported to {export}")
        return
    
    if import_path:
        imported = Glossary.from_file(import_path)
        # Merge
        for term in imported.terms:
            glossary.add(term['english'], term['maori'], term.get('context'))
        glossary_path.parent.mkdir(parents=True, exist_ok=True)
        glossary.save(glossary_path)
        click.echo(f"✅ Imported {len(imported.terms)} terms")
        return
    
    # Default: show
    if show or True:  # Always show if no operation
        click.echo("📚 Glossary")
        click.echo("")
        
        terms = glossary.terms  # Dict[str, Dict]
        if not terms:
            click.echo("(empty)")
            return
        
        # Group by first letter
        click.echo(f"{len(terms)} terms:")
        click.echo("")
        
        # terms is a dict, get values
        term_list = list(terms.values())
        for term in sorted(term_list, key=lambda t: t['english'].lower()):
            eng = term['english']
            mao = term['maori']
            ctx = term.get('context', '')
            ctx_str = f" ({ctx})" if ctx else ""
            click.echo(f"  {eng} → {mao}{ctx_str}")


@cmd_translate.command("fix-macrons")
@click.argument('text', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Fix macrons in file')
@click.option('--output', '-o', type=click.Path(), help='Output file')
@click.option('--in-place', '-i', is_flag=True, help='Edit file in place')
def cmd_fix_macrons(
    text: Optional[str],
    file: Optional[str],
    output: Optional[str],
    in_place: bool
):
    """Fix missing or incorrect macrons in Māori text.
    
    TEXT: Text to fix (or use --file)
    
    Examples:
        tehau translate fix-macrons "Maori"
        tehau translate fix-macrons --file doc.txt --in-place
    """
    from te_hau.translator.core import fix_macrons
    
    # Get text
    if file:
        with open(file, 'r') as f:
            text = f.read()
    elif text is None:
        if not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            raise click.ClickException("Provide text, --file, or pipe input")
    
    # Fix macrons
    result = fix_macrons(text)
    
    # Output
    if in_place and file:
        with open(file, 'w') as f:
            f.write(result)
        click.echo(f"✅ Fixed macrons in {file}", err=True)
    elif output:
        with open(output, 'w') as f:
            f.write(result)
        click.echo(f"✅ Saved to {output}", err=True)
    else:
        click.echo(result)


def _load_dialect_profiles() -> dict:
    """Load dialect profiles from project template or realm."""
    # Check multiple locations for dialect profiles
    search_paths = [
        Path(__file__).parent.parent.parent / "project_template" / "mauri" / "dialect_profiles.json",
        Path.home() / ".awaos" / "dialect_profiles.json",
    ]
    
    for path in search_paths:
        if path.exists():
            with open(path) as f:
                data = json.load(f)
                # Handle nested "dialects" wrapper
                if "dialects" in data:
                    return data["dialects"]
                return data
    
    # Default minimal profiles if none found
    return {
        "standard": {"name": "Standard", "description": "Standard te reo Māori"},
        "ngati_kuia": {"name": "Ngāti Kuia", "description": "Te Tauihu dialect"}
    }


def _get_dialect_names() -> list[str]:
    """Get list of available dialect names."""
    profiles = _load_dialect_profiles()
    return list(profiles.keys())


@cmd_translate.command("dialects")
@click.option('--verbose', '-v', is_flag=True, help='Show dialect details')
def cmd_dialects(verbose: bool):
    """List available dialect profiles.
    
    Examples:
        tehau translate dialects
        tehau translate dialects --verbose
    """
    profiles = _load_dialect_profiles()
    
    click.echo("🗣️  Available Dialect Profiles")
    click.echo("")
    
    for key, profile in profiles.items():
        name = profile.get("name", key)
        desc = profile.get("description", "")
        
        click.echo(f"  {key}")
        click.echo(f"    Name: {name}")
        if desc:
            click.echo(f"    Description: {desc}")
        
        if verbose:
            region = profile.get("region", "")
            if region:
                click.echo(f"    Region: {region}")
            
            macron_rules = profile.get("macron_rules", "")
            if macron_rules:
                # Handle both string and dict formats
                if isinstance(macron_rules, dict):
                    style = macron_rules.get('style', 'standard')
                else:
                    style = macron_rules
                click.echo(f"    Macron style: {style}")
            
            vocab = profile.get("vocab_overrides", {})
            if vocab:
                click.echo(f"    Vocabulary overrides: {len(vocab)} terms")
                # Show first 3
                for i, (k, v) in enumerate(vocab.items()):
                    if i >= 3:
                        remaining = len(vocab) - 3
                        click.echo(f"      ... and {remaining} more")
                        break
                    click.echo(f"      {k} → {v}")
        
        click.echo("")


@cmd_translate.command("with-dialect")
@click.argument('text')
@click.argument('dialect')
@click.option('--direction', '-d', type=click.Choice(['to-maori', 'to-english']), 
              default='to-maori', help='Translation direction')
@click.option('--realm', '-r', help='Use realm glossary')
def cmd_with_dialect(text: str, dialect: str, direction: str, realm: Optional[str]):
    """Translate using a specific dialect profile.
    
    TEXT: Text to translate
    DIALECT: Dialect profile name (use 'tehau translate dialects' to list)
    
    Examples:
        tehau translate with-dialect "Welcome" ngati_kuia
        tehau translate with-dialect "Kia ora" standard --direction to-english
    """
    from te_hau.translator.ahiatoa import get_ahiatoa
    
    # Validate dialect
    available = _get_dialect_names()
    if dialect not in available:
        raise click.ClickException(
            f"Unknown dialect '{dialect}'. Available: {', '.join(available)}"
        )
    
    # Load dialect profile
    profiles = _load_dialect_profiles()
    profile = profiles[dialect]
    
    # Get Ahiatoa
    ahiatoa = get_ahiatoa(realm)
    ahiatoa.set_dialect(dialect)
    
    # Apply vocab overrides from profile
    vocab_overrides = profile.get("vocab_overrides", {})
    if vocab_overrides:
        for eng, mao in vocab_overrides.items():
            ahiatoa.glossary.add(eng, mao, context=f"dialect:{dialect}")
    
    click.echo(f"🗣️  Using dialect: {profile.get('name', dialect)}", err=True)
    
    # Translate
    try:
        if direction == 'to-maori':
            result = ahiatoa.translate_to_maori(text)
        else:
            result = ahiatoa.translate_to_english(text)
    except Exception as e:
        raise click.ClickException(f"Translation failed: {e}")
    
    click.echo(result)
