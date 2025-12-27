# Te Kaitiaki o ngā Āhua Kawenga — Payload Registry

**Scan time:** 2025-12-27T10:04:57.029481
**Mauri score:** 10 / 10

## Realm Whakapapa
- contact: mailto:kaitiaki@awanet.nz
- description: The living bridge between Kitenga Whiro intelligence and the Awa Network.
- maintainer: Hemi Whiro
- mauri: flowing
- name: Te Pō Assistant
- realm: AwaNet
- version: 1.0.0

## Payload Shapes
### GET / → read_root
- Module: te_po.app
- Whakapapa path: te_po/app.py
- Registered route: yes
- Mauri score: 1

### GET /api/status → status
- Module: te_hau.app
- Whakapapa path: te_hau/app.py
- Registered route: yes
- Mauri score: 1

### POST /api/ocr → ocr_proxy
- Module: te_hau.app
- Whakapapa path: te_hau/app.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - file (UploadFile)

### GET /api/kaitiaki → kaitiaki_list
- Module: te_hau.app
- Whakapapa path: te_hau/app.py
- Registered route: yes
- Mauri score: 1

### POST /api/kaitiaki → kaitiaki_create
- Module: te_hau.app
- Whakapapa path: te_hau/app.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - payload (dict)

### GET /api/events → events
- Module: te_hau.app
- Whakapapa path: te_hau/app.py
- Registered route: yes
- Mauri score: 1

### POST /api/events → push
- Module: te_hau.app
- Whakapapa path: te_hau/app.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - event (dict)

### GET /health → health_check
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /tools/list → list_tools
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /openapi-core.json → openapi_core
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /.well-known/openapi-core.json → openapi_core_well_known
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /openai_tools.json → openai_tools
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /.well-known/ai-plugin.json → ai_plugin
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /tools/describe → describe_tools
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### POST /tools/call → call_tool
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - request (Request)

### GET /debug/routes → debug_routes
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### POST /awa/loop/test → awa_loop_test
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /health → health
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### POST /awa/protocol/event → receive_awa_event
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - request (Request)

### GET /awa/memory/debug → memory_debug
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### POST /awa/memory/search → search_memory
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - request (Request)

### POST /awa/memory/add → add_memory
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - request (Request)

### GET / → root
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /health → health_check
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /tools/list → list_tools_manifest
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /mcp/tools/list → list_tools_manifest_alias
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /openapi-core.json → openapi_core
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /.well-known/openapi-core.json → openapi_core_well_known
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /mcp/openapi-core.json → openapi_core_mcp_alias
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /tools/describe → describe_tools
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### POST /tools/call → call_tool
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - request (Request)

### GET /memory/ping → memory_ping
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /env → get_env
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: no
- Mauri score: 1

### GET /routes → list_routes
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: no
- Mauri score: 1

### GET /health/full → full_health
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: no
- Mauri score: 1

### GET / → root
- Module: kitenga_mcp.app_server
- Whakapapa path: kitenga_mcp/app_server.py
- Registered route: yes
- Mauri score: 1

### GET /jobs → get_recent_jobs
- Module: kitenga_mcp.pipeline
- Whakapapa path: kitenga_mcp/pipeline.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - realm (str)
  - limit (int)

### POST /enqueue → enqueue_job
- Module: kitenga_mcp.pipeline
- Whakapapa path: kitenga_mcp/pipeline.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - realm (str)
  - payload (dict)

### POST /search → memory_search
- Module: kitenga_mcp.memory
- Whakapapa path: kitenga_mcp/memory.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (MemorySearchRequest) → fields: query, realm
- Example payload:
```json
{
  "req": {
    "query": "example_query",
    "realm": "example_realm"
  }
}
```

### POST /store → store_fragment
- Module: kitenga_mcp.memory
- Whakapapa path: kitenga_mcp/memory.py
- Registered route: no
- Mauri score: 4
- Parameters:
  - realm (str)
  - content (str)
  - tapu_level (int)

### GET / → root
- Module: te_po.core.main
- Whakapapa path: te_po/core/main.py
- Registered route: yes
- Mauri score: 1

### GET /heartbeat → heartbeat
- Module: te_po.core.main
- Whakapapa path: te_po/core/main.py
- Registered route: yes
- Mauri score: 1

### GET /gpt_connect.yaml → serve_gpt_connect
- Module: te_po.core.main
- Whakapapa path: te_po/core/main.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - background_tasks (BackgroundTasks)

### GET /realm.json → serve_realm
- Module: te_po.core.main
- Whakapapa path: te_po/core/main.py
- Registered route: yes
- Mauri score: 1

### GET /openapi-core.json → serve_openapi_core
- Module: te_po.core.main
- Whakapapa path: te_po/core/main.py
- Registered route: yes
- Mauri score: 1

