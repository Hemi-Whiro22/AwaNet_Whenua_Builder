"""
Kitenga Schema Database Connector
Connects Kitenga Whiro to the kitenga schema tables in Supabase PostgreSQL.
"""
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SCHEMA = "kitenga"


@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager  
def get_cursor(conn=None):
    """Context manager for database cursors with RealDictCursor."""
    if conn:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            yield cur
        finally:
            cur.close()
    else:
        with get_connection() as conn:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            try:
                yield cur
                conn.commit()
            finally:
                cur.close()


# ==================== LOGS ====================

def log_event(event: str, detail: str, source: str = "kitenga_whiro", data: dict = None) -> str:
    """Insert a log entry into kitenga.logs."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(f"""
                INSERT INTO {SCHEMA}.logs (event, detail, source, data)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (event, detail, source, data or {}))
            result = cur.fetchone()
            conn.commit()
            return str(result['id'])


def get_recent_logs(limit: int = 50, source: str = None) -> List[Dict]:
    """Get recent log entries."""
    with get_cursor() as cur:
        if source:
            cur.execute(f"""
                SELECT * FROM {SCHEMA}.logs 
                WHERE source = %s
                ORDER BY created_at DESC LIMIT %s
            """, (source, limit))
        else:
            cur.execute(f"""
                SELECT * FROM {SCHEMA}.logs 
                ORDER BY created_at DESC LIMIT %s
            """, (limit,))
        return cur.fetchall()


# ==================== MEMORY ====================

def store_memory(content: str, metadata: dict = None) -> str:
    """Store context memory."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(f"""
                INSERT INTO {SCHEMA}.context_memory (content, metadata)
                VALUES (%s, %s)
                RETURNING id
            """, (content, metadata or {}))
            result = cur.fetchone()
            conn.commit()
            return str(result['id'])


def search_memory(query: str, limit: int = 10) -> List[Dict]:
    """Search context memory by text (basic ILIKE search)."""
    with get_cursor() as cur:
        cur.execute(f"""
            SELECT * FROM {SCHEMA}.context_memory 
            WHERE content ILIKE %s
            ORDER BY created_at DESC LIMIT %s
        """, (f'%{query}%', limit))
        return cur.fetchall()


def log_memory_event(source: str, ref_id: str, event_type: str, summary: str, details: dict = None) -> str:
    """Log to memory_log table."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(f"""
                INSERT INTO {SCHEMA}.memory_log (source, ref_id, event_type, summary, details)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (source, ref_id, event_type, summary, details or {}))
            result = cur.fetchone()
            conn.commit()
            return str(result['id'])


# ==================== CHAT ====================

def save_chat_log(session_id: str, user_message: str, assistant_reply: str, 
                  thread_id: str = None, mode: str = "chat", metadata: dict = None) -> str:
    """Save a chat log entry."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(f"""
                INSERT INTO {SCHEMA}.chat_logs 
                (session_id, thread_id, user_message, assistant_reply, mode, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (session_id, thread_id, user_message, assistant_reply, mode, metadata or {}))
            result = cur.fetchone()
            conn.commit()
            return str(result['id'])


def get_chat_history(session_id: str, limit: int = 50) -> List[Dict]:
    """Get chat history for a session."""
    with get_cursor() as cur:
        cur.execute(f"""
            SELECT * FROM {SCHEMA}.chat_logs 
            WHERE session_id = %s
            ORDER BY created_at DESC LIMIT %s
        """, (session_id, limit))
        return cur.fetchall()


# ==================== TAONGA ====================

def store_taonga(title: str, content: str, metadata: dict = None) -> str:
    """Store a taonga (treasure/artifact)."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(f"""
                INSERT INTO {SCHEMA}.taonga (title, content, metadata)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (title, content, metadata or {}))
            result = cur.fetchone()
            conn.commit()
            return str(result['id'])


def search_taonga(query: str, limit: int = 10) -> List[Dict]:
    """Search taonga by title or content."""
    with get_cursor() as cur:
        cur.execute(f"""
            SELECT * FROM {SCHEMA}.taonga 
            WHERE title ILIKE %s OR content ILIKE %s
            ORDER BY created_at DESC LIMIT %s
        """, (f'%{query}%', f'%{query}%', limit))
        return cur.fetchall()


def get_taonga_by_id(taonga_id: str) -> Optional[Dict]:
    """Get a specific taonga by ID."""
    with get_cursor() as cur:
        cur.execute(f"""
            SELECT * FROM {SCHEMA}.taonga WHERE id = %s
        """, (taonga_id,))
        return cur.fetchone()


# ==================== OCR ====================

