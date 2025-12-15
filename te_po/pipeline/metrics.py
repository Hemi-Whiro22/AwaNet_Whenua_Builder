from __future__ import annotations

import time
from functools import wraps

from prometheus_client import Counter, Histogram

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


__all__ = ["track_job", "jobs_total", "jobs_failed", "job_duration"]
