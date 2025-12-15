# Realm Template

This is the base template for creating new Awa Network realms.

## Quick Start

1. Copy `.env.example` to `.env`
2. Fill in the required fields:
   - `REALM_ID`: Unique identifier for this realm
   - `REALM_NAME`: Display name
   - `TE_PO_URL`: URL to the main Te Pó backend
   - `BEARER_KEY`: Bearer token for authentication

3. Bootstrap the proxy:
   ```bash
   python te_po_proxy/bootstrap.py
   ```

4. Run the proxy:
   ```bash
   python te_po_proxy/main.py
   ```

The proxy will be available at `http://localhost:8000`

## Structure

- **mauri/**: State and configuration
  - `realm_manifest.json`: Realm identity and configuration
- **te_po_proxy/**: Backend proxy (forwards to main Te Pó)
  - `main.py`: FastAPI proxy server
  - `bootstrap.py`: Initialization script
  - `requirements.txt`: Python dependencies
- **.env**: Realm configuration (create from .env.example)

## Optional: Add Frontend

To add a React frontend to this realm:

```bash
npm create vite@latest te_ao -- --template react
cd te_ao
npm install
```

Then update `VITE_API_URL` in `.env` to point to the proxy.

## Connecting to Main Te Pó

The proxy forwards all requests to the upstream Te Pó backend specified in `TE_PO_URL`.

Authentication uses the `BEARER_KEY` from `.env`, automatically added to all requests.

## Next Steps

- Deploy `te_po_proxy` to a hosting platform (Render, Railway, etc.)
- (Optional) Add a realm-specific UI under `te_ao/`
- Configure domain name and SSL