### GET /.well-known/openapi-core.json → serve_openapi_core_well_known
- Module: te_po.core.main
- Whakapapa path: te_po/core/main.py
- Registered route: yes
- Mauri score: 1

### GET /openai_tools.json → serve_openai_tools
- Module: te_po.core.main
- Whakapapa path: te_po/core/main.py
- Registered route: yes
- Mauri score: 1

### GET /analysis/sync-status → analysis_sync_status_endpoint
- Module: te_po.core.main
- Whakapapa path: te_po/core/main.py
- Registered route: yes
- Mauri score: 1

### GET /analysis/documents/latest → analysis_latest_document
- Module: te_po.core.main
- Whakapapa path: te_po/core/main.py
- Registered route: yes
- Mauri score: 1

### POST /awa/gpt/invoke → awa_gpt_invoke
- Module: te_po.core.awa_gpt
- Whakapapa path: te_po/core/awa_gpt.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - request (Request)

### POST /awa/gpt/realtime/toggle → toggle_realtime
- Module: te_po.core.awa_realtime
- Whakapapa path: te_po/core/awa_realtime.py
- Registered route: no
- Mauri score: 1

### GET /awa/gpt/realtime/status → realtime_status
- Module: te_po.core.awa_realtime
- Whakapapa path: te_po/core/awa_realtime.py
- Registered route: no
- Mauri score: 1

### POST /ocr → ocr
- Module: te_po.core.kitenga_cards
- Whakapapa path: te_po/core/kitenga_cards.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - payload (OCRPayload) → fields: image_base64
- Example payload:
```json
{
  "payload": {
    "image_base64": "example_image_base64"
  }
}
```

### POST /translate → translate_text
- Module: te_po.core.kitenga_cards
- Whakapapa path: te_po/core/kitenga_cards.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - req (TranslateRequest) → fields: text, target_lang
- Example payload:
```json
{
  "req": {
    "text": "example_text",
    "target_lang": "example_target_lang"
  }
}
```

### POST /speak → speak_text
- Module: te_po.core.kitenga_cards
- Whakapapa path: te_po/core/kitenga_cards.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - req (SpeakRequest) → fields: text
- Example payload:
```json
{
  "req": {
    "text": "example_text"
  }
}
```

### POST /scribe → scribe
- Module: te_po.core.kitenga_cards
- Whakapapa path: te_po/core/kitenga_cards.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - entry (ScribeEntry) → fields: speaker, text, tone, glyph_id, translate
- Example payload:
```json
{
  "entry": {
    "speaker": "example_speaker",
    "text": "example_text",
    "tone": "example_tone",
    "glyph_id": "example_glyph_id",
    "translate": false
  }
}
```

### POST /gpt-whisper → gpt_whisper
- Module: te_po.core.kitenga_cards
- Whakapapa path: te_po/core/kitenga_cards.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - request (Request)

### POST /scan-image → scan_image
- Module: te_po.routes.cards
- Whakapapa path: te_po/routes/cards.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - image (UploadFile)

### POST /estimate-value → estimate_value
- Module: te_po.routes.cards
- Whakapapa path: te_po/routes/cards.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (Dict[str, Any])

### POST /build-row → build_row
- Module: te_po.routes.cards
- Whakapapa path: te_po/routes/cards.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (Dict[str, Any])

### POST /build-csv → build_csv
- Module: te_po.routes.cards
- Whakapapa path: te_po/routes/cards.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (Dict[str, Any])

### POST /value → card_value
- Module: te_po.routes.cards
- Whakapapa path: te_po/routes/cards.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (Dict[str, Any])

### POST /upload-image → upload_image
- Module: te_po.routes.cards
- Whakapapa path: te_po/routes/cards.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - image (UploadFile)

### POST /run → pipeline_run
- Module: te_po.routes.pipeline
- Whakapapa path: te_po/routes/pipeline.py
- Registered route: no
- Mauri score: 5
- Parameters:
  - file (UploadFile | None)
  - text (str | None)
  - source (str)
  - authorization (str | None)

### POST /enqueue → enqueue_pipeline
- Module: te_po.routes.pipeline
- Whakapapa path: te_po/routes/pipeline.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - file (UploadFile)
  - x_realm (str | None)

### GET /status/{job_id} → pipeline_status
- Module: te_po.routes.pipeline
- Whakapapa path: te_po/routes/pipeline.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - job_id (str)

### GET /jobs/recent → get_recent_jobs_endpoint
- Module: te_po.routes.pipeline
- Whakapapa path: te_po/routes/pipeline.py
- Registered route: no
- Mauri score: 5
- Parameters:
  - limit (int)
  - realm (str | None)
  - queue (str | None)
  - status (str | None)

### POST /batch → enqueue_batch
- Module: te_po.routes.pipeline
- Whakapapa path: te_po/routes/pipeline.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - files (List[UploadFile])

