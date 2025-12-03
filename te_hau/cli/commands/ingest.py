import typer
from pathlib import Path
from ..utils import api_post, pretty

app = typer.Typer(help="Taonga ingest pipeline")


@app.command("file")
def ingest_file(path: str):
    fp = Path(path)
    if not fp.exists():
        typer.echo("❌ File not found.")
        raise typer.Exit()

    # backend expects {"path": "..."}
    result = api_post("/intake/process", {"path": str(fp)})
    pretty(result)
