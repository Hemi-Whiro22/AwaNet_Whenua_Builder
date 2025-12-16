# Context Pack

## Meta
- **Last Updated**: 2025-12-15
- **Repository**: The_Awa_Network
- **Branch**: main
- **Commit**: latest
- **Environment**: local
- **Primary URL**: [http://localhost:5000](http://localhost:5000)

## Services
### te_po
- **Status**: Active
- **Entrypoints**:
  - `/heartbeat`
  - `/status`
  - `/vector/search`
- **Ports**: 5000
- **Required Environment Variables**:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `OPENAI_API_KEY`
- **Healthchecks**:
  - `/heartbeat`
  - `/status`

### te_hau
- **Status**: Active
- **Entrypoints**:
  - `/api/v1/translate`
  - `/api/v1/process`
- **Ports**: 8000
- **Required Environment Variables**:
  - `TRANSLATION_API_KEY`
  - `DATABASE_URL`
- **Healthchecks**:
  - `/api/v1/health`

### te_ao
- **Status**: Active
- **Entrypoints**:
  - `/`
  - `/dashboard`
- **Ports**: 5173
- **Required Environment Variables**:
  - `FRONTEND_PORT`
- **Healthchecks**:
  - `/`

## Security
- **Bearer Auth Rules**:
  - `Authorization: Bearer <token>`
- **Unprotected Paths**:
  - `/docs/oauth2-redirect`
  - `/favicon.ico`
- **Token Environment Variables**:
  - `PIPELINE_TOKEN`
  - `OPENAI_API_KEY`
- **CORS Configuration**:
  - **Allowed Origins**:
    - `http://localhost:5173`
    - `https://example.com`
  - **Allowed Methods**:
    - `GET`
    - `POST`
    - `OPTIONS`
  - **Allowed Headers**:
    - `Authorization`
    - `Content-Type`

## Deployment
- **Render YAML Summary**:
  - **te_po**: Free plan, Oregon region
  - **te_hau**: Starter plan, Frankfurt region
  - **te_ao**: Free plan, Oregon region
- **Required Render Environment Variables**:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - `OPENAI_API_KEY`
  - `DATABASE_URL`

## Pipelines
- **Queue Mode**: `rq`
- **Postgres Tracking**: Enabled
- **Redis Optional**: True

## Known Issues
1. **ID**: 1
   - **Symptom**: API returns 500 on vector search
   - **Cause**: Missing `SUPABASE_URL`
   - **Fix**: Ensure `SUPABASE_URL` is set in environment
2. **ID**: 2
   - **Symptom**: Frontend fails to load
   - **Cause**: Missing `FRONTEND_PORT`
   - **Fix**: Set `FRONTEND_PORT` to 5173

## Backlog
1. **ID**: 101
   - **Title**: Add support for multi-realm processing
   - **Realm**: `te_po`
   - **Priority**: High
   - **Status**: Open
   - **Steps**:
     - Define multi-realm schema
     - Update vector search to support realms
   - **Acceptance Test**: Ensure vector search works across realms
2. **ID**: 102
   - **Title**: Improve translation accuracy
   - **Realm**: `te_hau`
   - **Priority**: Medium
   - **Status**: In-progress
   - **Steps**:
     - Fine-tune translation model
     - Add more test cases
   - **Acceptance Test**: Translation accuracy > 95%