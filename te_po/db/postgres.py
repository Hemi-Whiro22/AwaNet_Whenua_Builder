"""PostgreSQL connection pooling for te_po.

Provides psycopg3 ConnectionPool with safe parameter binding.
Works in both FastAPI (sync context) and RQ worker (sync context) processes.
"""

import os
from typing import Optional, Any, List, Dict, Tuple
from contextlib import contextmanager

try:
    from psycopg_pool import ConnectionPool
except ImportError:
    ConnectionPool = None

# Global pool instance
_pool: Optional[ConnectionPool] = None


def _build_pool() -> Optional[ConnectionPool]:
    """Create a psycopg3 ConnectionPool from DATABASE_URL.
    
    Supports:
    - postgresql://user:pass@host:port/db
    - postgresql://...?sslmode=require (for Supabase, Railway, etc.)
    
    Falls back gracefully if DATABASE_URL missing or psycopg_pool unavailable.
    """
    if ConnectionPool is None:
        return None
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return None
    
    try:
        # Add SSL for PostgreSQL URLs if sslmode not specified
        if "sslmode=" not in db_url and db_url.startswith("postgresql"):
            db_url = f"{db_url}?sslmode=require"
        
        pool = ConnectionPool(
            db_url,
            min_size=2,
            max_size=10,
            timeout=5,
        )
        return pool
    except Exception as e:
        import warnings
        warnings.warn(f"Failed to initialize PostgreSQL pool: {e}", RuntimeWarning)
        return None


def get_pool() -> Optional[ConnectionPool]:
    """Get the global ConnectionPool (lazy-initialized)."""
    global _pool
    if _pool is None:
        _pool = _build_pool()
    return _pool


@contextmanager
def get_connection():
    """Context manager for getting a connection from the pool."""
    pool = get_pool()
    if pool is None:
        raise RuntimeError("PostgreSQL pool not initialized (DATABASE_URL not set)")
    
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def db_execute(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> int:
    """Execute a query (INSERT/UPDATE/DELETE) and return rows affected.
    
    Example:
        db_execute(
            "INSERT INTO pipeline_jobs (id, status) VALUES (%s, %s)",
            (job_id, "queued")
        )
    """
    pool = get_pool()
    if pool is None:
        raise RuntimeError("PostgreSQL pool not initialized (DATABASE_URL not set)")
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            conn.commit()
            return cur.rowcount


def db_fetchone(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> Optional[Dict[str, Any]]:
    """Execute a query and return first row as dict, or None.
    
    Example:
        job = db_fetchone(
            "SELECT * FROM pipeline_jobs WHERE id = %s",
            (job_id,)
        )
    """
    pool = get_pool()
    if pool is None:
        return None
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                row = cur.fetchone()
                if row is None:
                    return None
                # Convert Row to dict
                return dict(zip([desc[0] for desc in cur.description], row))
    except Exception:
        return None


def db_fetchall(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> List[Dict[str, Any]]:
    """Execute a query and return all rows as list of dicts.
    
    Example:
        jobs = db_fetchall(
            "SELECT * FROM pipeline_jobs WHERE realm = %s ORDER BY created_at DESC LIMIT %s",
            (realm, 50)
        )
    """
    pool = get_pool()
    if pool is None:
        return []
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                rows = cur.fetchall()
                if not rows:
                    return []
                # Convert Rows to dicts
                col_names = [desc[0] for desc in cur.description]
                return [dict(zip(col_names, row)) for row in rows]
    except Exception:
        return []


def db_query(
    query: str,
    params: Optional[Tuple[Any, ...]] = None,
) -> Any:
    """Execute any query and return raw result (for advanced use).
    
    Useful for stored procedures or custom queries.
    """
    pool = get_pool()
    if pool is None:
        return None
    
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or ())
                conn.commit()
                return cur.fetchall()
    except Exception as e:
        raise RuntimeError(f"Query execution failed: {e}")
