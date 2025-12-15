import os
from typing import Any

from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None


def supabase_search(ctx: Any, table: str, query: str):
    if supabase is None:
        return {"error": "Supabase client not configured."}
    result = supabase.table(table).select("*").ilike("content", f"%{query}%").execute()
    return result.data


def supabase_insert(ctx: Any, table: str, record: dict):
    if supabase is None:
        return {"error": "Supabase client not configured."}
    result = supabase.table(table).insert(record).execute()
    return result.data
