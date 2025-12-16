-- Realm-scoped research + translation tables
-- Enables per-realm storage of sessions, notes, embeddings, and pronunciation caches.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS research_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    realm_id TEXT NOT NULL,
    thread_id TEXT,
    title TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    realm_id TEXT NOT NULL,
    session_id UUID REFERENCES research_sessions(id) ON DELETE CASCADE,
    author TEXT,
    content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    realm_id TEXT NOT NULL,
    source_id TEXT,
    content TEXT NOT NULL,
    token_count INT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS research_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    realm_id TEXT NOT NULL,
    chunk_id UUID REFERENCES research_chunks(id) ON DELETE CASCADE,
    source_id TEXT,
    embedding vector(1536) NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS translation_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    realm_id TEXT NOT NULL,
    source_text TEXT NOT NULL,
    translated_text TEXT NOT NULL,
    dialect TEXT,
    confidence NUMERIC,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS pronunciation_cache (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    realm_id TEXT NOT NULL,
    phrase TEXT NOT NULL,
    phonetic TEXT,
    audio_url TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_research_sessions_realm ON research_sessions(realm_id);
CREATE INDEX IF NOT EXISTS idx_research_notes_realm ON research_notes(realm_id);
CREATE INDEX IF NOT EXISTS idx_research_chunks_realm ON research_chunks(realm_id);
CREATE INDEX IF NOT EXISTS idx_research_embeddings_realm ON research_embeddings(realm_id);
CREATE INDEX IF NOT EXISTS idx_translation_logs_realm ON translation_logs(realm_id);
CREATE INDEX IF NOT EXISTS idx_pronunciation_cache_realm ON pronunciation_cache(realm_id);
CREATE INDEX IF NOT EXISTS idx_research_embeddings_chunk ON research_embeddings(chunk_id);

-- RPC for recall service: pgvector similarity search scoped by realm.
CREATE OR REPLACE FUNCTION match_research_embeddings(
    query_embedding vector,
    match_count integer,
    filter_realm_id text
)
RETURNS TABLE (
    chunk_id UUID,
    source_id TEXT,
    content TEXT,
    similarity FLOAT,
    metadata JSONB
)
LANGUAGE sql STABLE PARALLEL SAFE
AS $$
    SELECT
        e.chunk_id,
        e.source_id,
        c.content,
        1 - (e.embedding <=> query_embedding) AS similarity,
        COALESCE(e.metadata, '{}'::jsonb) AS metadata
    FROM research_embeddings e
    JOIN research_chunks c ON c.id = e.chunk_id
    WHERE e.realm_id = filter_realm_id
    ORDER BY e.embedding <=> query_embedding
    LIMIT GREATEST(1, match_count);
$$;

GRANT EXECUTE ON FUNCTION match_research_embeddings(vector, integer, text) TO authenticated, service_role, anon;
