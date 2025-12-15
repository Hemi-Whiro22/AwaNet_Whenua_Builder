import json
import shutil
import stat
import subprocess
from pathlib import Path
from datetime import datetime

import click

from kaitiaki.kaitiaki import KitengaWhiro
from te_hau.cli.devui import dev_menu
from te_hau.services.sound import bad, good
from te_hau.services.tepo_api import te_po_get, te_po_post

kaitiaki = KitengaWhiro()


@click.group(help="🌬️  Te Hau — CLI for Kitenga Whiro.")
def cli():
    pass


def _echo_result(label: str, result: dict):
    click.echo(f"{label}:")
    click.echo(json.dumps(result, ensure_ascii=False, indent=2))


def _run_with_cue(label: str, fn):
    try:
        result = fn()
        good()
        _echo_result(label, result)
    except Exception as exc:  # noqa: BLE001
        bad()
        raise click.ClickException(str(exc)) from exc


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def ocr(path):
    """OCR an image file."""
    _run_with_cue("OCR", lambda: kaitiaki.invoke("ingest.ocr", {"file": path}))


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--mode", type=click.Choice(["research", "taonga"]), default="research")
def summarize(path, mode):
    """Summarize a text file."""
    text = Path(path).read_text(encoding="utf-8")
    _run_with_cue("Summary", lambda: kaitiaki.invoke("ingest.summarize", {"text": text, "mode": mode}))


@cli.command()
@click.argument("text")
def translate(text):
    """Translate English to reo Māori."""
    _run_with_cue("Translate", lambda: kaitiaki.invoke("reo.translate", {"text": text}))


@cli.command()
@click.argument("text")
def explain(text):
    """Explain reo Māori text in English."""
    _run_with_cue("Explain", lambda: kaitiaki.invoke("reo.explain", {"text": text}))


@cli.command()
@click.argument("text")
def pronounce(text):
    """Provide phonetic reo Māori pronunciation."""
    _run_with_cue("Pronounce", lambda: kaitiaki.invoke("reo.pronounce", {"text": text}))


@cli.command()
@click.argument("text")
def embed(text):
    """Embed text into the local vector store."""
    _run_with_cue("Embed", lambda: kaitiaki.invoke("vector.embed", {"text": text}))


@cli.command()
@click.argument("text")
@click.option("--top-k", default=5, show_default=True)
@click.option("--no-rerank", is_flag=True, help="Skip model rerank.")
def search(text, top_k, no_rerank):
    """Search the local vector index."""
    _run_with_cue(
        "Search", lambda: kaitiaki.invoke("vector.search", {"query": text, "top_k": top_k, "rerank": not no_rerank})
    )


@cli.command()
@click.argument("question")
def research(question):
    """Send a research query to Te Pō."""
    _run_with_cue("Research", lambda: te_po_post("/research/query", {"query": question}))


@cli.command()
def status():
    """Check Te Pō status via Te Hau API bridge."""
    _run_with_cue("Status", lambda: te_po_get("/status"))


@cli.command()
def dev():
    """Launch Developer Cockpit."""
    dev_menu()


def _load_template_config(template_dir: Path) -> dict:
    config_path = template_dir / "template.config.json"
    if not config_path.exists():
        return {}
    with config_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _load_archetypes(template_dir: Path) -> dict[str, dict]:
    path = template_dir / "archetypes.json"
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return {entry["slug"]: entry for entry in data}


def _write_cli_log(dest_path: Path, payload: dict) -> None:
    log_path = dest_path / ".te_hau_cli.log"
    payload["timestamp"] = datetime.utcnow().isoformat() + "Z"
    log_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _print_secret_summary(config: dict) -> None:
    secret_defs = config.get("secrets", [])
    if not secret_defs:
        click.echo("No secrets metadata found; see docs/secrets.md.")
        return
    click.echo("\nSecrets checklist (store before deployment):")
    header = f"{'Secret':20} | {'Description':45} | {'Scopes':20}"
    click.echo(header)
    click.echo("-" * len(header))
    for entry in secret_defs:
        if isinstance(entry, str):
            click.echo(f"{entry:20} | {'(see docs/secrets.md)':45} | {'env':20}")
            continue
        scopes = ", ".join(entry.get("scopes", [])) or "env"
        desc = entry.get("description", "")
        key = entry.get("key", "unknown")
        click.echo(f"{key:20} | {desc[:45]:45} | {scopes:20}")


def _write_secrets_file(dest_path: Path, secret_defs: list[dict | str]) -> None:
    if not secret_defs:
        return
    lines = ["# Secrets Checklist", "", "| Secret | Description | Scopes |", "| --- | --- | --- |"]
    for entry in secret_defs:
        if isinstance(entry, str):
            lines.append(f"| {entry} | see docs/secrets.md | env |")
        else:
            scopes = ", ".join(entry.get("scopes", [])) or "env"
            lines.append(f"| {entry.get('key','')} | {entry.get('description','')} | {scopes} |")
    (dest_path / "SECRETS_CHECKLIST.md").write_text("\n".join(lines), encoding="utf-8")


