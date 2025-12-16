import os
from supabase import create_client

# Load environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise ValueError("Supabase URL or Service Role Key is not set in the environment variables.")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Define the table activation logic
def activate_table():
    try:
        # Example query to ensure the table is accessible
        response = supabase.table("project_state_public").select("*").limit(1).execute()
        print("Table activation successful. Response:")
        print(response.data)
    except Exception as e:
        print("Error activating table:", e)

if __name__ == "__main__":
    activate_table()