import typer
from ..utils import api_post, pretty

app = typer.Typer(help="Reo Māori translation + review")


@app.command("translate")
def translate(text: str):
    result = api_post("/reo/translate", {"text": text})
    pretty(result)


@app.command("review")
def review(text: str):
    result = api_post("/reo/review", {"text": text})
    pretty(result)
