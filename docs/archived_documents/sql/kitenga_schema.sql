-- Kitenga + Kaitiaki schema (trimmed, runnable). Apply in Supabase SQL editor.
-- Focus: files/artifacts, chat, memory, taonga, OCR, summaries, and carver context.

create extension if not exists "pgcrypto";

-- Artifacts / files (raw + clean + summary) (public-prefixed for PostgREST exposure)
create table if not exists public.kitenga_artifacts (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  file_name text,
  file_type text,
  file_size_bytes bigint,
  file_hash text,
  storage_path text,
  storage_url text,
  source text,
  summary_short text,
  summary_long text,
  full_text text,
  metadata jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- OCR runs (image -> text)
create table if not exists public.kitenga_ocr_logs (
  id uuid primary key default gen_random_uuid(),
  file_name text,
  text_extracted text,
  metadata jsonb,
  created_at timestamptz not null default now()
);

-- PDF summaries (optional, if you want a dedicated table)
create table if not exists public.kitenga_pdf_summaries (
  id uuid primary key default gen_random_uuid(),
  file_name text,
  summary text,
  chunks jsonb,
  embedding jsonb,
  metadata jsonb,
  created_at timestamptz not null default now()
);

-- Taonga pipeline
create table if not exists kitenga.taonga_uploads (
  id uuid primary key default gen_random_uuid(),
  file_name text,
  file_url text unique,
  uploaded_at timestamptz default now(),
  source text,
  title text,
  author text,
  published_at timestamptz,
  content text,
  summary text,
  embedding jsonb,
  metadata jsonb
);
create table if not exists kitenga.taonga_summaries (
  id uuid primary key default gen_random_uuid(),
  upload_id uuid references kitenga.taonga_uploads(id),
  summary text not null,
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);
create table if not exists kitenga.taonga_embeddings (
  id uuid primary key default gen_random_uuid(),
  summary_id uuid references kitenga.taonga_summaries(id),
  content text not null,
  embedding jsonb not null,
  metadata jsonb,
  created_at timestamptz default now()
);

-- Chat + messages
create table if not exists kitenga.chats (
  id uuid primary key default gen_random_uuid(),
  user_id uuid,
  title text,
  kaitiaki_name text default 'Kaitiaki',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
create table if not exists kitenga.messages (
  id uuid primary key default gen_random_uuid(),
  chat_id uuid references kitenga.chats(id),
  role text not null check (role in ('user','assistant','system')),
  content text not null,
  referenced_artifacts uuid[],
  metadata jsonb default '{}'::jsonb,
  created_at timestamptz default now()
);

-- Context / memory
create table if not exists kitenga.context_memory (
  id uuid primary key default gen_random_uuid(),
  content text,
  metadata jsonb,
  created_at timestamptz default now()
);
create table if not exists kitenga.kitenga_index (
  id uuid primary key default gen_random_uuid(),
  source text,
  source_id text,
  text text,
  embedding jsonb,
  created_at timestamptz default now()
);

-- Whakapapa / logs (pick one main log table)
create table if not exists kitenga.whakapapa_logs (
  id text primary key,
  title text not null,
  category text default 'whakapapa',
  author text default 'Kitenga',
  summary text,
  content_type text default 'text',
  data jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Memory log (generic events)
create table if not exists kitenga.memory_log (
  id uuid primary key default gen_random_uuid(),
  source text,
  ref_id uuid,
  event_type text,
  summary text,
  details jsonb,
  created_at timestamptz default now()
);
create table if not exists kitenga.memory_index (
  id uuid primary key default gen_random_uuid(),
  log_id uuid references kitenga.memory_log(id),
  content text,
  embedding jsonb,
  created_at timestamptz default now()
);

-- Audit (optional)
create table if not exists kitenga.validators_audit (
  id uuid primary key default gen_random_uuid(),
  ts timestamptz default now(),
  route text not null,
  method text not null,
  status_code integer not null,
  user_id text,
  request_id text,
  ip text,
  agent text,
  action text,
  payload_hash text,
  redacted boolean default true,
  cultural_flags jsonb,
  latency_ms integer,
  metadata jsonb
);

-- Carver memory (from Rongohia, for Codex/Kaitiaki persona)
create table if not exists kitenga.carver_memory (
  user_id uuid primary key,
  interests text[],
  verification_style text,
  trust_level integer,
  language_preference text,
  last_updated timestamptz
);

-- Logs / runs / chat / vector batches (public-prefixed for PostgREST)
create table if not exists public.kitenga_logs (
  id uuid primary key default gen_random_uuid(),
  event text,
  detail text,
  source text,
  data jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.kitenga_pipeline_runs (
  id uuid primary key default gen_random_uuid(),
  source text,
  status text,
  raw_path text,
  clean_path text,
  chunk_ids jsonb,
  vector_batch_id text,
  metadata jsonb,
  created_at timestamptz not null default now()
);

create table if not exists public.kitenga_vector_batches (
  batch_id text primary key,
  vector_store_id text,
  status text,
  file_counts jsonb,
  metadata jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.kitenga_chat_logs (
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
