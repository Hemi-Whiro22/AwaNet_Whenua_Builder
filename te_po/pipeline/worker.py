from __future__ import annotations

from rq import Worker

from te_po.pipeline.queue import redis_conn


def main():
    if redis_conn is None:
        raise SystemExit("Redis connection unavailable. Set REDIS_URL or run Redis on localhost:6379")
    worker = Worker(["pipeline"], connection=redis_conn)
    worker.work()


if __name__ == "__main__":
    main()
