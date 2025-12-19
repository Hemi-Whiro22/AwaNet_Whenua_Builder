### te_po.core.main

- `N/A` / — — | body: None | query: — | path: — | response: None
- `GET` / — — | body: None | query: — | path: — | response: None
- `N/A` /heartbeat — — | body: None | query: — | path: — | response: None
- `GET` /heartbeat — — | body: None | query: — | path: — | response: None


### te_po.routes.assistant

- `POST` /assistant/create — Create an OpenAI Assistant with optional vector store.
    Used by Realm Generator to spin up kaitiaki with their own vector stores.
    
    Payload:
    - name: Assistant name (required)
    - instructions: System instructions (required)
    - model: Model to use (default: gpt-4o)
    - create_vector_store: Whether to create a vector store (default: True)
    - vector_store_name: Name for the vector store | body: <class 'dict'> | query: — | path: — | response: None
- `GET` /assistant/list — List all OpenAI assistants. | body: None | query: limit:int?=20 | path: — | response: None
- `POST` /assistant/run — Bridge endpoint for assistant tool-calls.
    Accepts either:
    - file_url: URL to fetch file bytes
    - text: inline text to process | body: <class 'dict'> | query: — | path: — | response: None
- `GET` /assistant/vector-stores — List all OpenAI vector stores. | body: None | query: limit:int?=20 | path: — | response: None


### te_po.routes.assistants_meta

- `GET` /assistants/profiles — Return assistant profile definitions for QA/Ops wiring. | body: None | query: — | path: — | response: None


### te_po.routes.awa_protocol

- `POST` /awa/envelope — Wrap message with realm context.
    Adds realm identity, timestamp, and metadata. | body: EnvelopeRequest (message:str=PydanticUndefined, realm:typing.Optional[str]?, metadata:typing.Optional[typing.Dict[str, typing.Any]]?) | query: — | path: — | response: None
- `POST` /awa/handoff — Transfer task between kaitiaki.
    Records context transfer and updates ownership. | body: HandoffRequest (from_kaitiaki:str=PydanticUndefined, to_kaitiaki:str=PydanticUndefined, task_id:str=PydanticUndefined, context:typing.Optional[typing.Dict[str, typing.Any]]?) | query: — | path: — | response: None
- `GET` /awa/kaitiaki — List all registered kaitiaki in the system. | body: None | query: — | path: — | response: None
- `POST` /awa/kaitiaki/context — Get context (state, capabilities, memory) for a kaitiaki. | body: None | query: kaitiaki:str=PydanticUndefined, realm:typing.Optional[str]? | path: — | response: None
- `POST` /awa/kaitiaki/register — Register a new kaitiaki (guardian agent).
    Stores role, system prompt, and tool definitions. | body: KaitiakiregisterRequest (name:str=PydanticUndefined, role:str=PydanticUndefined, system_prompt:str=PydanticUndefined, tools:typing.Optional[typing.List[str]]?, realm:typing.Optional[str]?) | query: — | path: — | response: None
- `POST` /awa/log — Log activity to carving log.
    Creates immutable audit trail entry. | body: LogRequest (event_type:str=PydanticUndefined, details:typing.Dict[str, typing.Any]=PydanticUndefined, realm:typing.Optional[str]?, severity:str?=info) | query: — | path: — | response: None
- `POST` /awa/memory/query — Semantic search across vector memory.
    Returns documents with similarity scores. | body: MemoryQueryRequest (query:str=PydanticUndefined, top_k:int?=5, threshold:float?=0.7, realm:typing.Optional[str]?, tapu_level:typing.Optional[int]?) | query: — | path: — | response: None
- `POST` /awa/memory/store — Store content to vector memory with embedding.
    Assigns tapu level and metadata. | body: MemoryStoreRequest (content:str=PydanticUndefined, metadata:typing.Optional[typing.Dict[str, typing.Any]]?, realm:typing.Optional[str]?, tapu_level:int?=0) | query: — | path: — | response: None
- `POST` /awa/notify — Send notification to recipient.
    Supports multiple channels (Slack, email, realtime). | body: NotifyRequest (recipient:str=PydanticUndefined, message:str=PydanticUndefined, channel:str?=default, priority:str?=normal) | query: — | path: — | response: None
