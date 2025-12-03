import typer
from rich import print
from ..utils import api_get, pretty

app = typer.Typer(help="Health & diagnostics")


@app.command("full")
def full_health():
    """Run the full Te Pō / Kaitiaki health sweep."""
    result = api_get("/health/full")
    pretty(result)


@app.command("ping")
def ping():
    """Quick check if Te Pō is alive."""
    result = api_get("/health/ping")
    pretty(result)
