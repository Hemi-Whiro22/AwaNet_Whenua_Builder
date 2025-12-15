-- Row Level Security policies for Te Pō tables (enable + minimal service_role policy).
-- Run in Supabase SQL editor. Adjust/grant additional policies for auth/anon as needed.

-- Canonical pipeline + logging tables
alter table if exists public.tepo_files enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_files_service_role_full') then
    create policy tepo_files_service_role_full on public.tepo_files
      for all to service_role using (true) with check (true);
  end if;
end$$;

alter table if exists public.tepo_pipeline_runs enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_pipeline_runs_service_role_full') then
    create policy tepo_pipeline_runs_service_role_full on public.tepo_pipeline_runs
      for all to service_role using (true) with check (true);
  end if;
end$$;

alter table if exists public.tepo_chunks enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_chunks_service_role_full') then
    create policy tepo_chunks_service_role_full on public.tepo_chunks
      for all to service_role using (true) with check (true);
  end if;
end$$;

alter table if exists public.tepo_vector_batches enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_vector_batches_service_role_full') then
    create policy tepo_vector_batches_service_role_full on public.tepo_vector_batches
      for all to service_role using (true) with check (true);
  end if;
end$$;

alter table if exists public.tepo_logs enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_logs_service_role_full') then
    create policy tepo_logs_service_role_full on public.tepo_logs
      for all to service_role using (true) with check (true);
  end if;
end$$;

alter table if exists public.tepo_chat_logs enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_chat_logs_service_role_full') then
    create policy tepo_chat_logs_service_role_full on public.tepo_chat_logs
      for all to service_role using (true) with check (true);
  end if;
end$$;

alter table if exists public.mauri_snapshots enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'mauri_snapshots_service_role_full') then
    create policy mauri_snapshots_service_role_full on public.mauri_snapshots
      for all to service_role using (true) with check (true);
  end if;
end$$;

-- Legacy/domain tables we are keeping (read/write via service role)
alter table if exists public.ari_whakapapa enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'ari_whakapapa_service_role_full') then
    create policy ari_whakapapa_service_role_full on public.ari_whakapapa
      for all to service_role using (true) with check (true);
  end if;
end$$;

alter table if exists public.carver_context_memory enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'carver_context_memory_service_role_full') then
    create policy carver_context_memory_service_role_full on public.carver_context_memory
      for all to service_role using (true) with check (true);
  end if;
end$$;

alter table if exists public.kitenga_taonga enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'kitenga_taonga_service_role_full') then
    create policy kitenga_taonga_service_role_full on public.kitenga_taonga
      for all to service_role using (true) with check (true);
  end if;
end$$;

alter table if exists public.mataroa_audit_log enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'mataroa_audit_log_service_role_full') then
    create policy mataroa_audit_log_service_role_full on public.mataroa_audit_log
      for all to service_role using (true) with check (true);
  end if;
end$$;

alter table if exists public.rongohia_audit_logs enable row level security;
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'rongohia_audit_logs_service_role_full') then
    create policy rongohia_audit_logs_service_role_full on public.rongohia_audit_logs
      for all to service_role using (true) with check (true);
  end if;
end$$;

-- Storage schema objects typically require storage-specific policies; for now we rely on Supabase defaults.

-- ===========================
-- Taonga protection (mode='taonga')
-- Deny anon/auth for taonga rows; allow service_role full access.
-- Apply only if tables have a 'mode' column.
-- ===========================

-- tepo_files taonga guard
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_files_taonga_block_anon') then
    create policy tepo_files_taonga_block_anon on public.tepo_files
      for select to anon using (mode is null or mode <> 'taonga');
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_files_taonga_block_auth') then
    create policy tepo_files_taonga_block_auth on public.tepo_files
      for select to authenticated using (mode is null or mode <> 'taonga');
  end if;
end$$;

-- tepo_pipeline_runs taonga guard
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_pipeline_runs_taonga_block_anon') then
    create policy tepo_pipeline_runs_taonga_block_anon on public.tepo_pipeline_runs
      for select to anon using (mode is null or mode <> 'taonga');
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_pipeline_runs_taonga_block_auth') then
    create policy tepo_pipeline_runs_taonga_block_auth on public.tepo_pipeline_runs
      for select to authenticated using (mode is null or mode <> 'taonga');
  end if;
end$$;

-- tepo_chunks taonga guard
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_chunks_taonga_block_anon') then
    create policy tepo_chunks_taonga_block_anon on public.tepo_chunks
      for select to anon using (metadata ->> 'mode' is null or metadata ->> 'mode' <> 'taonga');
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_chunks_taonga_block_auth') then
    create policy tepo_chunks_taonga_block_auth on public.tepo_chunks
      for select to authenticated using (metadata ->> 'mode' is null or metadata ->> 'mode' <> 'taonga');
  end if;
end$$;

-- tepo_logs taonga guard
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_logs_taonga_block_anon') then
    create policy tepo_logs_taonga_block_anon on public.tepo_logs
      for select to anon using (data ->> 'mode' is null or data ->> 'mode' <> 'taonga');
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_logs_taonga_block_auth') then
    create policy tepo_logs_taonga_block_auth on public.tepo_logs
      for select to authenticated using (data ->> 'mode' is null or data ->> 'mode' <> 'taonga');
  end if;
end$$;

-- tepo_chat_logs taonga guard
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_chat_logs_taonga_block_anon') then
    create policy tepo_chat_logs_taonga_block_anon on public.tepo_chat_logs
      for select to anon using (metadata ->> 'data_mode' is null or metadata ->> 'data_mode' <> 'taonga');
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_chat_logs_taonga_block_auth') then
    create policy tepo_chat_logs_taonga_block_auth on public.tepo_chat_logs
      for select to authenticated using (metadata ->> 'data_mode' is null or metadata ->> 'data_mode' <> 'taonga');
  end if;
end$$;

-- tepo_vector_batches taonga guard
do $$
begin
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_vector_batches_taonga_block_anon') then
    create policy tepo_vector_batches_taonga_block_anon on public.tepo_vector_batches
      for select to anon using (metadata ->> 'mode' is null or metadata ->> 'mode' <> 'taonga');
  end if;
  if not exists (select 1 from pg_policies where schemaname = 'public' and policyname = 'tepo_vector_batches_taonga_block_auth') then
    create policy tepo_vector_batches_taonga_block_auth on public.tepo_vector_batches
      for select to authenticated using (metadata ->> 'mode' is null or metadata ->> 'mode' <> 'taonga');
  end if;
end$$;