### GET /batch-status/{batch_id} → batch_status
- Module: te_po.routes.pipeline
- Whakapapa path: te_po/routes/pipeline.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - batch_id (str)

### POST /cancel/{job_id} → cancel_job
- Module: te_po.routes.pipeline
- Whakapapa path: te_po/routes/pipeline.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - job_id (str)

### GET /health/queue → queue_health
- Module: te_po.routes.pipeline
- Whakapapa path: te_po/routes/pipeline.py
- Registered route: no
- Mauri score: 1

### GET /profiles → document_profiles
- Module: te_po.routes.documents
- Whakapapa path: te_po/routes/documents.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - limit (int)

### POST /research/query → research
- Module: te_po.routes.research
- Whakapapa path: te_po/routes/research.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - body (dict)

### POST /research/web_search → research_web_search
- Module: te_po.routes.research
- Whakapapa path: te_po/routes/research.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (dict)

### POST /research/stacked → research_stacked
- Module: te_po.routes.research
- Whakapapa path: te_po/routes/research.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (dict)

### POST /run → assistant_run
- Module: te_po.routes.assistant
- Whakapapa path: te_po/routes/assistant.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - payload (dict)
  - authorization (str | None)

### POST /create → create_assistant
- Module: te_po.routes.assistant
- Whakapapa path: te_po/routes/assistant.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - payload (dict)
  - authorization (str | None)

### GET /list → list_assistants
- Module: te_po.routes.assistant
- Whakapapa path: te_po/routes/assistant.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - authorization (str | None)
  - limit (int)

### GET /vector-stores → list_vector_stores
- Module: te_po.routes.assistant
- Whakapapa path: te_po/routes/assistant.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - authorization (str | None)
  - limit (int)

### POST /run → run_assistant
- Module: te_po.routes.assistant_bridge
- Whakapapa path: te_po/routes/assistant_bridge.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (dict[str, Any])

### GET /health → health_check
- Module: te_po.routes.assistant_bridge
- Whakapapa path: te_po/routes/assistant_bridge.py
- Registered route: yes
- Mauri score: 1

### GET /version → version
- Module: te_po.routes.assistant_bridge
- Whakapapa path: te_po/routes/assistant_bridge.py
- Registered route: no
- Mauri score: 1

### POST /memory-ingest → ingest_chat_memory
- Module: te_po.routes.chat
- Whakapapa path: te_po/routes/chat.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (ChatMemoryIngestRequest) → fields: session_id, text, role, thread_id, assistant_reply
- Example payload:
```json
{
  "payload": {
    "session_id": "example_session_id",
    "text": "example_text",
    "role": "example_role",
    "thread_id": "example_thread_id",
    "assistant_reply": "example_assistant_reply"
  }
}
```

### POST /save-session → save_session
- Module: te_po.routes.chat
- Whakapapa path: te_po/routes/chat.py
- Registered route: no
- Mauri score: 7
- Parameters:
  - session_id (str)
  - title (Optional[str])
  - tags (Optional[str])
  - summarize (bool)
  - summary_words (int)
  - write_ari (bool)

### GET /status → status
- Module: te_po.routes.status
- Whakapapa path: te_po/routes/status.py
- Registered route: yes
- Mauri score: 1

### GET /status/openai → status_openai
- Module: te_po.routes.status
- Whakapapa path: te_po/routes/status.py
- Registered route: no
- Mauri score: 1

### GET /status/full → status_full
- Module: te_po.routes.status
- Whakapapa path: te_po/routes/status.py
- Registered route: no
- Mauri score: 1

### POST /embed → vector_embed
- Module: te_po.routes.vector
- Whakapapa path: te_po/routes/vector.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (EmbedRequest) → fields: text
- Example payload:
```json
{
  "payload": {
    "text": "example_text"
  }
}
```

### POST /search → vector_search
- Module: te_po.routes.vector
- Whakapapa path: te_po/routes/vector.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (SearchRequest) → fields: query, top_k
- Example payload:
```json
{
  "payload": {
    "query": "example_query",
    "top_k": 0
  }
}
```

### POST /retrieval-test → vector_retrieval_test
- Module: te_po.routes.vector
- Whakapapa path: te_po/routes/vector.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (SearchRequest) → fields: query, top_k
- Example payload:
```json
{
  "payload": {
    "query": "example_query",
    "top_k": 0
  }
}
```

### GET /recent → vector_recent
- Module: te_po.routes.vector
- Whakapapa path: te_po/routes/vector.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - limit (int)

### GET /batch-status → vector_batch_status
- Module: te_po.routes.vector
- Whakapapa path: te_po/routes/vector.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - batch_id (str)
  - vector_store_id (str | None)

### GET /status → kitenga_db_status
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: yes
- Mauri score: 1

### GET /stats → kitenga_db_stats
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: no
- Mauri score: 1

