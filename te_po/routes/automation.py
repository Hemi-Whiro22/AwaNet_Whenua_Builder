import os
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/automation", tags=["Automation"])


class GitChecklistPayload(BaseModel):
    message: str = Field(..., description="Git commit message to use after running the checklist")


def _run_git_checklist(message: str) -> str:
    repo_root = Path(__file__).resolve().parents[2]
    script = repo_root / "scripts" / "git_commit_pipeline.py"
    if not script.exists():
        raise FileNotFoundError(f"Checklist script missing at {script}")

    env = os.environ.copy()
    prev_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{repo_root}:{prev_pythonpath}" if prev_pythonpath else str(repo_root)

    cmd = [sys.executable, str(script), "-m", message]
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or "Checklist failed without stderr")
    return result.stdout.strip()


@router.post("/git-checklist", summary="Run Git checklist + push")
def run_git_checklist(payload: GitChecklistPayload):
    try:
        output = _run_git_checklist(payload.message)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return {"status": "completed", "message": payload.message, "output": output}