- `POST` /awa/pipeline — Execute a Te Pō pipeline.
    Valid pipelines: ocr, summarise, translate, embed, taonga | body: PipelineRequest (name:str=PydanticUndefined, input:typing.Dict[str, typing.Any]=PydanticUndefined, wait:bool?=False, realm:typing.Optional[str]?) | query: — | path: — | response: None
- `GET` /awa/pipelines — List available pipelines. | body: None | query: — | path: — | response: None
- `POST` /awa/task — Execute a kaitiaki task.
    Routes to the specified kaitiaki with task details. | body: TaskRequest (kaitiaki:str=PydanticUndefined, task:str=PydanticUndefined, input:typing.Dict[str, typing.Any]=PydanticUndefined, priority:str?=normal, realm:typing.Optional[str]?) | query: — | path: — | response: None
- `POST` /awa/vector/embed — Generate embeddings for text.
    Uses configured embedding model (OpenAI). | body: VectorEmbedRequest (text:str=PydanticUndefined, model:typing.Optional[str]?) | query: — | path: — | response: None
- `POST` /awa/vector/search — Semantic search (alias for /awa/memory/query). | body: MemoryQueryRequest (query:str=PydanticUndefined, top_k:int?=5, threshold:float?=0.7, realm:typing.Optional[str]?, tapu_level:typing.Optional[int]?) | query: — | path: — | response: None


### te_po.routes.cards

- `POST` /cards/build-csv — Build a CSV from a list of card objects.
    groups_of: batch size (default 10) for splitting files client-side. | body: <class 'typing._GenericAlias'> | query: — | path: — | response: None
- `POST` /cards/build-row — Build a Trade Me-ready row from card metadata. | body: <class 'typing._GenericAlias'> | query: — | path: — | response: None
- `POST` /cards/estimate-value — Aggregate multi-source valuation for a trading card. | body: <class 'typing._GenericAlias'> | query: — | path: — | response: None
- `POST` /cards/scan-image — Run OCR on a card photo to extract card details (name, number, rarity). | body: Body_scan_image_cards_scan_image_post (image:UploadFile=PydanticUndefined) | query: — | path: — | response: None
- `POST` /cards/upload-image — Upload a single card image to Supabase storage and return its public URL. | body: Body_upload_image_cards_upload_image_post (image:UploadFile=PydanticUndefined) | query: — | path: — | response: None
- `POST` /cards/value — Lookup card value from reference; fallback to default. | body: <class 'typing._GenericAlias'> | query: — | path: — | response: None


### te_po.routes.chat

- `POST` /chat/save-session — Finalize/save a chat session: optional summary, tag, and store in Supabase logs.
    - session_id: chat session identifier
    - title: optional human-friendly title
    - tags: optional comma-separated tags
    - summarize: when true, attempts an OpenAI summary of session context | body: None | query: session_id:str=PydanticUndefined, title:typing.Optional[str]?, tags:typing.Optional[str]?, summarize:bool?=True, summary_words:int?=300, write_ari:bool?=False | path: — | response: None


### te_po.routes.cors_manager

- `GET` /cors/origins — List all currently allowed CORS origins. | body: None | query: — | path: — | response: OriginsResponse
- `POST` /cors/origins/add — Add a new CORS origin at runtime. | body: OriginRequest (origin:str=PydanticUndefined) | query: — | path: — | response: None
- `POST` /cors/origins/remove — Remove a CORS origin at runtime. | body: OriginRequest (origin:str=PydanticUndefined) | query: — | path: — | response: None
- `POST` /cors/origins/reset — Reset CORS origins to defaults. | body: None | query: — | path: — | response: None


### te_po.routes.dev

- `GET` /dev/chunk — — | body: None | query: — | path: — | response: None
- `GET` /dev/clean — — | body: None | query: — | path: — | response: None
- `GET` /dev/kitenga-status — Get Kitenga Whiro configuration status. | body: None | query: — | path: — | response: None
- `POST` /dev/ocr — — | body: Body_dev_ocr_dev_ocr_post (file:UploadFile=PydanticUndefined) | query: — | path: — | response: None
- `POST` /dev/ollama — Quick chat endpoint for the local Ollama (Llama 3) runtime. | body: Body_dev_ollama_dev_ollama_post (prompt:str=PydanticUndefined, system_prompt:str?=You are a helpful Māori research assistant., model:str?) | query: — | path: — | response: None
- `GET` /dev/openai — — | body: None | query: — | path: — | response: None
- `GET` /dev/routes — List all registered routes in the application. | body: None | query: — | path: — | response: None
- `POST` /dev/summarise — — | body: Body_dev_summarise_dev_summarise_post (text:str=PydanticUndefined, mode:str?=research) | query: — | path: — | response: None