### POST /logs → create_log
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (LogEventRequest) → fields: event, detail, source, data
- Example payload:
```json
{
  "req": {
    "event": "example_event",
    "detail": "example_detail",
    "source": "example_source",
    "data": {}
  }
}
```

### GET /logs/recent → recent_logs
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - limit (int)
  - source (str)

### POST /memory → create_memory
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (MemoryRequest) → fields: content, metadata
- Example payload:
```json
{
  "req": {
    "content": "example_content",
    "metadata": {}
  }
}
```

### POST /memory/search → search_memory_route
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (SearchRequest) → fields: query, limit
- Example payload:
```json
{
  "req": {
    "query": "example_query",
    "limit": 0
  }
}
```

### POST /chat/log → create_chat_log
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (ChatLogRequest) → fields: session_id, user_message, assistant_reply, thread_id, mode, metadata
- Example payload:
```json
{
  "req": {
    "session_id": "example_session_id",
    "user_message": "example_user_message",
    "assistant_reply": "example_assistant_reply",
    "thread_id": "example_thread_id",
    "mode": "example_mode",
    "metadata": {}
  }
}
```

### GET /chat/history/{session_id} → chat_history
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - session_id (str)
  - limit (int)

### POST /taonga → create_taonga
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (TaongaRequest) → fields: title, content, metadata
- Example payload:
```json
{
  "req": {
    "title": "example_title",
    "content": "example_content",
    "metadata": {}
  }
}
```

### GET /taonga/{taonga_id} → get_taonga
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - taonga_id (str)

### POST /taonga/search → search_taonga_route
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (SearchRequest) → fields: query, limit
- Example payload:
```json
{
  "req": {
    "query": "example_query",
    "limit": 0
  }
}
```

### GET /pipeline/recent → recent_pipelines
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - limit (int)

### POST /whakapapa → create_whakapapa
- Module: te_po.routes.kitenga_db
- Whakapapa path: te_po/routes/kitenga_db.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (WhakapapaRequest) → fields: id, title, category, summary, content_type, data, author
- Example payload:
```json
{
  "req": {
    "id": "example_id",
    "title": "example_title",
    "category": "example_category",
    "summary": "example_summary",
    "content_type": "example_content_type",
    "data": {},
    "author": "example_author"
  }
}
```

### POST /envelope → wrap_envelope
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (EnvelopeRequest) → fields: message, realm, metadata
- Example payload:
```json
{
  "req": {
    "message": "example_message",
    "realm": "example_realm",
    "metadata": {}
  }
}
```

### POST /task → execute_task
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (TaskRequest) → fields: kaitiaki, task, input, priority, realm
- Example payload:
```json
{
  "req": {
    "kaitiaki": "example_kaitiaki",
    "task": "example_task",
    "input": {},
    "priority": "example_priority",
    "realm": "example_realm"
  }
}
```

### POST /handoff → handoff_task
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (HandoffRequest) → fields: from_kaitiaki, to_kaitiaki, task_id, context
- Example payload:
```json
{
  "req": {
    "from_kaitiaki": "example_from_kaitiaki",
    "to_kaitiaki": "example_to_kaitiaki",
    "task_id": "example_task_id",
    "context": {}
  }
}
```

### POST /memory/query → query_memory
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (MemoryQueryRequest) → fields: query, top_k, threshold, realm, tapu_level
- Example payload:
```json
{
  "req": {
    "query": "example_query",
    "top_k": 0,
    "threshold": 0,
    "realm": "example_realm",
    "tapu_level": 0
  }
}
```

### POST /memory/store → store_memory
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (MemoryStoreRequest) → fields: content, metadata, realm, tapu_level
- Example payload:
```json
{
  "req": {
    "content": "example_content",
    "metadata": {},
    "realm": "example_realm",
    "tapu_level": 0
  }
}
```

### POST /log → log_activity
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (LogRequest) → fields: event_type, details, realm, severity
- Example payload:
```json
{
  "req": {
    "event_type": "example_event_type",
    "details": {},
    "realm": "example_realm",
    "severity": "example_severity"
  }
}
```

### POST /notify → send_notification
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (NotifyRequest) → fields: recipient, message, channel, priority
- Example payload:
```json
{
  "req": {
    "recipient": "example_recipient",
    "message": "example_message",
    "channel": "example_channel",
    "priority": "example_priority"
  }
}
```

### POST /kaitiaki/register → register_kaitiaki
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (KaitiakiregisterRequest) → fields: name, role, system_prompt, tools, realm
- Example payload:
```json
{
  "req": {
    "name": "example_name",
    "role": "example_role",
    "system_prompt": "example_system_prompt",
    "tools": [],
    "realm": "example_realm"
  }
}
```

### POST /kaitiaki/context → get_kaitiaki_context
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - kaitiaki (str)
  - realm (Optional[str])

### GET /kaitiaki → list_kaitiaki
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 1

