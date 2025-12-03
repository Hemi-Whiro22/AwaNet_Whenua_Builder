#!/usr/bin/env python3
"""
Create an OpenAI vector store and persist the ID to te_po/core/.env.
Skips creation if OPENAI_VECTOR_STORE_ID is already set.
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
    """Append or replace a key in te_po/core/.env."""
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
    existing = os.getenv("OPENAI_VECTOR_STORE_ID")
    if existing:
        print(f"OPENAI_VECTOR_STORE_ID already set: {existing} (skip create)")
        return

    client = OpenAI()
    print("Creating vector store: kitenga_whiro_memory ...")
    vs = client.vector_stores.create(name="kitenga_whiro_memory")
    vs_id = vs.id
    print(f"Created vector store id: {vs_id}")
    set_env_var("OPENAI_VECTOR_STORE_ID", vs_id)
    print(f"Saved OPENAI_VECTOR_STORE_ID to {ENV_PATH}")


if __name__ == "__main__":
    main()
