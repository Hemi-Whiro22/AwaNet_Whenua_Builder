import json
from pathlib import Path

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


def main():
    cli()


if __name__ == "__main__":
    main()