### POST /vector/embed → generate_embeddings
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (VectorEmbedRequest) → fields: text, model
- Example payload:
```json
{
  "req": {
    "text": "example_text",
    "model": "example_model"
  }
}
```

### POST /vector/search → semantic_search
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (MemoryQueryRequest) → fields: query, top_k, threshold, realm, tapu_level
- Example payload:
```json
{
  "req": {
    "query": "example_query",
    "top_k": 0,
    "threshold": 0,
    "realm": "example_realm",
    "tapu_level": 0
  }
}
```

### POST /pipeline → run_pipeline
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (PipelineRequest) → fields: name, input, wait, realm
- Example payload:
```json
{
  "req": {
    "name": "example_name",
    "input": {},
    "wait": false,
    "realm": "example_realm"
  }
}
```

### GET /pipelines → list_pipelines
- Module: te_po.routes.awa_protocol
- Whakapapa path: te_po/routes/awa_protocol.py
- Registered route: no
- Mauri score: 1

### POST /git-checklist → run_git_checklist
- Module: te_po.routes.automation
- Whakapapa path: te_po/routes/automation.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (GitChecklistPayload) → fields: message
- Example payload:
```json
{
  "payload": {
    "message": "example_message"
  }
}
```

### POST /tools/run → run_tool
- Module: te_po.routes.kitenga_tool_router
- Whakapapa path: te_po/routes/kitenga_tool_router.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - call (ToolCall) → fields: tool_name, payload
- Example payload:
```json
{
  "call": {
    "tool_name": "example_tool_name",
    "payload": {}
  }
}
```

### GET /tools/list → list_tools
- Module: te_po.routes.kitenga_tool_router
- Whakapapa path: te_po/routes/kitenga_tool_router.py
- Registered route: yes
- Mauri score: 1

### GET /profiles → assistant_profiles
- Module: te_po.routes.assistants_meta
- Whakapapa path: te_po/routes/assistants_meta.py
- Registered route: no
- Mauri score: 1

### POST /review → review_code
- Module: te_po.routes.llama3
- Whakapapa path: te_po/routes/llama3.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (CodeReviewRequest) → fields: code, language, focus
- Example payload:
```json
{
  "req": {
    "code": "example_code",
    "language": "example_language",
    "focus": "example_focus"
  }
}
```

### POST /docstring → generate_docstring
- Module: te_po.routes.llama3
- Whakapapa path: te_po/routes/llama3.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (DocstringRequest) → fields: code, language, style
- Example payload:
```json
{
  "req": {
    "code": "example_code",
    "language": "example_language",
    "style": "example_style"
  }
}
```

### POST /analyze-error → analyze_error
- Module: te_po.routes.llama3
- Whakapapa path: te_po/routes/llama3.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (ErrorAnalysisRequest) → fields: error, context, language
- Example payload:
```json
{
  "req": {
    "error": "example_error",
    "context": "example_context",
    "language": "example_language"
  }
}
```

### GET /status → llama3_status
- Module: te_po.routes.llama3
- Whakapapa path: te_po/routes/llama3.py
- Registered route: yes
- Mauri score: 1

### POST /{realm_id}/recall → realm_recall
- Module: te_po.routes.recall
- Whakapapa path: te_po/routes/recall.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - realm_id (str)
  - payload (RecallRequest) → fields: query, thread_id, top_k, vector_store
- Example payload:
```json
{
  "payload": {
    "query": "example_query",
    "thread_id": "example_thread_id",
    "top_k": 0,
    "vector_store": "example_vector_store"
  }
}
```

### GET /origins → list_origins
- Module: te_po.routes.cors_manager
- Whakapapa path: te_po/routes/cors_manager.py
- Registered route: no
- Mauri score: 1

### POST /origins/add → add_origin
- Module: te_po.routes.cors_manager
- Whakapapa path: te_po/routes/cors_manager.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (OriginRequest) → fields: origin
- Example payload:
```json
{
  "req": {
    "origin": "example_origin"
  }
}
```

### POST /origins/remove → remove_origin
- Module: te_po.routes.cors_manager
- Whakapapa path: te_po/routes/cors_manager.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - req (OriginRequest) → fields: origin
- Example payload:
```json
{
  "req": {
    "origin": "example_origin"
  }
}
```

### POST /origins/reset → reset_origins
- Module: te_po.routes.cors_manager
- Whakapapa path: te_po/routes/cors_manager.py
- Registered route: no
- Mauri score: 1

### POST /query_card_context → query_card_context
- Module: te_po.routes.roshi
- Whakapapa path: te_po/routes/roshi.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (Dict[str, Any])

### GET / → memory_index
- Module: te_po.routes.memory
- Whakapapa path: te_po/routes/memory.py
- Registered route: yes
- Mauri score: 1

