"""Project state management for Kitenga - captures live project snapshot."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

from te_po.utils.supabase_client import get_client
from te_po.utils.audit import log_event


def get_git_status() -> Dict[str, Any]:
    """Capture current git state - recent commits, branch, changes."""
    try:
        repo_path = "/workspaces/The_Awa_Network"
        
        # Get current branch
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=repo_path,
            text=True,
        ).strip()
        
        # Get last 5 commits
        commits = subprocess.check_output(
            ["git", "log", "--oneline", "-5"],
            cwd=repo_path,
            text=True,
        ).strip().split("\n")
        
        # Get status summary
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            text=True,
        ).strip()
        
        return {
            "branch": branch,
            "recent_commits": commits,
            "has_changes": len(status) > 0,
            "status_summary": status[:500] if status else "clean",
        }
    except Exception as e:
        log_event("git_status_error", str(e))
        return {"error": str(e)}


def get_project_structure() -> Dict[str, Any]:
    """Capture current project structure - services, routes, models."""
    try:
        te_po_path = "/workspaces/The_Awa_Network/te_po"
        
        return {
            "services": list(os.listdir(f"{te_po_path}/services")) if os.path.exists(f"{te_po_path}/services") else [],
            "routes": list(os.listdir(f"{te_po_path}/routes")) if os.path.exists(f"{te_po_path}/routes") else [],
            "models": list(os.listdir(f"{te_po_path}/models")) if os.path.exists(f"{te_po_path}/models") else [],
        }
    except Exception as e:
        log_event("project_structure_error", str(e))
        return {"error": str(e)}


def capture_project_snapshot() -> Dict[str, Any]:
    """Capture complete project state snapshot."""
    snapshot = {
        "timestamp": datetime.utcnow().isoformat(),
        "git": get_git_status(),
        "structure": get_project_structure(),
        "summary": "Live project state snapshot for Kitenga context",
    }
    return snapshot


def save_project_state(snapshot: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Save project state snapshot to Supabase kitenga_project_state table."""
    if snapshot is None:
        snapshot = capture_project_snapshot()
    
    try:
        client = get_client()
        if not client:
            log_event("supabase_unavailable", "Cannot save project state")
            return {"error": "Supabase unavailable"}
        
        # Save to kitenga_project_state table
        result = client.table("kitenga_project_state").upsert(
            {
                "id": "current",  # Single "current" record
                "snapshot": snapshot,
                "updated_at": datetime.utcnow().isoformat(),
            }
        ).execute()
        
        log_event(
            "project_state_saved",
            "Project state snapshot saved to Supabase",
            data={"timestamp": snapshot["timestamp"]},
        )
        
        return snapshot
    except Exception as e:
        log_event("project_state_save_error", str(e))
        return {"error": str(e)}


def get_project_state() -> Dict[str, Any]:
    """Retrieve current project state from Supabase."""
    try:
        client = get_client()
        if not client:
            return {"error": "Supabase unavailable"}
        
        result = client.table("kitenga_project_state").select("snapshot").eq("id", "current").execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0].get("snapshot", {})
        
        # If no snapshot exists, capture and save one
        return save_project_state()
    except Exception as e:
        log_event("project_state_retrieve_error", str(e))
        return {"error": str(e)}


def format_project_state_for_context(snapshot: Optional[Dict[str, Any]] = None) -> str:
    """Format project state as context string for Kitenga prompts."""
    if snapshot is None:
        snapshot = get_project_state()
    
    if "error" in snapshot:
        return "No current project state available"
    
    lines = [
        "## Current Project State",
        f"Updated: {snapshot.get('timestamp', 'unknown')}",
        "",
        "### Git Status",
    ]
    
    git = snapshot.get("git", {})
    if "error" not in git:
        lines.append(f"- Branch: {git.get('branch', 'unknown')}")
        lines.append(f"- Recent commits: {len(git.get('recent_commits', []))} shown")
        if git.get("recent_commits"):
            for commit in git["recent_commits"][:3]:
                lines.append(f"  - {commit}")
        lines.append(f"- Status: {'clean' if not git.get('has_changes') else 'has changes'}")
    
    lines.extend([
        "",
        "### Project Structure",
    ])
    
    structure = snapshot.get("structure", {})
    if "error" not in structure:
        lines.append(f"- Services: {len(structure.get('services', []))} modules")
        lines.append(f"- Routes: {len(structure.get('routes', []))} endpoints")
        lines.append(f"- Models: {len(structure.get('models', []))} schemas")
    
    return "\n".join(lines)
