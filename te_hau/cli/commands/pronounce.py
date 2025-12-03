import typer
from ..utils import api_post, pretty

app = typer.Typer(help="Māori pronunciation engine")


@app.command("say")
def pronounce(text: str):
    result = api_post("/reo/pronounce", {"text": text})
    pretty(result)
