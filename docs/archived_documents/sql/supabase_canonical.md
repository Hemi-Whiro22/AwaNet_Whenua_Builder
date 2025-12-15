# Supabase Canonical Schema (Kitenga/AwaNet)

Use this as the single source of truth to avoid creating more tables/buckets.

## Keep (canonical)
- Tables
  - `kitenga_chat_logs` — chat turns from UI/API
  - `kitenga_pipeline_runs` — pipeline/job results per ingest
  - `kitenga_vector_batches` — OpenAI vector batch tracking
  - `kitenga_artifacts` — file/doc metadata (paths, summaries, vector ids)
  - `kitenga_logs` — general audit/events
  - `card_scans`, `card_context_index`, `cards_for_sale` — card workflow (if still used)
  - `pipeline_jobs` — queued pipeline jobs (if pipeline routes enabled)
  - `tepo_logs` — generic UI/research logs (optional; can be merged into kitenga_logs later)
- Buckets
  - `tepo_storage` — raw/clean/chunk uploads
  - `ocr_cards` — card images/processed JSON (if cards in use)
  - `mauri_state` — only if mauri sync is active; otherwise mark legacy

## Prefer these readers
- Chat history: read `kitenga_chat_logs` (ordered by `created_at`)
- Docs/profiles/status: read `kitenga_artifacts`

## Candidates to deprecate/drop (review before running)
- Tables that were read-only or unused in current code:
  - `tepo_chat_logs` (now superseded by kitenga_chat_logs)
  - `tepo_files` (now superseded by kitenga_artifacts)
  - Legacy context/memory tables you’re no longer using (see drop_candidates list)

## Drop script template (commented for safety)
-- Uncomment only after backup/verification.
-- drop table if exists public.tepo_chat_logs;
-- drop table if exists public.tepo_files;

## Checklist before cleanup
1) Backup the DB (`pg_dump` or Supabase export).
2) Confirm no UI/route reads/writes to the tables you drop.
3) Run commented drops in a psql session once verified.

## Notes
- Keep future additions inside the `kitenga_*` namespace to avoid table sprawl.
- If you stop using card features or mauri_state, archive the bucket/table references and then drop after backup.
