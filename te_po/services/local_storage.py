import json
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "storage"

DIRS = {
    "raw": BASE / "raw",
    "clean": BASE / "clean",
    "chunks": BASE / "chunks",
    "openai": BASE / "openai",
    "logs": BASE / "logs",
}


def ensure_dirs():
    for p in DIRS.values():
        p.mkdir(parents=True, exist_ok=True)


ensure_dirs()


def save(stage: str, filename: str, content: str):
    path = DIRS[stage] / filename
    path.write_text(content, encoding="utf-8")
    return str(path)


def load(stage: str, filename: str):
    path = DIRS[stage] / filename
    return path.read_text(encoding="utf-8") if path.exists() else None


def list_files(stage: str):
    return [p.name for p in DIRS[stage].glob("*")]


def timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def append_audit(event: dict) -> None:
    """Append a JSON event to the project audit log (best-effort)."""
    try:
        audit_path = DIRS["logs"] / "project_audit.jsonl"
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        with open(audit_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        return