def save_ocr_log(file_name: str, text_extracted: str, metadata: dict = None) -> str:
    """Save OCR extraction log."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(f"""
                INSERT INTO {SCHEMA}.ocr_logs (file_name, text_extracted, metadata)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (file_name, text_extracted, metadata or {}))
            result = cur.fetchone()
            conn.commit()
            return str(result['id'])


# ==================== PIPELINE ====================

def create_pipeline_run(source: str, status: str = "pending", metadata: dict = None) -> str:
    """Create a new pipeline run record."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(f"""
                INSERT INTO {SCHEMA}.pipeline_runs (source, status, metadata)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (source, status, metadata or {}))
            result = cur.fetchone()
            conn.commit()
            return str(result['id'])


def update_pipeline_run(run_id: str, status: str, **kwargs) -> bool:
    """Update a pipeline run record."""
    updates = ["status = %s"]
    values = [status]
    
    for key in ['raw_path', 'clean_path', 'chunk_ids', 'vector_batch_id', 'metadata']:
        if key in kwargs:
            updates.append(f"{key} = %s")
            values.append(kwargs[key])
    
    values.append(run_id)
    
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(f"""
                UPDATE {SCHEMA}.pipeline_runs 
                SET {', '.join(updates)}
                WHERE id = %s
            """, values)
            conn.commit()
            return cur.rowcount > 0


def get_recent_pipeline_runs(limit: int = 20) -> List[Dict]:
    """Get recent pipeline runs."""
    with get_cursor() as cur:
        cur.execute(f"""
            SELECT * FROM {SCHEMA}.pipeline_runs 
            ORDER BY created_at DESC LIMIT %s
        """, (limit,))
        return cur.fetchall()


# ==================== ARTIFACTS ====================

def store_artifact(file_name: str, file_type: str, storage_path: str,
                   summary: str = None, full_text: str = None, 
                   kaupapa_tags: list = None, metadata: dict = None) -> str:
    """Store an artifact in the kitenga schema."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(f"""
                INSERT INTO {SCHEMA}.artifacts 
                (file_name, file_type, storage_path, summary, full_text, kaupapa_tags)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (file_name, file_type, storage_path, summary, full_text, kaupapa_tags or []))
            result = cur.fetchone()
            conn.commit()
            return str(result['id'])


# ==================== WHAKAPAPA (LINEAGE) ====================

def log_whakapapa(id: str, title: str, category: str, summary: str, 
                  content_type: str = "event", data: dict = None, author: str = "kitenga_whiro") -> str:
    """Log to whakapapa_logs - the lineage/history table."""
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(f"""
                INSERT INTO {SCHEMA}.whakapapa_logs (id, title, category, author, summary, content_type, data)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    summary = EXCLUDED.summary,
                    data = EXCLUDED.data,
                    updated_at = NOW()
                RETURNING id
            """, (id, title, category, author, summary, content_type, data or {}))
            result = cur.fetchone()
            conn.commit()
            return str(result['id'])


# ==================== STATS ====================

def get_schema_stats() -> Dict[str, Any]:
    """Get statistics about the kitenga schema."""
    with get_cursor() as cur:
        stats = {}
        
        tables = [
            'logs', 'context_memory', 'memory_log', 'chat_logs', 
            'taonga', 'ocr_logs', 'pipeline_runs', 'artifacts', 'whakapapa_logs'
        ]
        
        for table in tables:
            try:
                cur.execute(f"SELECT COUNT(*) as count FROM {SCHEMA}.{table}")
                result = cur.fetchone()
                stats[table] = result['count'] if result else 0
            except:
                stats[table] = -1
        
        return {
            "schema": SCHEMA,
            "table_counts": stats,
            "total_records": sum(v for v in stats.values() if v > 0),
            "checked_at": datetime.utcnow().isoformat()
        }


# ==================== TEST CONNECTION ====================

def test_connection() -> Dict[str, Any]:
    """Test database connection and return schema info."""
    try:
        with get_cursor() as cur:
            cur.execute(f"""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema = %s
                ORDER BY table_name
            """, (SCHEMA,))
            tables = [row['table_name'] for row in cur.fetchall()]
            
        return {
            "connected": True,
            "schema": SCHEMA,
            "tables": tables,
            "table_count": len(tables)
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e)
        }


if __name__ == "__main__":
    # Quick test
    print("🐺 Testing Kitenga Schema Connection...")
    result = test_connection()
    print(f"Connected: {result['connected']}")
    if result['connected']:
        print(f"Schema: {result['schema']}")
        print(f"Tables: {result['table_count']}")
        print("\nStats:")
        stats = get_schema_stats()
        for table, count in stats['table_counts'].items():
            print(f"  {table}: {count} rows")
