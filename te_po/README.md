Te Pō (Backend Realm)
- FastAPI backend and services for Whai Tika Reo.
- Holds core APIs, health, and guardian integration.

## Te Pō API Extensions

- **Assistant Bridge** (`/assistant/run`): Proxies your OpenAI assistant (`gpt-4o`, assistant ID in `KITENGA_ASSISTANT_ID`) with optional vector search tools. Use it to send text + thread metadata from GPT Build or other automation and reuse the existing vector/telemetry tooling.
- **Health + version** (`/assistant/health`, `/assistant/version`): Built-in diagnostics that report environment readiness (OpenAI key status, vector ID, git commit) and are ideal for Render/Cloudflare health checks.
  - `/assistant/version` emits the current `git rev-parse HEAD` value plus the environment identifiers so Render knows exactly what revision is running, even when valet/tunnels are in play.

Make sure the same env vars drive your deployment configuration: `OPENAI_API_KEY`, `KITENGA_ASSISTANT_ID`, `KITENGA_VECTOR_STORE_ID`, and `OPENAI_BASE_URL` (defaults to `https://api.openai.com/v1`).