### POST /retrieve → memory_retrieve
- Module: te_po.routes.memory
- Whakapapa path: te_po/routes/memory.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (MemoryQuery) → fields: query, top_k, min_similarity
- Example payload:
```json
{
  "payload": {
    "query": "example_query",
    "top_k": 0,
    "min_similarity": 0
  }
}
```

### POST /translate → reo_translate
- Module: te_po.routes.reo
- Whakapapa path: te_po/routes/reo.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - payload (ReoRequest) → fields: text
- Example payload:
```json
{
  "payload": {
    "text": "example_text"
  }
}
```

### POST /explain → reo_explain
- Module: te_po.routes.reo
- Whakapapa path: te_po/routes/reo.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (ReoRequest) → fields: text
- Example payload:
```json
{
  "payload": {
    "text": "example_text"
  }
}
```

### POST /pronounce → reo_pronounce
- Module: te_po.routes.reo
- Whakapapa path: te_po/routes/reo.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (ReoRequest) → fields: text
- Example payload:
```json
{
  "payload": {
    "text": "example_text"
  }
}
```

### POST /create → create_realm
- Module: te_po.routes.realm_generator
- Whakapapa path: te_po/routes/realm_generator.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - request (RealmCreateRequest) → fields: realm_name, kaitiaki_name, kaitiaki_role, kaitiaki_instructions, description, selected_apis, template, cloudflare_hostname, pages_project, backend_url, github_org
- Example payload:
```json
{
  "request": {
    "realm_name": "example_realm_name",
    "kaitiaki_name": "example_kaitiaki_name",
    "kaitiaki_role": "example_kaitiaki_role",
    "kaitiaki_instructions": "example_kaitiaki_instructions",
    "description": "example_description",
    "selected_apis": [],
    "template": "example_template",
    "cloudflare_hostname": "example_cloudflare_hostname",
    "pages_project": "example_pages_project",
    "backend_url": "example_backend_url",
    "github_org": "example_github_org"
  }
}
```

### GET /status/github → github_status
- Module: te_po.routes.realm_generator
- Whakapapa path: te_po/routes/realm_generator.py
- Registered route: no
- Mauri score: 1

### GET /list → list_all_realms
- Module: te_po.routes.realm_generator
- Whakapapa path: te_po/routes/realm_generator.py
- Registered route: no
- Mauri score: 1

### GET /{realm_slug} → get_realm_info
- Module: te_po.routes.realm_generator
- Whakapapa path: te_po/routes/realm_generator.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - realm_slug (str)

### GET /{realm_slug}/sql → get_realm_sql
- Module: te_po.routes.realm_generator
- Whakapapa path: te_po/routes/realm_generator.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - realm_slug (str)
  - kaitiaki_name (str)

### GET /template/info → get_template_info
- Module: te_po.routes.realm_generator
- Whakapapa path: te_po/routes/realm_generator.py
- Registered route: no
- Mauri score: 1

### DELETE /{realm_slug} → delete_realm
- Module: te_po.routes.realm_generator
- Whakapapa path: te_po/routes/realm_generator.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - realm_slug (str)
  - confirm (bool)

### GET /metrics → metrics
- Module: te_po.routes.metrics
- Whakapapa path: te_po/routes/metrics.py
- Registered route: no
- Mauri score: 1

### GET /recent → recent_logs
- Module: te_po.routes.logs
- Whakapapa path: te_po/routes/logs.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - limit (int)
  - contains (str | None)

### POST /ocr/scan → scan
- Module: te_po.routes.ocr
- Whakapapa path: te_po/routes/ocr.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - file (UploadFile)

### POST /ocr/stealth → stealth_scan
- Module: te_po.routes.ocr
- Whakapapa path: te_po/routes/ocr.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - file (UploadFile)

### POST /ocr/stealth-testit → stealth_scan_testit
- Module: te_po.routes.ocr
- Whakapapa path: te_po/routes/ocr.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - file (UploadFile)

### POST /ocr → intake_ocr
- Module: te_po.routes.intake
- Whakapapa path: te_po/routes/intake.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - file (UploadFile)

### POST /summarize → intake_summarize
- Module: te_po.routes.intake
- Whakapapa path: te_po/routes/intake.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (SummarizeRequest) → fields: text, mode
- Example payload:
```json
{
  "payload": {
    "text": "example_text",
    "mode": "example_mode"
  }
}
```

### GET /bridge/test → bridge_test
- Module: te_po.routes.awa
- Whakapapa path: te_po/routes/awa.py
- Registered route: no
- Mauri score: 1

### POST /awa/orchestrate → awa_orchestrate
- Module: te_po.routes.awa
- Whakapapa path: te_po/routes/awa.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - request (Request)

### POST /gpt/bridge → gpt_bridge
- Module: te_po.routes.awa
- Whakapapa path: te_po/routes/awa.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - request (Request)

### POST /add_to_csv → add_to_csv
- Module: te_po.routes.sell
- Whakapapa path: te_po/routes/sell.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - data (Dict[str, Any])