### te_po.routes.documents

- `GET` /documents/profiles — Return recent document profiles from local pipeline logs (best-effort) and Supabase metadata if available. | body: None | query: limit:int?=50 | path: — | response: None


### te_po.routes.intake

- `POST` /intake/ocr — — | body: Body_intake_ocr_intake_ocr_post (file:UploadFile=PydanticUndefined) | query: — | path: — | response: None
- `POST` /intake/summarize — — | body: SummarizeRequest (text:str=PydanticUndefined, mode:str=PydanticUndefined) | query: — | path: — | response: None


### te_po.routes.kitenga_backend

- `POST` /kitenga/ask — Relay Te Ao chat prompts to the configured OpenAI assistant using the Assistants API. | body: KitengaAskRequest (prompt:str=PydanticUndefined, session_id:str | None?, thread_id:str | None?, metadata:typing.Optional[typing.Dict[str, typing.Any]]?) | query: — | path: — | response: None
- `POST` /kitenga/cards/scan — Scan DBS cards (front/back), extract metadata, estimate value, and persist to Supabase.
    - Accepts multipart with front/back UploadFile or JSON with URLs.
    - Uses StealthOCR -> parsed metadata -> optional Brave price estimate.
    - Stores raw/process artifacts in Supabase bucket `ocr_cards` and rows in `card_scans`. | body: Body_scan_cards_kitenga_cards_scan_post (front:fastapi.datastructures.UploadFile | None?, back:fastapi.datastructures.UploadFile | None?, payload:te_po.routes.kitenga_backend.CardScanRequest | None?) | query: — | path: — | response: None
- `POST` /kitenga/gpt-whisper — Free-form text -> OpenAI response with optional retrieval/pipeline/vector persistence. Supports JSON or multipart/form-data with file. | body: Body_gpt_whisper_kitenga_gpt_whisper_post (payload:te_po.routes.kitenga_backend.WhisperRequest | None?, file:fastapi.datastructures.UploadFile | None?, whisper:str | None?, session_id:str | None?, thread_id:str | None?, system_prompt:str | None?, run_pipeline:bool | str?=False, save_vector:bool | str?=False, use_retrieval:bool | str?=False, use_openai_summary:bool | str?=False, use_openai_translation:bool | str?=False, mode:str | None?=research, allow_taonga_store:bool | str?=False, source:str | None?) | query: session_id_q:str | None? | path: — | response: None
- `POST` /kitenga/query_knowledge_base — Endpoint to query the knowledge base using vector search.
    Args:
        query: The search query string.
        top_k: Number of top results to return.
        min_similarity: Minimum similarity threshold for results.
    Returns:
        A list of matching knowledge base entries. | body: Body_query_knowledge_base_kitenga_query_knowledge_base_post (query:str=PydanticUndefined, top_k:int?=5, min_similarity:float?=0.7) | query: — | path: — | response: None
- `POST` /kitenga/run_pipeline — Endpoint to execute a pipeline.
    Args:
        pipeline_name: Name of the pipeline to execute.
        input_data: Input data for the pipeline.
        realm_name: Realm in which the pipeline resides.
        verbose: Whether to show detailed logs.
    Returns:
        Pipeline execution results. | body: Body_run_pipeline_endpoint_kitenga_run_pipeline_post (pipeline_name:str=PydanticUndefined, input_data:str=PydanticUndefined, realm_name:str?=Te_Po, verbose:bool?=False) | query: — | path: — | response: None
- `POST` /kitenga/tool/ocr — — | body: OcrToolRequest (file_url:str=PydanticUndefined, taonga_mode:bool?=False, prefer_offline:bool?=True) | query: — | path: — | response: None
- `POST` /kitenga/tool/translate — — | body: TranslateToolRequest (text:str=PydanticUndefined, target_language:str?=mi, context:str | None?) | query: — | path: — | response: None
- `POST` /kitenga/vision-ocr — Extract text from an image via OpenAI vision; optionally persist to vector store. | body: VisionOCRRequest (image_base64:str=PydanticUndefined, save_vector:bool?=False, run_pipeline:bool?=False, pipeline_source:str | None?) | query: — | path: — | response: None


### te_po.routes.kitenga_db

