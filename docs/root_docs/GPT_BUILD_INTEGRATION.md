# Awa Network - GPT Build Integration Guide

## Quick Start: Tools & Endpoints for GPT Build Connector

Your system has **27 services** with **120+ endpoints** across 3 main services (Te Pō, Te Hau, Te Ao). Here's what you can expose to GPT Build:

---

## 🎯 OpenAI-Ready Tools (Already Formatted)

These 7 tools are pre-configured for OpenAI/GPT integration:

### 1. **Kitenga Whisper** - Chat/Processing
- **Path**: `POST /kitenga/gpt-whisper`
- **Purpose**: Main chat/processing endpoint
- **Use**: For conversational AI tasks

### 2. **OCR Tool** - Document Scanning
- **Path**: `POST /kitenga/tool/ocr`
- **Purpose**: OCR a remote image/PDF/text file
- **Input**: File reference or URL
- **Use**: Extract text from documents

### 3. **Pipeline Run** - Data Ingestion
- **Path**: `POST /kitenga/pipeline/run`
- **Purpose**: Run the ingestion pipeline
- **Use**: Process documents through your pipeline

### 4. **Kitenga Vision OCR** - AI Vision
- **Path**: `POST /kitenga/tool/vision-ocr`
- **Purpose**: OpenAI Vision-based OCR
- **Use**: Advanced image understanding

### 5. **Chat Save Session** - Memory
- **Path**: `POST /kitenga/chat/save-session`
- **Purpose**: Save a chat session to vector store
- **Use**: Persist conversations for retrieval

### 6. **Assistant Run** - Multi-turn Tasks
- **Path**: `POST /kitenga/assistant/run`
- **Purpose**: Run an assistant thread
- **Use**: Execute complex multi-step tasks

### 7. **Vector Batch Status** - Check Status
- **Path**: `GET /kitenga/vector/batch-status`
- **Purpose**: Check vector batch status
- **Use**: Monitor document processing

---

## 📚 Core API Routes by Service (120+ endpoints)

### Te Pō Service (Main Backend - 90+ endpoints)

#### Protocol & System (14 endpoints)
- **AWA Protocol Routes** - Inter-service communication
  - `POST /awa/route` - Route messages
  - `POST /awa/wrap` - Wrap payloads
  - `GET /awa/contract/{route}` - Get route contracts

#### Database & Knowledge (13 endpoints)
- **Kitenga Database**
  - `GET /kitenga/db/metadata`
  - `POST /kitenga/db/query`
  - `GET /kitenga/db/schema`

#### Processing & Pipeline (8 endpoints)
- **Pipeline Operations**
  - `POST /pipeline/run` - Execute pipeline
  - `GET /pipeline/status`
  - `POST /pipeline/config`

#### Backend Services (8 endpoints)
- **Kitenga Backend**
  - `POST /kitenga/process`
  - `GET /kitenga/status`
  - `POST /kitenga/batch`

#### Development Tools (8 endpoints)
- **Dev Routes**
  - `GET /dev/health`
  - `POST /dev/test`
  - `GET /dev/logs`

#### Realm Generation (7 endpoints)
- **Realm Generator**
  - `POST /realm/generate`
  - `GET /realm/list`
  - `POST /realm/validate`

#### Cards & Content (6 endpoints)
- **Card Management**
  - `GET /cards/list`
  - `POST /cards/create`
  - `GET /cards/{id}`

#### Vector & Embeddings (5 endpoints)
- **Vector Operations**
  - `POST /vector/embed` - Create embeddings
  - `POST /vector/search` - Semantic search
  - `GET /vector/recent` - Recent vectors
  - `POST /vector/retrieval-test` - Test retrieval
  - `GET /vector/batch-status` - Batch status

#### Language Tools (3 endpoints - Reo Māori)
- **Reo Translation**
  - `POST /reo/translate` - Translate text
  - `POST /reo/explain` - Explain words
  - `POST /reo/pronounce` - Pronunciation

#### OCR Services (3 endpoints)
- **OCR Processing**
  - `POST /ocr/scan` - Scan documents
  - `POST /ocr/batch` - Batch OCR
  - `GET /ocr/status` - OCR status

#### Ingestion (2 endpoints)
- **Content Intake**
  - `POST /intake/ocr` - OCR intake
  - `POST /intake/summarize` - Summarization

#### State Management (5 endpoints)
- **State Synchronization**
  - `GET /state/current`
  - `POST /state/update`
  - `GET /state/history`

#### Memory & Recall (2 endpoints)
- **Conversation Memory**
  - `POST /memory/store` - Store memory
  - `POST /recall/search` - Retrieve memory

#### Research & Analysis (3 endpoints)
- **Research Tools**
  - `POST /research/analyze`
  - `GET /research/status`
  - `POST /research/save`

#### Other Services (8+ endpoints)
- Assistant management
- Chat sessions
- Document management
- Metrics & monitoring
- Status & health checks