### POST /vision-ocr → vision_ocr
- Module: te_po.routes.kitenga_backend
- Whakapapa path: te_po/routes/kitenga_backend.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - payload (VisionOCRRequest) → fields: image_base64, save_vector, run_pipeline, pipeline_source
  - authorization (str | None)
- Example payload:
```json
{
  "payload": {
    "image_base64": "example_image_base64",
    "save_vector": false,
    "run_pipeline": false,
    "pipeline_source": "example_pipeline_source"
  }
}
```

### POST /cards/scan → scan_cards
- Module: te_po.routes.kitenga_backend
- Whakapapa path: te_po/routes/kitenga_backend.py
- Registered route: no
- Mauri score: 5
- Parameters:
  - request (Request)
  - front (UploadFile | None)
  - back (UploadFile | None)
  - payload (CardScanRequest | None)

### POST /tool/ocr → ocr_tool_handler
- Module: te_po.routes.kitenga_backend
- Whakapapa path: te_po/routes/kitenga_backend.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (OcrToolRequest) → fields: file_url, taonga_mode, prefer_offline
- Example payload:
```json
{
  "payload": {
    "file_url": "example_file_url",
    "taonga_mode": false,
    "prefer_offline": false
  }
}
```

### POST /tool/translate → translate_tool_handler
- Module: te_po.routes.kitenga_backend
- Whakapapa path: te_po/routes/kitenga_backend.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - payload (TranslateToolRequest) → fields: text, target_language, context
- Example payload:
```json
{
  "payload": {
    "text": "example_text",
    "target_language": "example_target_language",
    "context": "example_context"
  }
}
```

### POST /ask → ask_kitenga
- Module: te_po.routes.kitenga_backend
- Whakapapa path: te_po/routes/kitenga_backend.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - request (KitengaAskRequest) → fields: prompt, session_id, thread_id, metadata
- Example payload:
```json
{
  "request": {
    "prompt": "example_prompt",
    "session_id": "example_session_id",
    "thread_id": "example_thread_id",
    "metadata": {}
  }
}
```

### POST /gpt-whisper → gpt_whisper
- Module: te_po.routes.kitenga_backend
- Whakapapa path: te_po/routes/kitenga_backend.py
- Registered route: yes
- Mauri score: 10
- Parameters:
  - request (Request)
  - payload (WhisperRequest | None)
  - file (UploadFile | None)
  - whisper (str | None)
  - session_id (str | None)
  - session_id_q (str | None)
  - thread_id (str | None)
  - system_prompt (str | None)
  - run_pipeline (bool | str)
  - save_vector (bool | str)
  - use_retrieval (bool | str)
  - use_openai_summary (bool | str)
  - use_openai_translation (bool | str)
  - mode (str | None)
  - allow_taonga_store (bool | str)
  - source (str | None)
  - authorization (str | None)

### POST /run_pipeline → run_pipeline_endpoint
- Module: te_po.routes.kitenga_backend
- Whakapapa path: te_po/routes/kitenga_backend.py
- Registered route: no
- Mauri score: 5
- Parameters:
  - pipeline_name (str)
  - input_data (str)
  - realm_name (str)
  - verbose (bool)

### POST /query_knowledge_base → query_knowledge_base
- Module: te_po.routes.kitenga_backend
- Whakapapa path: te_po/routes/kitenga_backend.py
- Registered route: no
- Mauri score: 4
- Parameters:
  - query (str)
  - top_k (int)
  - min_similarity (float)

### GET /ledger → ledger
- Module: te_po.routes.state
- Whakapapa path: te_po/routes/state.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - limit (int)

### GET /state → state
- Module: te_po.routes.state
- Whakapapa path: te_po/routes/state.py
- Registered route: no
- Mauri score: 1

### GET /state/public → get_public_state_endpoint
- Module: te_po.routes.state
- Whakapapa path: te_po/routes/state.py
- Registered route: no
- Mauri score: 1

### GET /state/private → get_private_state_endpoint
- Module: te_po.routes.state
- Whakapapa path: te_po/routes/state.py
- Registered route: no
- Mauri score: 1

### GET /state/version → get_state_version_endpoint
- Module: te_po.routes.state
- Whakapapa path: te_po/routes/state.py
- Registered route: no
- Mauri score: 1

### POST /ocr → dev_ocr
- Module: te_po.routes.dev
- Whakapapa path: te_po/routes/dev.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - file (UploadFile)

### GET /clean → dev_clean
- Module: te_po.routes.dev
- Whakapapa path: te_po/routes/dev.py
- Registered route: no
- Mauri score: 1

### GET /chunk → dev_chunk
- Module: te_po.routes.dev
- Whakapapa path: te_po/routes/dev.py
- Registered route: no
- Mauri score: 1

