from __future__ import annotations

import time
from functools import wraps

import logging
from typing import Any

try:
    from prometheus_client import Counter, Histogram
except ImportError:  # pragma: no cover
    class _DummyMetric:
        def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
            pass

        def inc(self, amount: float = 1) -> None:  # pragma: no cover
            pass

        def observe(self, value: float) -> None:  # pragma: no cover
            pass

    Counter = _DummyMetric
    Histogram = _DummyMetric

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None

jobs_total = Counter("jobs_total", "Total pipeline jobs processed")
jobs_failed = Counter("jobs_failed", "Pipeline jobs that failed")
job_duration = Histogram("job_duration_seconds", "Pipeline job duration seconds")


def track_job(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            jobs_total.inc()
            job_duration.observe(time.time() - start)
            return result
        except Exception:
            jobs_failed.inc()
            raise

    return wrapper


def log_memory_usage(stage: str):
    """
    Logs the memory usage of the current process.

    Args:
        stage (str): The stage of the pipeline to log memory for.
    """
    if psutil is None:
        logging.debug("psutil not available; skipping memory usage log.")
        return
    process = psutil.Process()
    memory_info = process.memory_info()
    logging.info(
        f"[Memory Usage] Stage: {stage}, RSS: {memory_info.rss / 1024 ** 2:.2f} MB, "
        f"VMS: {memory_info.vms / 1024 ** 2:.2f} MB",
    )


__all__ = ["track_job", "jobs_total", "jobs_failed", "job_duration"]
