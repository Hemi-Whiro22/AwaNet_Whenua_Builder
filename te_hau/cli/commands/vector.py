import typer
from ..utils import api_post, pretty

app = typer.Typer(help="Semantic vector search")


@app.command("search")
def search(query: str):
    result = api_post("/vector/search", {"query": query})
    pretty(result)
