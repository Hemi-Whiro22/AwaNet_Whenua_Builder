from __future__ import annotations

from pathlib import Path

from te_po.pipeline.orchestrator.pipeline_orchestrator import run_pipeline

FILES = [
    Path("docs/CONTEXT_PACK.md"),
    Path("docs/PROJECT_STATE_SYNC.md"),
]


def main() -> None:
    for path in FILES:
        if not path.exists():
            print(f"⚠️  Sanity file missing: {path}")
            continue
        print(f"🛡️  Running pipeline on {path}")
        res = run_pipeline(
            path.read_bytes(),
            filename=path.name,
            source="kaitiaki_sanity",
            generate_summary=True,
        )
        print(res)


if __name__ == "__main__":
    main()