- `GET` /kitenga/db/chat/history/{session_id} — Get chat history for a session. | body: None | query: limit:int?=50 | path: session_id:str | response: None
- `POST` /kitenga/db/chat/log — Save a chat log entry. | body: ChatLogRequest (session_id:str=PydanticUndefined, user_message:str=PydanticUndefined, assistant_reply:str=PydanticUndefined, thread_id:typing.Optional[str]?, mode:str?=chat, metadata:typing.Optional[typing.Dict[str, typing.Any]]?) | query: — | path: — | response: None
- `POST` /kitenga/db/logs — Create a log entry in kitenga.logs. | body: LogEventRequest (event:str=PydanticUndefined, detail:str=PydanticUndefined, source:str?=kitenga_whiro, data:typing.Optional[typing.Dict[str, typing.Any]]?) | query: — | path: — | response: None
- `GET` /kitenga/db/logs/recent — Get recent log entries. | body: None | query: limit:int?=50, source:str? | path: — | response: None
- `POST` /kitenga/db/memory — Store context memory. | body: MemoryRequest (content:str=PydanticUndefined, metadata:typing.Optional[typing.Dict[str, typing.Any]]?) | query: — | path: — | response: None
- `POST` /kitenga/db/memory/search — Search context memory. | body: SearchRequest (query:str=PydanticUndefined, limit:int?=10) | query: — | path: — | response: None
- `GET` /kitenga/db/pipeline/recent — Get recent pipeline runs. | body: None | query: limit:int?=20 | path: — | response: None
- `GET` /kitenga/db/stats — Get kitenga schema statistics. | body: None | query: — | path: — | response: None
- `GET` /kitenga/db/status — Check kitenga schema connection status. | body: None | query: — | path: — | response: None
- `POST` /kitenga/db/taonga — Store a taonga. | body: TaongaRequest (title:str=PydanticUndefined, content:str=PydanticUndefined, metadata:typing.Optional[typing.Dict[str, typing.Any]]?) | query: — | path: — | response: None
- `POST` /kitenga/db/taonga/search — Search taonga. | body: SearchRequest (query:str=PydanticUndefined, limit:int?=10) | query: — | path: — | response: None
- `GET` /kitenga/db/taonga/{taonga_id} — Get a taonga by ID. | body: None | query: — | path: taonga_id:str | response: None
- `POST` /kitenga/db/whakapapa — Log to whakapapa (lineage). | body: WhakapapaRequest (id:str=PydanticUndefined, title:str=PydanticUndefined, category:str=PydanticUndefined, summary:str=PydanticUndefined, content_type:str?=event, data:typing.Optional[typing.Dict[str, typing.Any]]?, author:str?=kitenga_whiro) | query: — | path: — | response: None


### te_po.routes.llama3

- `POST` /awa/llama3/analyze-error — Analyze an error and suggest solutions. | body: ErrorAnalysisRequest (error:str=PydanticUndefined, context:typing.Optional[str]?, language:typing.Optional[str]?) | query: — | path: — | response: ErrorAnalysisResponse
- `POST` /awa/llama3/docstring — Generate docstring for code. | body: DocstringRequest (code:str=PydanticUndefined, language:str?=python, style:str?=numpy) | query: — | path: — | response: DocstringResponse
- `POST` /awa/llama3/review — Review code for issues and improvements. | body: CodeReviewRequest (code:str=PydanticUndefined, language:str?=python, focus:typing.Optional[str]?) | query: — | path: — | response: CodeReviewResponse
- `GET` /awa/llama3/status — Check if Llama3 is available. | body: None | query: — | path: — | response: None


### te_po.routes.logs

- `GET` /logs/recent — Return the most recent audit events (reverse chronological). | body: None | query: limit:int?=50, contains:str | None? | path: — | response: None


### te_po.routes.memory

- `GET` /memory/ — — | body: None | query: — | path: — | response: None
- `POST` /memory/retrieve — — | body: MemoryQuery (query:str=PydanticUndefined, top_k:int | None?=5, min_similarity:float | None?=0.0) | query: — | path: — | response: None


### te_po.routes.metrics

- `GET` /metrics — — | body: None | query: — | path: — | response: None


### te_po.routes.ocr

