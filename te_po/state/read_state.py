"""
State reading utilities for Te Po.
Reads from state.yaml and provides public/private state access.
"""
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

STATE_FILE = Path(__file__).resolve().parents[1] / "state.yaml"


def _load_state() -> Dict[str, Any]:
    """Load state from YAML file."""
    if not STATE_FILE.exists():
        return {"version": "0.0.0", "public": {}, "private": {}}
    
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {"version": "0.0.0", "public": {}, "private": {}}


def get_state_version() -> str:
    """Get current state version."""
    state = _load_state()
    return state.get("version", "0.0.0")


def get_public_state() -> Dict[str, Any]:
    """Get public (shareable) state."""
    state = _load_state()
    return state.get("public", state)


def get_private_state() -> Dict[str, Any]:
    """Get private (internal) state."""
    state = _load_state()
    return state.get("private", {})


def get_full_state() -> Dict[str, Any]:
    """Get full state object."""
    return _load_state()
