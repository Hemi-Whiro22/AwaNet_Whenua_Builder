"""
Te Hau Supabase Client

Vector storage and database operations using Supabase.
"""

import os
import json
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime


def get_supabase_client():
    """Get Supabase client, loading credentials from environment."""
    try:
        from supabase import create_client, Client
    except ImportError:
        raise ImportError("supabase package required. Install with: pip install supabase")
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    
    if not url or not key:
        # Try loading from .env
        env_file = Path.home() / ".awanet" / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("SUPABASE_URL=") and not url:
                    url = line.split("=", 1)[1].strip().strip('"\'')
                elif line.startswith("SUPABASE_SERVICE_KEY=") and not key:
                    key = line.split("=", 1)[1].strip().strip('"\'')
                elif line.startswith("SUPABASE_ANON_KEY=") and not key:
                    key = line.split("=", 1)[1].strip().strip('"\'')
    
    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_ANON_KEY not found. "
            "Set them in environment or ~/.awanet/.env"
        )
    
    return create_client(url, key)


def store_embedding(
    namespace: str,
    content: str,
    embedding: List[float],
    metadata: Optional[Dict] = None
) -> str:
    """
    Store an embedding in the vector database.
    
    Args:
        namespace: Vector namespace (e.g., realm::my_realm)
        content: Original text content
        embedding: Embedding vector
        metadata: Additional metadata
        
    Returns:
        Document ID
    """
    client = get_supabase_client()
    
    doc_id = f"doc_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hash(content) % 10000:04d}"
    
    data = {
        "id": doc_id,
        "namespace": namespace,
        "content": content,
        "embedding": embedding,
        "metadata": json.dumps(metadata or {}),
        "created_at": datetime.utcnow().isoformat()
    }
    
    client.table("realm_memories").insert(data).execute()
    
    return doc_id


def store_embeddings(
    namespace: str,
    items: List[Dict[str, Any]]
) -> List[str]:
    """
    Store multiple embeddings in batch.
    
    Args:
        namespace: Vector namespace
        items: List of {content, embedding, metadata} dicts
        
    Returns:
        List of document IDs
    """
    client = get_supabase_client()
    
    doc_ids = []
    rows = []
    
    for i, item in enumerate(items):
        doc_id = f"doc_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{i:04d}"
        doc_ids.append(doc_id)
        
        rows.append({
            "id": doc_id,
            "namespace": namespace,
            "content": item["content"],
            "embedding": item["embedding"],
            "metadata": json.dumps(item.get("metadata", {})),
            "created_at": datetime.utcnow().isoformat()
        })
    
    client.table("realm_memories").insert(rows).execute()
    
    return doc_ids


def search_vectors(
    query_embedding: List[float],
    namespace: str,
    top_k: int = 5,
    threshold: float = 0.7
) -> List[Dict]:
    """
    Search for similar vectors using pgvector.
    
    Args:
        query_embedding: Query vector
        namespace: Vector namespace to search
        top_k: Number of results
        threshold: Minimum similarity threshold
        
    Returns:
        List of matching documents with scores
    """
    client = get_supabase_client()
    
    # Use Supabase's RPC for vector similarity search
    response = client.rpc(
        "match_memories",
        {
            "query_embedding": query_embedding,
            "match_namespace": namespace,
            "match_count": top_k,
            "match_threshold": threshold
        }
    ).execute()
    
    return response.data


def delete_by_namespace(namespace: str) -> int:
    """
    Delete all documents in a namespace.
    
    Args:
        namespace: Vector namespace
        
    Returns:
        Number of deleted documents
    """
    client = get_supabase_client()
    
    response = client.table("realm_memories").delete().eq("namespace", namespace).execute()
    
    return len(response.data) if response.data else 0


def get_realm_stats(namespace: str) -> Dict:
    """
    Get statistics for a realm's vector store.
    
    Args:
        namespace: Vector namespace
        
    Returns:
        Statistics dict
    """
    client = get_supabase_client()
    
    response = client.table("realm_memories").select("id", count="exact").eq("namespace", namespace).execute()
    
    return {
        "namespace": namespace,
        "document_count": response.count or 0
    }


# SQL for creating the required Supabase tables
SUPABASE_SCHEMA = """
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Realm memories table (vector store)
CREATE TABLE IF NOT EXISTS realm_memories (
    id TEXT PRIMARY KEY,
    namespace TEXT NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for namespace queries
CREATE INDEX IF NOT EXISTS idx_realm_memories_namespace 
ON realm_memories(namespace);

-- Vector similarity search index
CREATE INDEX IF NOT EXISTS idx_realm_memories_embedding 
ON realm_memories USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Function for vector similarity search
CREATE OR REPLACE FUNCTION match_memories(
    query_embedding vector(1536),
    match_namespace TEXT,
    match_count INT DEFAULT 5,
    match_threshold FLOAT DEFAULT 0.7
)
RETURNS TABLE (
    id TEXT,
    namespace TEXT,
    content TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        rm.id,
        rm.namespace,
        rm.content,
        rm.metadata,
        1 - (rm.embedding <=> query_embedding) AS similarity
    FROM realm_memories rm
    WHERE rm.namespace = match_namespace
      AND 1 - (rm.embedding <=> query_embedding) > match_threshold
    ORDER BY rm.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Row Level Security
ALTER TABLE realm_memories ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their realm's memories
CREATE POLICY "Realm isolation" ON realm_memories
    FOR ALL
    USING (
        namespace = 'global::awanet' 
        OR namespace LIKE 'realm::' || current_setting('request.jwt.claims', true)::json->>'realm_id'
    );

-- Realms table
CREATE TABLE IF NOT EXISTS realms (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    bearer_hash TEXT NOT NULL,
    kaitiaki TEXT,
    glyph_color TEXT,
    parent_realm TEXT REFERENCES realms(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    sealed_at TIMESTAMPTZ,
    seal_hash TEXT,
    config JSONB DEFAULT '{}'
);

-- Kaitiaki table
CREATE TABLE IF NOT EXISTS kaitiaki (
    id TEXT PRIMARY KEY,
    realm_id TEXT REFERENCES realms(id),
    name TEXT NOT NULL,
    stage TEXT DEFAULT 'pēpi',
    model TEXT DEFAULT 'gpt-4o',
    system_prompt TEXT,
    tools TEXT[] DEFAULT '{}',
    evolution_history JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Pipeline runs table
CREATE TABLE IF NOT EXISTS pipeline_runs (
    id TEXT PRIMARY KEY,
    realm_id TEXT REFERENCES realms(id),
    pipeline_name TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    input_ref TEXT,
    output_ref TEXT,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error TEXT
);
"""
