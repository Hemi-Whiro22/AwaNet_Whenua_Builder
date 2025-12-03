import typer
from ..utils import api_post, pretty

app = typer.Typer(help="Manage OpenAI Pro tier activation")


@app.command("activate")
def activate(key: str):
    result = api_post("/pro/activate", {"key": key})
    pretty(result)
