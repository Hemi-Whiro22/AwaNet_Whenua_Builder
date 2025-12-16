from te_po.state.read_state import get_public_state

def get_project_state():
    """Fetch the current project state."""
    return get_public_state()

def list_project_backlog(filters=None):
    """List the project backlog based on provided filters."""
    state = get_public_state()
    backlog = state.get("backlog", [])

    if filters:
        backlog = [item for item in backlog if all(item.get(k) == v for k, v in filters.items())]

    return backlog