- `POST` /ocr/scan — — | body: Body_scan_ocr_scan_post (file:UploadFile=PydanticUndefined) | query: — | path: — | response: None
- `POST` /ocr/stealth — Direct StealthOCR test endpoint using real Tesseract + vision fallback (with cultural protection).
    Returns the protected text and metadata; does NOT run the full pipeline. | body: Body_stealth_scan_ocr_stealth_post (file:UploadFile=PydanticUndefined) | query: — | path: — | response: None
- `POST` /ocr/stealth-testit — Alternate StealthOCR test endpoint using the testit class (real Tesseract + vision).
    Useful to compare behaviors without touching the main pipeline. | body: Body_stealth_scan_testit_ocr_stealth_testit_post (file:UploadFile=PydanticUndefined) | query: — | path: — | response: None


### te_po.routes.pipeline

- `POST` /pipeline/batch — Enqueue multiple files; returns batch_id and job_ids. | body: Body_enqueue_batch_pipeline_batch_post (files:typing.List[fastapi.datastructures.UploadFile]=PydanticUndefined) | query: — | path: — | response: None
- `GET` /pipeline/batch-status/{batch_id} — — | body: None | query: — | path: batch_id:str | response: None
- `POST` /pipeline/cancel/{job_id} — — | body: None | query: — | path: job_id:str | response: None
- `POST` /pipeline/enqueue — Enqueue a pipeline job (inline mode) or to Redis/RQ (RQ mode).
    
    Queue mode controlled by QUEUE_MODE env var:
    - inline (default): Run immediately in-process, no Redis required
    - rq: Use Redis queue, requires Redis configured
    
    Returns:
    - Inline mode: {job_id, status, result?, error?}
    - RQ mode: {job_id, rq_job_id, queue, realm, status}
    
    Optional header: X-Realm (for multi-tenant tracking) | body: Body_enqueue_pipeline_pipeline_enqueue_post (file:UploadFile=PydanticUndefined) | query: — | path: — | response: None
- `GET` /pipeline/health/queue — Health check for queue system.
    
    In inline mode: Returns 'disabled' (no Redis needed).
    In RQ mode: Checks Redis connectivity and queue lengths. | body: None | query: — | path: — | response: None
- `GET` /pipeline/jobs/recent — Get recent pipeline jobs from PostgreSQL for dashboarding.
    
    Query parameters:
    - limit: Max results (default 50, max 500)
    - realm: Filter by realm (optional)
    - queue: Filter by queue (urgent/default/slow) (optional)
    - status: Filter by status (queued/running/finished/failed) (optional) | body: None | query: limit:int?=50, realm:str | None?, queue:str | None?, status:str | None? | path: — | response: None
- `POST` /pipeline/run — Run the pipeline on an uploaded file (preferred) or inline text. | body: Body_pipeline_run_pipeline_run_post (file:fastapi.datastructures.UploadFile | None?, text:str | None?, source:str?=api) | query: — | path: — | response: None
- `GET` /pipeline/status/{job_id} — Return the pipeline job status from PostgreSQL (durable tracking).
    
    Includes: status, result, error, started_at, finished_at, queue, realm.
    Falls back to Supabase if PostgreSQL unavailable (backward compat). | body: None | query: — | path: job_id:str | response: None


### te_po.routes.realm_generator

- `POST` /realms/create — Create a new realm from template
    
    This will:
    1. Create an OpenAI assistant for the realm's kaitiaki
    2. Create a vector store for the realm's knowledge
    3. Copy the project template to /realms/{realm_slug}/
    4. Replace all placeholders with realm-specific values
    5. Generate realm config and README
    6. Initialize git repo (user pushes when ready) | body: RealmCreateRequest (realm_name:str=PydanticUndefined, kaitiaki_name:typing.Optional[str]?, kaitiaki_role:typing.Optional[str]?, kaitiaki_instructions:typing.Optional[str]?, description:typing.Optional[str]?, selected_apis:typing.Optional[list]?, template:typing.Optional[str]?=basic, cloudflare_hostname:typing.Optional[str]?, pages_project:typing.Optional[str]?, backend_url:typing.Optional[str]?, github_org:typing.Optional[str]?) | query: — | path: — | response: RealmResponse
- `GET` /realms/list — List all spawned realms
    
    Returns all realms in the /realms/ directory with their configs | body: None | query: — | path: — | response: RealmResponse
- `GET` /realms/status/github — Check if GitHub integration is available | body: None | query: — | path: — | response: None
- `GET` /realms/template/info — Get information about the realm template
    
    Returns the template config showing what placeholders and secrets are needed | body: None | query: — | path: — | response: None