### GET /openai → dev_openai
- Module: te_po.routes.dev
- Whakapapa path: te_po/routes/dev.py
- Registered route: no
- Mauri score: 1

### POST /summarise → dev_summarise
- Module: te_po.routes.dev
- Whakapapa path: te_po/routes/dev.py
- Registered route: no
- Mauri score: 3
- Parameters:
  - text (str)
  - mode (str)

### POST /ollama → dev_ollama
- Module: te_po.routes.dev
- Whakapapa path: te_po/routes/dev.py
- Registered route: no
- Mauri score: 4
- Parameters:
  - prompt (str)
  - system_prompt (str)
  - model (str)

### GET /routes → list_routes
- Module: te_po.routes.dev
- Whakapapa path: te_po/routes/dev.py
- Registered route: no
- Mauri score: 1

### GET /kitenga-status → kitenga_status
- Module: te_po.routes.dev
- Whakapapa path: te_po/routes/dev.py
- Registered route: no
- Mauri score: 1

### GET / → get_ui
- Module: te_hau.scripts.realm_ui
- Whakapapa path: te_hau/scripts/realm_ui.py
- Registered route: yes
- Mauri score: 1

### POST /api/generate → generate_realm
- Module: te_hau.scripts.realm_ui
- Whakapapa path: te_hau/scripts/realm_ui.py
- Registered route: yes
- Mauri score: 2
- Parameters:
  - request (RealmRequest) → fields: name, slug, kaitiaki_name, kaitiaki_role, description, push_to_git
- Example payload:
```json
{
  "request": {
    "name": "example_name",
    "slug": "example_slug",
    "kaitiaki_name": "example_kaitiaki_name",
    "kaitiaki_role": "example_kaitiaki_role",
    "description": "example_description",
    "push_to_git": "example_push_to_git"
  }
}
```

### GET /api/status → get_status
- Module: te_hau.scripts.realm_ui
- Whakapapa path: te_hau/scripts/realm_ui.py
- Registered route: yes
- Mauri score: 1

### GET /status → status
- Module: kitenga_mcp.cloudflare.server
- Whakapapa path: kitenga_mcp/cloudflare/server.py
- Registered route: yes
- Mauri score: 1

### GET /status → status
- Module: kitenga_mcp.render.server
- Whakapapa path: kitenga_mcp/render/server.py
- Registered route: yes
- Mauri score: 1

### GET /status → status
- Module: kitenga_mcp.openai.server
- Whakapapa path: kitenga_mcp/openai/server.py
- Registered route: yes
- Mauri score: 1

### GET /list → list_tools
- Module: kitenga_mcp.tools.__init__
- Whakapapa path: kitenga_mcp/tools/__init__.py
- Registered route: no
- Mauri score: 1

### POST /register → register_tool
- Module: kitenga_mcp.tools.__init__
- Whakapapa path: kitenga_mcp/tools/__init__.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - tool (ToolDefinition) → fields: id, name, description, route, method, inputs, output_description
- Example payload:
```json
{
  "tool": {
    "id": "example_id",
    "name": "example_name",
    "description": "example_description",
    "route": "example_route",
    "method": "example_method",
    "inputs": [],
    "output_description": "example_output_description"
  }
}
```

### GET /manifests → list_manifests
- Module: kitenga_mcp.tools.__init__
- Whakapapa path: kitenga_mcp/tools/__init__.py
- Registered route: no
- Mauri score: 1

### GET /manifests/{name} → get_manifest
- Module: kitenga_mcp.tools.__init__
- Whakapapa path: kitenga_mcp/tools/__init__.py
- Registered route: no
- Mauri score: 2
- Parameters:
  - name (str)

### GET /status → status
- Module: kitenga_mcp.tepo.server
- Whakapapa path: kitenga_mcp/tepo/server.py
- Registered route: yes
- Mauri score: 1

### GET /status → status
- Module: kitenga_mcp.supabase.server
- Whakapapa path: kitenga_mcp/supabase/server.py
- Registered route: yes
- Mauri score: 1

### GET /status → status
- Module: kitenga_mcp.git.server
- Whakapapa path: kitenga_mcp/git/server.py
- Registered route: yes
- Mauri score: 1

## Drift Observations
- Added: 0
- Removed: 0
- Changed: 0

## Notes
- Karakia: E rere ana te awa o ngā whakaaro, kia tau te mauri o tēnei mahi. Haumi e, hui e, tāiki e.

---
Author: awa developer (Kitenga Whiro [Adrian Hemi])
Protection: {"kaitiaki_signature": "k9_72c5c83f24066e71", "encoding_version": "tawhiri_v1.0", "cultural_protection": "active", "ownership": "AwaNet Kaitiaki Collective", "theft_protection": true, "original_hash": "72c5c83f24066e71", "encoding_timestamp": "2025-10-21", "liberation_marker": "w4o4_protected"}
