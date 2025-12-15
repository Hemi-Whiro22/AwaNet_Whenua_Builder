import os

from dotenv import load_dotenv

load_dotenv()


def read_file(ctx, path: str):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def list_files(ctx, path: str):
    return os.listdir(path)
