# CORS and Bearer Authentication

This document explains how CORS and Bearer token authentication work in Kitenga Whiro, and how to configure them for browser-based clients.

## Architecture

**Middleware Stack (execution order - outermost to innermost):**
1. **CORS Middleware** - Handles `Access-Control-*` headers and preflight `OPTIONS` requests
2. **Bearer Auth Middleware** - Validates `Authorization: Bearer <token>` header
3. **UTF8 Enforcer** - Ensures proper UTF-8 encoding

This ordering allows CORS preflight requests to pass through auth checks (as required by the browser), while protecting actual API calls.

## Configuring CORS for Browser Clients

### Environment Variable: `CORS_ALLOW_ORIGINS`

Set as a comma-separated list of allowed origins. Browser clients can only access the API from these origins.

**Local development default (if not set):**
```
http://localhost:5173
http://localhost:8100
http://127.0.0.1:5173
http://127.0.0.1:8100
```

**Example for production:**
```bash
export CORS_ALLOW_ORIGINS=https://example.com,https://www.example.com,https://admin.example.com
```

**Example for local multi-project setup:**
```bash
export CORS_ALLOW_ORIGINS=http://localhost:5173,http://localhost:8101,http://localhost:8102
```

### How It Works

1. Browser sends preflight `OPTIONS` request with `Origin` header
2. CORS middleware checks if origin is in `CORS_ALLOW_ORIGINS`
3. If allowed, responds with `Access-Control-Allow-*` headers
4. Browser then sends actual `GET/POST/PUT/etc.` request
5. Auth middleware checks for `Authorization: Bearer <token>`

## Bearer Token Authentication

### Required Header Format
```
Authorization: Bearer <PIPELINE_TOKEN>
```

**Environment variable:** `PIPELINE_TOKEN` (or `HUMAN_BEARER_KEY` as fallback)

### Unprotected Routes

These routes **do not require a Bearer token**:
- `/` - Root status endpoint
- `/heartbeat` - Health check
- `/health` - Health check
- `/docs` - API documentation (Swagger UI)
- `/openapi.json` - OpenAPI schema
- `/redoc` - ReDoc documentation

**Note:** `OPTIONS` and `HEAD` requests are always allowed (for CORS preflight and health probes)

### Protected Routes

All other routes require the `Authorization: Bearer <token>` header.

## Browser Client Configuration

### Vite + Vue/React Example

**`.env` file:**
```env
VITE_API_URL=http://localhost:10000
VITE_API_TOKEN=your-pipeline-token-here
```

**`src/api.js` or similar:**
```javascript
const API_URL = import.meta.env.VITE_API_URL;
const API_TOKEN = import.meta.env.VITE_API_TOKEN;

export async function apiCall(endpoint, options = {}) {
  const headers = {
    "Authorization": `Bearer ${API_TOKEN}`,
    ...options.headers,
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status} ${response.statusText}`);
  }

  return response.json();
}

// Usage:
const data = await apiCall("/api/intake", { method: "POST", body: JSON.stringify(...) });
```

### curl Example

```bash
# Without token (returns 401 for protected routes)
curl -i https://tiwhanawhana-backend.onrender.com/api/intake

# With token (succeeds for protected routes)
curl -i -H "Authorization: Bearer $PIPELINE_TOKEN" \
  https://tiwhanawhana-backend.onrender.com/api/intake
```

## Troubleshooting

### "CORS policy: No 'Access-Control-Allow-Origin' header"

**Cause:** Your origin is not in `CORS_ALLOW_ORIGINS`

**Solution:** Add your origin to the environment variable:
```bash
export CORS_ALLOW_ORIGINS=$CORS_ALLOW_ORIGINS,http://your-origin:port
```

### "401 Missing Bearer token"

**Cause:** You didn't include the `Authorization: Bearer <token>` header

**Solution:** Add the header to all requests:
```javascript
headers: {
  "Authorization": `Bearer ${process.env.VITE_API_TOKEN}`
}
```

### "403 Invalid Bearer token"

**Cause:** The token doesn't match `PIPELINE_TOKEN` or `HUMAN_BEARER_KEY`

**Solution:** Verify the token is set correctly:
```bash
echo $PIPELINE_TOKEN
```

## Production Deployment (Render)

On Render, ensure these environment variables are set in the dashboard:

1. **`CORS_ALLOW_ORIGINS`** - Your production domain(s)
   ```
   https://tiwhanawhana.example.com,https://api.tiwhanawhana.example.com
   ```

2. **`PIPELINE_TOKEN`** - Your secret API token (strong random value)
   ```
   use-a-long-random-string-here
   ```

3. **`HUMAN_BEARER_KEY`** - Optional fallback token

See [docs/realms/TE_PO/TEPO_RENDER_DEPLOYMENT.md](realms/TE_PO/TEPO_RENDER_DEPLOYMENT.md) for full deployment guide.

## Testing Locally

See [scripts/test_cors_auth.sh](../scripts/test_cors_auth.sh) for automated curl tests.
