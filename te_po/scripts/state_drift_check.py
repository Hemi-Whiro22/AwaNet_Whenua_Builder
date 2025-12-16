import yaml
import requests
from fastapi.routing import APIRoute
from te_po.app import app

STATE_FILE = "state.yaml"


def load_state_yaml():
    """Load the state.yaml file."""
    with open(STATE_FILE, "r") as file:
        return yaml.safe_load(file)


def get_declared_entrypoints():
    """Extract declared entrypoints from state.yaml."""
    state = load_state_yaml()
    return set(state.get("services", {}).get("te_po", {}).get("entrypoints", []))


def get_mounted_routes():
    """Extract mounted routes from the FastAPI app."""
    return set(route.path for route in app.routes if isinstance(route, APIRoute))


def compare_routes():
    """Compare declared entrypoints with mounted routes."""
    declared = get_declared_entrypoints()
    mounted = get_mounted_routes()

    missing = declared - mounted
    extra = mounted - declared

    print("# Route Drift Report\n")

    if missing:
        print("## Missing Routes\n")
        for route in missing:
            print(f"- [ ] {route}")
    else:
        print("No missing routes.\n")

    if extra:
        print("## Extra Routes\n")
        for route in extra:
            print(f"- [ ] {route}")
    else:
        print("No extra routes.\n")


if __name__ == "__main__":
    compare_routes()