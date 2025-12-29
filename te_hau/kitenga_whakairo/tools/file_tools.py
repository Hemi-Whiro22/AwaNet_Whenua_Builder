from pathlib import Path
from typing import Any, List


def read_file(ctx: Any, path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def list_files(ctx: Any, path: str) -> List[str]:
    return [p.name for p in Path(path).iterdir()]
