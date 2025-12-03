from pathlib import Path


def get_data_dir(*parts: str) -> Path:
    """
    Resolve the canonical data directory, preferring backend/te_po/data when present.
    Ensures the requested subpath exists.
    """
    current = Path(__file__).resolve()
    root = current.parents[1]
    for candidate in current.parents:
        if (candidate / "te_po").exists() or (candidate / "backend" / "te_po").exists():
            root = candidate
            break

    candidates = [
        root / "backend" / "te_po" / "data",
        root / "te_po" / "data",
        root / "data",
    ]

    for base in candidates:
        try:
            base.mkdir(parents=True, exist_ok=True)
        except Exception:
            continue
        target = base.joinpath(*parts)
        target.mkdir(parents=True, exist_ok=True)
        return target

    target = root.joinpath(*parts)
    target.mkdir(parents=True, exist_ok=True)
    return target