def _apply_archetype(dest_path: Path, archetype: dict, tools: list[str], archetype_slug: str) -> None:
    if not archetype:
        return

    def _update_json(path: Path, updater):
        data = json.loads(path.read_text(encoding="utf-8"))
        updater(data)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    config_path = dest_path / "config" / "realm.json"
    if config_path.exists():
        def upd_realm(data):
            data["panels"] = archetype.get("panels", data.get("panels", []))
            data["features"] = archetype.get("features", data.get("features", {}))
        _update_json(config_path, upd_realm)

    lock_path = dest_path / "mauri" / "realm_lock.json"
    if lock_path.exists():
        def upd_lock(data):
            data["allowed_panels"] = archetype.get("panels", data.get("allowed_panels", []))
            data["archetype"] = archetype_slug
        _update_json(lock_path, upd_lock)

    den_manifest = dest_path / "mauri" / "state" / "den_manifest.json"
    if den_manifest.exists():
        def upd_manifest(data):
            data["name"] = archetype.get("title", data.get("name"))
            data["description"] = archetype.get("description", data.get("description"))
            if tools:
                data["tools"] = tools
        _update_json(den_manifest, upd_manifest)

    tools_path = dest_path / "config" / "tools_enabled.json"
    tools_path.write_text(json.dumps({"tools": tools}, indent=2), encoding="utf-8")


def _write_context_seed(dest_path: Path, realm: str, summary: str) -> None:
    target = dest_path / "context" / "context_seed.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "realm": realm,
        "summary": summary,
        "notes": "Generated via te_hau CLI",
    }
    target.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _write_readme(dest_path: Path, realm: str, archetype: dict, cf_info: dict, tools: list[str]) -> None:
    readme = dest_path / "README.md"
    lines = [
        f"# {realm} Realm",
        "",
        f"Archetype: **{archetype.get('title','n/a')}**" if archetype else "Archetype: custom",
        "",
        "## Bootstrap Summary",
        f"- Cloudflare hostname: `{cf_info['host']}`",
        f"- Cloudflare Pages project: `{cf_info['pages']}`",
        f"- Backend URL: `{cf_info['backend']}`",
        f"- Tools enabled: {', '.join(tools) if tools else 'none'}",
        "",
        "## Next Steps",
        "- Update `.env` with real secrets (see `SECRETS_CHECKLIST.md`).",
        "- Run `scripts/seed_context.py --write` to add more context and push to Supabase.",
        "- Deploy frontend via Cloudflare Pages workflow.",
        "- Deploy backend wherever you host mini_te_po.",
    ]
    readme.write_text("\n".join(lines), encoding="utf-8")


