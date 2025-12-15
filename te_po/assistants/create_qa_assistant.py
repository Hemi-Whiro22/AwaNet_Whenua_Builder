#!/usr/bin/env python3
"""
Create a QA assistant + vector store for the UI retrieval path and persist IDs to te_po/core/.env.
- Skips creation if OPENAI_ASSISTANT_ID_QA is already set.
- Creates a vector store if OPENAI_VECTOR_STORE_ID is missing.
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


def ensure_vector_store(client: OpenAI) -> str:
    vs_id = os.getenv("OPENAI_VECTOR_STORE_ID")
    if vs_id:
        print(f"OPENAI_VECTOR_STORE_ID already set: {vs_id}")
        return vs_id
    vs = client.beta.vector_stores.create(name="Kitenga QA Store")
    set_env_var("OPENAI_VECTOR_STORE_ID", vs.id)
    print(f"Created vector store: {vs.id} (saved to .env)")
    return vs.id


def ensure_assistant(client: OpenAI, vector_store_id: str) -> str:
    asst_id = os.getenv("OPENAI_ASSISTANT_ID_QA")
    if asst_id:
        print(f"OPENAI_ASSISTANT_ID_QA already set: {asst_id}")
        return asst_id

    assistant = client.beta.assistants.create(
        name="Kitenga QA",
        model="gpt-4o-mini",
        instructions="Answer questions with retrieval over the attached vector store. Be concise and cite sources when possible.",
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vector_store_id]}},
    )
    set_env_var("OPENAI_ASSISTANT_ID_QA", assistant.id)
    print(f"Created assistant: {assistant.id} (saved to .env)")
    return assistant.id


def main():
    load_env()
    client = OpenAI()
    vs_id = ensure_vector_store(client)
    ensure_assistant(client, vs_id)


if __name__ == "__main__":
    main()
