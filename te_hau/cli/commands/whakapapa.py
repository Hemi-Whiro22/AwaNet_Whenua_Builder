import typer
from ..utils import pretty, api_get

app = typer.Typer(help="Export Kaitiaki whakapapa")


@app.command("export")
def export():
    result = api_get("/whakapapa/export")
    pretty(result)
