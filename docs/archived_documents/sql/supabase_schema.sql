-- Supabase schema for Te Pō mirrors (storage, pipeline, Mauri, chat/logs)
-- Run once in Supabase SQL editor or psql.

-- Extensions
create extension if not exists "pgcrypto";

-- Files stored/seen by the pipeline (mirror of te_po/storage and Supabase bucket)
create table if not exists public.tepo_files (
  id uuid primary key default gen_random_uuid(),
  source text,
  filename text,
  storage_path text,
  storage_bucket text,
  storage_url text,
  content_type text,
  sha256 text,
  size bigint,
  raw_path text,
  clean_path text,
  chunk_ids jsonb,
  vector_batch_id text,
  summary_short text,
  summary_long text,
  metadata jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create index if not exists idx_tepo_files_source on public.tepo_files(source);
create index if not exists idx_tepo_files_vector_batch on public.tepo_files(vector_batch_id);
create index if not exists idx_tepo_files_created_at on public.tepo_files(created_at desc);

-- Pipeline run mirror (one row per pipeline execution)
create table if not exists public.tepo_pipeline_runs (
  id uuid primary key default gen_random_uuid(),
  source text,
  status text,
  glyph text,
  raw_file text,
  clean_file text,
  chunk_ids jsonb,
  vector_batch_id text,
  storage jsonb,
  supabase_status jsonb,
  metadata jsonb,
  created_at timestamptz not null default now()
);
create index if not exists idx_tepo_pipeline_runs_source on public.tepo_pipeline_runs(source);
create index if not exists idx_tepo_pipeline_runs_created_at on public.tepo_pipeline_runs(created_at desc);

-- Chunk mirror (optional storage of chunk text/metadata)
create table if not exists public.tepo_chunks (
  chunk_id text primary key,
  text_content text,
  embedding jsonb,
  vector_store_id text,
  metadata jsonb,
  created_at timestamptz not null default now()
);
create index if not exists idx_tepo_chunks_vector_store on public.tepo_chunks(vector_store_id);

-- Vector batch status mirror (for OpenAI vector store batches)
create table if not exists public.tepo_vector_batches (
  batch_id text primary key,
  vector_store_id text,
  status text,
  file_counts jsonb,
  metadata jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- Mauri/state snapshots mirror
create table if not exists public.mauri_snapshots (
  id uuid primary key default gen_random_uuid(),
  snapshot_ts timestamptz,
  files jsonb,
  count int,
  metadata jsonb,
  created_at timestamptz not null default now()
);

-- Carver context memory (for Codex/assistant recall)
create table if not exists public.carver_context_memory (
  id uuid primary key default gen_random_uuid(),
  session_id text,
  title text,
  content jsonb,
  tags text[],
  created_at timestamptz not null default now()
);

-- Audit/log events (mirror of project/ledger logs)
create table if not exists public.tepo_logs (
  id uuid primary key default gen_random_uuid(),
  event text,
  detail text,
  source text,
  data jsonb,
  created_at timestamptz not null default now()
);
create index if not exists idx_tepo_logs_created_at on public.tepo_logs(created_at desc);
create index if not exists idx_tepo_logs_event on public.tepo_logs(event);

-- Chat/whisper transcripts (optional, for UI sessions)
create table if not exists public.tepo_chat_logs (
  id uuid primary key default gen_random_uuid(),
  session_id text,
  thread_id text,
  user_message text,
  assistant_reply text,
  mode text,
  vector_batch_id text,
  pipeline_result jsonb,
  metadata jsonb,
  created_at timestamptz not null default now()
);
create index if not exists idx_tepo_chat_logs_session on public.tepo_chat_logs(session_id);
create index if not exists idx_tepo_chat_logs_created_at on public.tepo_chat_logs(created_at desc);

-- Optional: keep storage path unique to avoid duplicates
create unique index if not exists uq_tepo_files_storage_path on public.tepo_files(storage_path);
