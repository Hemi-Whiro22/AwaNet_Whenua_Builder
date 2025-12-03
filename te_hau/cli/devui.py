from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
import requests
import os

API = "http://localhost:8000"
console = Console()


def call(endpoint, method="get", files=None, data=None, json_body=None):
    url = f"{API}{endpoint}"
    try:
        if method == "post":
            response = requests.post(url, files=files, data=data, json=json_body, timeout=30)
        else:
            response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}


def dev_menu():
    while True:
        table = Table(title="Awa Developer Cockpit (Te Hau)")
        table.add_column("Option")
        table.add_column("Action")

        table.add_row("1", "Run OCR on test file")
        table.add_row("2", "Clean document")
        table.add_row("3", "Chunk document")
        table.add_row("4", "Send chunks to OpenAI")
        table.add_row("5", "Translate text (Māori ↔ English)")
        table.add_row("6", "Summarise")
        table.add_row("7", "Vector Embed (OpenAI)")
        table.add_row("8", "Open Output Folder")
        table.add_row("9", "Quit")

        console.print(table)
        choice = Prompt.ask("Select option")

        if choice == "1":
            console.print("[bold cyan]Running OCR...[/]")
            test_path = os.path.join("te_hau", "test_assets", "test.png")
            if not os.path.exists(test_path):
                console.print("[bold red]Missing test asset at te_hau/test_assets/test.png[/]")
            else:
                with open(test_path, "rb") as fh:
                    files = {"file": fh}
                    console.print(call("/dev/ocr", "post", files=files))

        elif choice == "2":
            console.print("[bold cyan]Cleaning raw text...[/]")
            console.print(call("/dev/clean"))

        elif choice == "3":
            console.print("[bold cyan]Chunking...[/]")
            console.print(call("/dev/chunk"))

        elif choice == "4":
            console.print("[bold cyan]Sending to OpenAI...[/]")
            console.print(call("/dev/openai"))

        elif choice == "5":
            text = Prompt.ask("Text to translate")
            console.print(call("/reo/translate", "post", data={"text": text}))

        elif choice == "6":
            text = Prompt.ask("Text to summarise")
            console.print(call("/dev/summarise", "post", data={"text": text}))

        elif choice == "7":
            console.print("[bold cyan]Embedding chunks...[/]")
            payload = Prompt.ask("Text to embed", default="Developer embedding test")
            console.print(call("/vector/embed", "post", json_body={"text": payload}))

        elif choice == "8":
            console.print("[bold cyan]Opening output folder...[/]")
            os.system("xdg-open te_po/storage/openai >/dev/null 2>&1")  # noqa: S605,S607

        elif choice == "9":
            break

        else:
            console.print("[yellow]Invalid selection[/]")
