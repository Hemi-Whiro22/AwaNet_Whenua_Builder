import os
from supabase import create_client

def validate_supabase_connection():
    """Validate Supabase state storage and retrieval."""
    url = os.getenv("SUPABASE_URL")
    anon_key = os.getenv("SUPABASE_ANON_KEY")

    if not url or not anon_key:
        raise ValueError("Supabase URL or ANON KEY is missing from environment variables.")

    supabase = create_client(url, anon_key)

    # Test: Insert and retrieve a sample record
    data = {"test_key": "test_value"}
    response = supabase.table("test_table").insert(data).execute()

    if response.status_code != 201:
        raise RuntimeError(f"Failed to insert data: {response.json()}")

    print("Supabase connection validated successfully.")

if __name__ == "__main__":
    validate_supabase_connection()