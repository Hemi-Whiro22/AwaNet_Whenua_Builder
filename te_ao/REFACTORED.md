# Te Ao - Kitenga UI (Refactored)

## Purpose

**Te Ao** is now a focused developer/admin interface for:
- Testing API routes and health endpoints
- Monitoring Render deployment status
- Creating new realms from templates
- Viewing real-time realm events

## Panels

### 1. API & Health (`/api`)
Test all endpoints and view current service status.

**Features:**
- Real-time status monitoring (service components, dependencies)
- Quick-test buttons for key endpoints:
  - `/heartbeat` - Health check
  - `/status/full` - Detailed service status
  - `/docs` - OpenAPI documentation
  - `/api/intake`, `/api/chat` - Protected routes (test auth)
- Live test results with timing information
- Shows 401/403 errors clearly for auth debugging

**Use case:** Verify API is running and endpoints are accessible before deploying changes.

---

### 2. Realm Starter (`/realms`)
Create new realms from templates.

**Features:**
- Form to create realms with:
  - Realm name (e.g., `te_wai`, `te_ahi`)
  - Description
  - Template selection:
    - **Basic** - Core components only
    - **With Kaitiaki** - Includes governance + guardian roles
    - **With Storage** - Document storage + indexing
    - **Full Stack** - Everything enabled
- Created realms history panel
- Calls `te_hau` backend to actually spin up the realm

**Integration:**
- Calls `/api/realms/create` POST endpoint (requires Bearer token)
- Backend should integrate with `te_hau` to generate realm structure
- Returns realm path and metadata

**Use case:** Quickly scaffold new realm environments with governance rules baked in.

---

### 3. Realm Events (`/health`)
Monitor real-time events from active realms.

**Features:**
- Displays realm lifecycle events
- Shows event types: creation, updates, errors
- Real-time event streaming via WebSocket or polling
- Event payloads for debugging

**Use case:** Watch realm operations and troubleshoot issues in real-time.

---

## What Was Removed

The following research/chatbot panels were removed:
- ❌ ChatPanel (research chat)
- ❌ ResearchPanel
- ❌ SummaryPanel
- ❌ CulturalScanPanel
- ❌ IwiPortalPanel
- ❌ MemoryPanel
- ❌ VectorSearchPanel
- ❌ OCRPanel
- ❌ PronunciationPanel
- ❌ TranslationPanel / TranslatePanel
- ❌ AdminPanel

These features belong in separate applications (not in the deployment testing UI).

---

## Environment Setup

**`.env` file:**
```env
VITE_API_URL=http://localhost:10000
VITE_API_TOKEN=your-pipeline-token-here
```

**On Render:**
```env
VITE_API_URL=https://tiwhanawhana-backend.onrender.com
VITE_API_TOKEN=${PIPELINE_TOKEN}  # Set in Render dashboard
```

---

## Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

---

## Architecture

```
te_ao/
├── src/
│   ├── App.jsx              # Main tab navigation
│   ├── panels/
│   │   ├── ApiTestPanel.jsx     # API testing + status
│   │   ├── RealmStarterPanel.jsx # Realm creation form
│   │   └── RealmHealthPanel.tsx  # Event monitoring
│   ├── hooks/
│   │   ├── useApi.js            # API client wrapper
│   │   └── useEvents.js         # Event streaming
│   └── components/
│       └── ui/                  # Shared UI components
├── package.json
└── vite.config.js
```

---

## API Integration

### API Test Panel
Endpoints being tested:
- `GET /` - Root status
- `GET /heartbeat` - Health check
- `GET /status/full` - Detailed status
- `GET /docs` - OpenAPI schema
- `POST /api/intake` - (requires auth) Test protected route
- `POST /api/chat` - (requires auth) Test chat endpoint

### Realm Starter Panel
Endpoints being called:
- `POST /api/realms/create` - Create new realm from template

### Realm Health Panel
Endpoints being monitored:
- WebSocket or polling endpoint for realm events (TBD)

---

## Next Steps

1. **Backend Integration:** Implement `/api/realms/create` endpoint in `te_po`
2. **Event Streaming:** Add WebSocket or polling for realm events
3. **Authentication:** Ensure Bearer token is properly sent with all requests
4. **Kaitiaki Integration:** Link realm creation to `te_hau` realm generator
5. **Styling:** Refine Tailwind styling for production use

---

## Related Docs

- [docs/CORS_AND_AUTH.md](../../docs/CORS_AND_AUTH.md) - Auth setup for browser clients
- [docs/realms/TE_PO.md](../../docs/realms/TE_PO.md) - Backend realm setup
- [te_hau/README.md](../../te_hau/README.md) - Realm creation CLI