### Te Hau Service (API Bridge - 6 endpoints)

- `GET /api/status` - Mirror Te Pō status
- `POST /api/ocr` - Proxy OCR to Te Pō
- `GET /api/kaitiaki` - List kaitiaki (guides)
- `POST /api/kaitiaki` - Create kaitiaki
- `GET /api/events` - List recent events
- `POST /api/events` - Push events
- `GET/POST /api/{full_path}` - Generic passthrough

### Te Ao Service (Frontend Connector)

Frontend-based endpoints for real-time communication and UI state management.

---

## 🔌 How to Connect to GPT Build

### Option 1: Use Pre-configured OpenAI Tools
Your system already has these 7 tools configured in `openai_tools.json`. You can:
1. Export this JSON to GPT Build
2. Map each tool to your endpoints
3. Test via the OpenAI Assistant interface

### Option 2: Create Custom Connector
For broader endpoint access, create a connector that:
```javascript
// GPT Build Custom Connector Template
const endpoints = {
  // OCR & Document Processing
  ocr: "POST http://localhost:8010/ocr/scan",
  vision_ocr: "POST http://localhost:8010/kitenga/tool/vision-ocr",

  // Search & Knowledge
  vector_search: "POST http://localhost:8010/vector/search",
  db_query: "POST http://localhost:8010/kitenga/db/query",

  // Processing
  pipeline_run: "POST http://localhost:8010/pipeline/run",

  // Language
  translate: "POST http://localhost:8010/reo/translate",

  // Chat/Memory
  save_session: "POST http://localhost:8010/kitenga/chat/save-session",
  recall: "POST http://localhost:8010/recall/search",

  // System
  status: "GET http://localhost:8010/status"
}
```

### Option 3: Route Specific Endpoints
Based on your use case, expose subsets:

**For Document Processing:**
- `/ocr/scan` → OCR
- `/intake/summarize` → Summarize
- `/vector/embed` → Create embeddings

**For Chat:**
- `/kitenga/gpt-whisper` → Process message
- `/kitenga/chat/save-session` → Store context
- `/recall/search` → Retrieve context

**For Research:**
- `/vector/search` → Search documents
- `/kitenga/db/query` → Query knowledge base
- `/research/analyze` → Analyze content

---

## 🔧 Configuration for MCP Servers

Your `Continue` IDE has MCP servers configured:
- `kitenga_whiro` - Not connected (Python CLI missing)
- `tepo` - Not connected (Python CLI missing)
- `supabase` - Not connected
- `git` - Not connected (Node CLI missing)

**To fix these**, you need to:
```bash
# Install Python CLI
python3 -m pip install --user --upgrade tepo-cli

# Install Node CLI
npm install -g @kitenga/cli
```

Once connected, you'll have IDE-level tool access to all your endpoints.

---

## 📊 Quick Reference: Endpoint Count by Category

| Service | Endpoints | Key Use |
|---------|-----------|---------|
| AWA Protocol | 14 | Inter-service routing |
| Kitenga DB | 13 | Knowledge queries |
| Kitenga Backend | 8 | Main processing |
| Pipeline | 8 | Data ingestion |
| Dev Tools | 8 | Testing/debugging |
| Realm Generator | 7 | Create realms |
| Cards | 6 | Content cards |
| Vector | 5 | Embeddings/search |
| State | 5 | State sync |
| Reo (Language) | 3 | Translation |
| OCR | 3 | Document scanning |
| **TOTAL** | **120+** | **Full system** |

---

## 🎯 Recommended Starter Set for GPT Build

Start with these 5 core endpoints:

1. `POST /kitenga/gpt-whisper` - **Chat interface**
2. `POST /vector/search` - **Knowledge search**
3. `POST /ocr/scan` - **Document OCR**
4. `POST /pipeline/run` - **Process documents**
5. `POST /kitenga/chat/save-session` - **Persist context**

This gives you chat, search, OCR, processing, and memory - a complete AI agent stack.

---

## 🚀 Next Steps

1. **Export OpenAI Tools**: Take your `openai_tools.json` to GPT Build
2. **Test Endpoints**: Use the included health checks (`GET /heartbeat`)
3. **Set Base URL**: Point GPT Build to `http://localhost:8010` (or your deployment)
4. **Configure Auth**: If needed, add bearer tokens to your tool configs
5. **Map Functions**: Create GPT Build connector functions for each tool

---

## 📁 Key Files

- [Routes Summary](./analysis/routes_summary.json) - Full endpoint details
- [OpenAI Tools](./te_po/openai_tools.json) - Pre-configured tools
- [OpenAI Assistants](./te_po/openai_assistants.json) - Assistant configs (QA, Ops, Research)
- [MCP Server](./tepo_mcp_server.py) - Model Context Protocol server

---

**Your system is ready for GPT Build integration!** 🎉
