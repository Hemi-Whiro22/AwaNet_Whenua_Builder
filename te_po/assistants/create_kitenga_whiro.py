#!/usr/bin/env python3
"""
Create an OpenAI assistant for Kitenga Whiro with tool calls and persist the ID to te_po/core/.env.
Skips creation if KITENGA_ASSISTANT_ID is already set.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / "core" / ".env"


def load_env() -> None:
    load_dotenv(ENV_PATH)


def set_env_var(key: str, value: str) -> None:
    lines = []
    if ENV_PATH.exists():
        lines = ENV_PATH.read_text().splitlines()
    updated = False
    for idx, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[idx] = f"{key}={value}"
            updated = True
            break
    if not updated:
        lines.append(f"{key}={value}")
    ENV_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    load_env()
    existing = os.getenv("KITENGA_ASSISTANT_ID")
    if existing:
        print(f"KITENGA_ASSISTANT_ID already set: {existing} (skip create)")
        return

    client = OpenAI()

    tools = [
        {"type": "code_interpreter"},
        {"type": "file_search"},
        {
            "type": "function",
            "function": {
                "name": "run_pipeline",
                "description": "Send a file reference or text to the local FastAPI endpoint /pipeline/run for OCR+embedding.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_url": {"type": "string", "description": "URL to fetch the file to process"},
                        "text": {"type": "string", "description": "Inline text to process if file_url is not provided"},
                        "source": {"type": "string", "description": "Label or source tag for the run"},
                    },
                    "required": [],
                },
            },
        },
    ]

    assistant = client.beta.assistants.create(
        name="Kitenga Whiro",
        model="gpt-4o",
        instructions="Kitenga Whiro orchestrates OCR, cleaning, chunking, and embedding via local pipeline /pipeline/run.",
        tools=tools,
    )

    asst_id = assistant.id
    print(f"Created assistant id: {asst_id}")
    set_env_var("KITENGA_ASSISTANT_ID", asst_id)
    print(f"Saved KITENGA_ASSISTANT_ID to {ENV_PATH}")


if __name__ == "__main__":
    main()