@cli.command("new-project")
@click.option(
    "--template-dir",
    default=lambda: Path(__file__).resolve().parents[1] / "project_template",
    help="Path to project template directory.",
    type=click.Path(path_type=Path),
)
@click.option("--realm", prompt="Realm / project name", help="New realm/project name.")
@click.option("--dest", type=click.Path(path_type=Path), help="Destination directory (defaults to ./<realm>).")
@click.option("--cf-host", help="Cloudflare hostname (kitenga-<realm>.example.com).")
@click.option("--cf-tunnel-id", help="Cloudflare Tunnel ID.")
@click.option("--cf-tunnel-name", help="Cloudflare Tunnel name.")
@click.option("--cf-pages-project", help="Cloudflare Pages project name.")
@click.option("--backend-url", help="Public backend URL (https://<realm>.example.com).")
@click.option("--bootstrap/--no-bootstrap", default=False, help="Run template bootstrap script.")
@click.option("--git-init/--no-git-init", default=True, help="Initialize git repository in destination.")
@click.option("--remote", help="Optional git remote URL to add after init.")
@click.option("--push/--no-push", default=False, help="Push to remote after committing (requires --remote).")
def new_project(
    template_dir,
    realm,
    dest,
    cf_host,
    cf_tunnel_id,
    cf_tunnel_name,
    cf_pages_project,
    backend_url,
    bootstrap,
    git_init,
    remote,
    push,
):
    """Instantiate the SDK project template with Cloudflare wiring."""
    template_dir = Path(template_dir).expanduser().resolve()
    if not template_dir.exists():
        raise click.ClickException(f"Template directory not found: {template_dir}")

    slug = realm.lower().replace(" ", "-")
    default_cf_host = cf_host or f"kitenga-{slug}.example.com"
    default_tunnel_name = cf_tunnel_name or f"kitenga-{slug}"
    default_pages_project = cf_pages_project or f"te-ao-{slug}"
    default_backend_url = backend_url or f"https://{slug}.example.com"

    cf_host = cf_host or click.prompt("Cloudflare hostname", default=default_cf_host)
    cf_tunnel_id = cf_tunnel_id or click.prompt("Cloudflare Tunnel ID", default="", show_default=False)
    if not cf_tunnel_id:
        raise click.ClickException("Cloudflare Tunnel ID is required.")
    cf_tunnel_name = cf_tunnel_name or click.prompt("Cloudflare Tunnel name", default=default_tunnel_name)
    cf_pages_project = cf_pages_project or click.prompt("Cloudflare Pages project", default=default_pages_project)
    backend_url = backend_url or click.prompt("Public backend URL", default=default_backend_url)
    context_summary = click.prompt(
        "Context summary (stored in context/context_seed.json)",
        default=f"{realm} realm born via Te Hau CLI.",
    )

    dest_path = Path(dest).expanduser().resolve() if dest else Path.cwd() / realm
    if dest_path.exists():
        raise click.ClickException(f"Destination already exists: {dest_path}")

    config = _load_template_config(template_dir)
    archetypes = _load_archetypes(template_dir)
    archetype_slug = None
    archetype = None
    selected_tools: list[str] = []
    if archetypes:
        choices = list(archetypes.keys())
        archetype_slug = click.prompt(
            "Archetype",
            type=click.Choice(choices),
            default=choices[0],
        )
        archetype = archetypes[archetype_slug]
        click.echo(f"Selected archetype: {archetype.get('title')} — {archetype.get('description')}")
        default_tools = archetype.get("tools", [])
        click.echo(f"Default tools: {', '.join(default_tools) if default_tools else 'none'}")
        extra_tools = click.prompt("Additional tools (comma separated)", default="")
        extra_list = [t.strip() for t in extra_tools.split(",") if t.strip()]
        selected_tools = sorted({*default_tools, *extra_list})

    click.echo(f"Creating project at {dest_path} from {template_dir} ...")
    shutil.copytree(template_dir, dest_path)

    new_realm_script = dest_path / "scripts" / "new_realm.sh"
    bootstrap_script = dest_path / "scripts" / "bootstrap.sh"
    for script in (new_realm_script, bootstrap_script):
        if script.exists():
            script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    cmd = [
        "./scripts/new_realm.sh",
        "--hostname",
        cf_host,
        "--tunnel-id",
        cf_tunnel_id,
        "--tunnel-name",
        cf_tunnel_name,
        "--pages-project",
        cf_pages_project,
        "--backend-url",
        backend_url,
        realm,
    ]
    subprocess.run(cmd, cwd=dest_path, check=True)
    if archetype:
        _apply_archetype(dest_path, archetype, selected_tools, archetype_slug or "")

    _write_context_seed(dest_path, realm, context_summary)
    _write_secrets_file(dest_path, config.get("secrets", []))
    _write_readme(
        dest_path,
        realm,
        archetype or {},
        {"host": cf_host, "pages": cf_pages_project, "backend": backend_url},
        selected_tools,
    )

    if bootstrap:
        click.echo("Running bootstrap script (installs deps)...")
        subprocess.run(["./scripts/bootstrap.sh"], cwd=dest_path, check=True)

    if git_init:
        click.echo("Initializing git repository...")
        subprocess.run(["git", "init"], cwd=dest_path, check=True)
        subprocess.run(["git", "add", "."], cwd=dest_path, check=True)
        subprocess.run(["git", "commit", "-m", f"chore: bootstrap {realm}"], cwd=dest_path, check=True)
        if remote:
            subprocess.run(["git", "remote", "add", "origin", remote], cwd=dest_path, check=True)
            if push:
                subprocess.run(["git", "push", "-u", "origin", "HEAD"], cwd=dest_path, check=True)
        elif push:
            raise click.ClickException("--push requested but no --remote supplied.")

    _write_cli_log(
        dest_path,
        {
            "realm": realm,
            "cloudflare_hostname": cf_host,
            "cloudflare_pages_project": cf_pages_project,
            "backend_url": backend_url,
            "template_dir": str(template_dir),
            "archetype": archetype_slug,
            "tools": selected_tools,
            "context_summary": context_summary,
        },
    )

    click.echo("✅ Project template instantiated.")
    click.echo(f"- Location: {dest_path}")
    click.echo(f"- Cloudflare hostname: {cf_host}")
    click.echo(f"- Cloudflare Pages project: {cf_pages_project}")
    click.echo("Next steps: configure secrets per docs/secrets.md and deploy via Cloudflare Pages.")
    _print_secret_summary(config)


def main():
    cli()


if __name__ == "__main__":
    main()
