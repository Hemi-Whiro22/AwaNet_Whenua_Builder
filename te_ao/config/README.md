## Te Ao Tooling & Assistants

- Load `te_po/openai_tools.json` for tool definitions. Base URL comes from `TE_PO_BASE_URL`, auth token from `PIPELINE_TOKEN`.
- Assistant IDs: use `OPENAI_ASSISTANT_ID_QA` for the chat panel, `OPENAI_ASSISTANT_ID_OPS` for broader tool access. Pass `OPENAI_VECTOR_STORE_ID` to assistants so retrieval covers ingested docs.
- UI tips:
  - Show assistant + vector store info in the panel header.
  - Expose tools as actions: pipeline run (text/file), vision OCR (optionally run pipeline), assistant bridge, vector batch status.
  - Display recent ingestions and batch progress (from pipeline responses and `/vector/batch-status`).
- Whisper endpoint (`/kitenga/gpt-whisper`) can drive the chat UI. Payload supports: `whisper`, `session_id`, `thread_id`, optional `system_prompt`, `use_retrieval` (routes through QA assistant + vector store), `run_pipeline`, `save_vector`, `source`. Returns `response`, `mode`, `thread_id`, plus optional `pipeline`/`vector`.
- State & ledger: mauri/state/te_po_state.json captures assistants/tools/routes; mauri/state/te_po_carving_log.jsonl holds the carve ledger. API mirrors at `/logs/state` and `/logs/ledger`.
- Documents API: `/documents/profiles` returns recent pipeline runs and Supabase metadata (title/summary/storage/batch ids) for UI display. Extend supabase table `tepo_files` with fields (title, summary, storage_url) to power richer doc panels.
