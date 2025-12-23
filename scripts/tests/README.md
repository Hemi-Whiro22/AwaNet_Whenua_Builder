# Test Helpers

These scripts keep the local Te Pō backend honest and the Render deployment verified.

## Running the suite manually

1. Start your backend (e.g. `uvicorn te_po.core.main:app --reload --port 8000`).
2. From the repo root invoke:

```bash
bash scripts/tests/run_all_tests.sh local
```

Use `render` instead of `local` to run the same suite against `https://tiwhanawhana-backend.onrender.com`.

## Automated start + test

Use `scripts/tests/start_and_test.sh` to:

1. Start the FastAPI app locally on `localhost:8000` (configurable via `PORT`, `HOST`, and `APP_MODULE` environment variables).
2. Wait for `/heartbeat` to answer.
3. Export `API_URL`/`STATE_BASE_URL`.
4. Run the full suite (`run_all_tests.sh`).
5. Kill the server after the tests finish.

```bash
bash scripts/tests/start_and_test.sh local
```

Pass `render` to the helper to skip the local server and just run everything against Render:

```bash
bash scripts/tests/start_and_test.sh render
```

## Environment overrides

- `API_URL` and `STATE_BASE_URL` can be exported before invoking the scripts to target alternate hosts.
- `PIPELINE_TOKEN` or `HUMAN_BEARER_KEY` must be available if you want the auth tests to exercise protected routes.
