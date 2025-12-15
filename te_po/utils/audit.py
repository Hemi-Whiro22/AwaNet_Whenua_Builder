from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from te_po.services.local_storage import append_audit
from te_po.services.supabase_logging import log_audit_event

MAURI_LEDGER = Path(__file__).resolve().parents[2] / "mauri" / "state" / "te_po_carving_log.jsonl"


def _append_mauri_ledger(event: dict) -> None:
    """Best-effort append to the Mauri carving ledger."""
    try:
        MAURI_LEDGER.parent.mkdir(parents=True, exist_ok=True)
        with open(MAURI_LEDGER, "a", encoding="utf-8") as fh:
            import json

            fh.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        return


def log_event(
    event_type: str,
    detail: str,
    source: Optional[str] = None,
    data: Optional[dict[str, Any]] = None,
) -> None:
    """Best-effort project audit log entry (storage + Mauri ledger)."""
    event = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "detail": detail,
        "source": source,
        "data": data or {},
    }
    try:
        append_audit(event)
    except Exception:
        pass
    _append_mauri_ledger(event)
    try:
        log_audit_event(event_type, detail, source=source, data=data or {})
    except Exception:
        pass
