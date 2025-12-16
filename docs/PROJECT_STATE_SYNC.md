# Project State Sync

## Overview
The `state.yaml` file serves as the single source of truth for project state. This document explains how to publish, read, and use the project state across systems.

## Publishing State
The `state.yaml` file can be published to Supabase tables for sharing and synchronization.

### Supabase Tables
1. **`project_state_public`**: Contains safe, non-sensitive state information.
2. **`project_state_private`**: Contains additional operational details (no secrets).

### Table Schema
- `id` (text, primary key): Project identifier (e.g., `The_Awa_Network`)
- `state_yaml` (text): YAML representation of the state
- `repo` (text): Repository name
- `branch` (text): Branch name
- `commit` (text): Commit hash
- `version` (int): State version
- `last_updated` (timestamptz): Timestamp of the last update

### RLS Policies
- `project_state_public`: Readable by authenticated users or service roles.
- `project_state_private`: Accessible only by service roles.

### Publishing Script
Use the `publish_state.py` script to publish the state:
```bash
python -m te_po.state.publish_state
```
This script:
1. Loads `state.yaml`
2. Validates required keys
3. Upserts the state into `project_state_public`
4. Increments the version if the content changes

## Reading State
### Reader Helper
Use the `read_state.py` helper to fetch the latest state:
```python
from te_po.state.read_state import get_public_state
state = get_public_state()
```

### API Endpoints
1. **`GET /state/public`**: Returns the latest public state (requires Bearer authentication).
2. **`GET /state/version`**: Returns the current state version.

## External Callers
External clients should use the `render` URL from the `urls` section of the state. For example:
```
https://tiwhanawhana-backend.onrender.com
```
Do not use internal ports (e.g., `:10000`).

## Running Locally

### Publish State
To publish the state locally, use the `publish_state.py` script:
```bash
python -m te_po.scripts.publish_state --dry-run  # Simulate the publish process
python -m te_po.scripts.publish_state --live     # Publish to Supabase
```

### Test Endpoints
Run the smoke test script to validate the endpoints:
```bash
bash scripts/test_state_sync.sh
```

### Check Route Drift
Use the drift checker script to compare declared entrypoints with mounted routes:
```bash
python te_po/scripts/state_drift_check.py
```

## Running on Render

### Environment Variables
Ensure the following environment variables are set on Render:
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `HUMAN_BEARER_KEY`
- `PIPELINE_TOKEN`

### Deployment
Deploy the application to Render and verify the endpoints:
- `/state/public` should be accessible without authentication.
- `/state/private` should require a Bearer token.

### Validate State
Run the smoke test script against the Render deployment:
```bash
BASE_URL="https://your-render-url" BEARER_TOKEN="your-token" bash scripts/test_state_sync.sh
```

## Constraints
- **No Secrets**: Do not store secret values in Supabase.
- **Minimal Schema**: Keep the schema stable and minimal.
- **Inline Mode**: Ensure compatibility with `QUEUE_MODE=inline` (no Redis).

## Future Enhancements
- Add support for multi-realm processing.
- Improve translation accuracy in `te_hau`.

## Conclusion
The `state.yaml` file and its synchronization process ensure consistency and reliability across systems. Follow the guidelines to maintain a robust project state.