- `DELETE` /realms/{realm_slug} — Delete a realm
    
    WARNING: This permanently deletes the realm folder.
    Does NOT delete OpenAI resources (assistant, vector store).
    
    Args:
        realm_slug: The slug identifier for the realm
        confirm: Must be True to actually delete | body: None | query: confirm:bool?=False | path: realm_slug:str | response: RealmResponse
- `GET` /realms/{realm_slug} — Get information about a specific realm
    
    Args:
        realm_slug: The slug identifier for the realm (e.g., te_wai) | body: None | query: — | path: realm_slug:str | response: RealmResponse
- `GET` /realms/{realm_slug}/sql — Get the SQL migration script for a realm's tables
    
    Args:
        realm_slug: The slug identifier for the realm
        kaitiaki_name: Name of the kaitiaki guardian | body: None | query: kaitiaki_name:str?=Kaitiaki | path: realm_slug:str | response: None


### te_po.routes.recall

- `POST` /{realm_id}/recall — Retrieve realm-scoped recall matches. | body: RecallRequest (query:str=PydanticUndefined, thread_id:str | None?, top_k:int | None?, vector_store:str | None?) | query: — | path: realm_id:str | response: None


### te_po.routes.reo

- `POST` /reo/explain — — | body: ReoRequest (text:str=PydanticUndefined) | query: — | path: — | response: None
- `POST` /reo/pronounce — — | body: ReoRequest (text:str=PydanticUndefined) | query: — | path: — | response: None
- `POST` /reo/translate — — | body: ReoRequest (text:str=PydanticUndefined) | query: — | path: — | response: None


### te_po.routes.research

- `POST` /research/query — — | body: <class 'dict'> | query: — | path: — | response: None
- `POST` /research/stacked — Layered research: local vector search -> recent docs -> web/LLM fallback. | body: <class 'dict'> | query: — | path: — | response: None
- `POST` /research/web_search — Web search via Brave API with optional site filters. Falls back to stacked search if missing key, empty, or failure. | body: <class 'dict'> | query: — | path: — | response: None


### te_po.routes.roshi

- `POST` /roshi/query_card_context — Vector search over card_context_index. Body: { query: "text" } | body: <class 'typing._GenericAlias'> | query: — | path: — | response: None


### te_po.routes.sell

- `POST` /sell/add_to_csv — Log a card for Trade Me CSV output by inserting into cards_for_sale. | body: <class 'typing._GenericAlias'> | query: — | path: — | response: None


### te_po.routes.state

- `GET` /logs/ledger — Return recent carving ledger entries from Mauri state. | body: None | query: limit:int?=200 | path: — | response: None
- `GET` /logs/state — Return Te Pō state summary from Mauri. | body: None | query: — | path: — | response: None
- `GET` /logs/state/private — Fetch the private project state. Protected by BearerAuthMiddleware. | body: None | query: — | path: — | response: None
- `GET` /logs/state/public — Fetch the public project state. | body: None | query: — | path: — | response: None
- `GET` /logs/state/version — Fetch the current state version. | body: None | query: — | path: — | response: None


### te_po.routes.status

- `GET` /status — Lightweight health endpoint for Te Pō. | body: None | query: — | path: — | response: None
- `GET` /status/full — — | body: None | query: — | path: — | response: None
- `GET` /status/openai — Check OpenAI readiness (key present, optional vector store reachable). | body: None | query: — | path: — | response: None


### te_po.routes.vector

- `GET` /vector/batch-status — Check the status of a vector store file batch (GA OpenAI API). | body: None | query: batch_id:str=PydanticUndefined, vector_store_id:str | None? | path: — | response: None
- `POST` /vector/embed — — | body: EmbedRequest (text:str=PydanticUndefined) | query: — | path: — | response: None
- `GET` /vector/recent — Return recent vector logs saved locally (te_po/storage/openai/<glyph>.json).
    Useful for UI 'recent vectors' display. | body: None | query: limit:int?=5 | path: — | response: None
- `POST` /vector/retrieval-test — Run a simple retrieval against stored embeddings for confidence checks. | body: SearchRequest (query:str=PydanticUndefined, top_k:typing.Optional[int]?=5) | query: — | path: — | response: None
- `POST` /vector/search — — | body: SearchRequest (query:str=PydanticUndefined, top_k:typing.Optional[int]?=5) | query: — | path: — | response: None

