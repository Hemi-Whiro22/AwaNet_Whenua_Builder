"""
Service helpers for pipeline-facing API routes.
"""

from __future__ import annotations

from fastapi import HTTPException

from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline
from te_po.utils.audit import log_event


def handle_pipeline_run(data: bytes, filename: str, source: str) -> dict:
    """
    Thin wrapper around run_pipeline used by /pipeline/run.
    """
    result = run_pipeline(data, filename, source=source)
    log_event(
        "pipeline_run",
        "Pipeline executed",
        source=source,
        data={"filename": filename, "result": result},
    )
    return result
