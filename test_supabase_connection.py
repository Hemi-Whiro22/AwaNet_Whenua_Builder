import os
from dotenv import load_dotenv
from supabase import create_client
from pathlib import Path

# Update the .env path to point to the te_po directory
env_path = Path(__file__).parent / "te_po" / ".env"
load_dotenv(env_path)

# Print the resolved .env path and its contents for debugging
print(f"Resolved .env path: {env_path}")
if env_path.exists():
    with open(env_path, 'r') as f:
        print(".env contents:")
        print(f.read())
else:
    print(".env file does not exist at the resolved path.")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Missing Supabase URL or Key. Please check your .env file.")
else:
    try:
        print("Testing Supabase connection...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.table("test_table").select("*").execute()
        print("Connection successful! Response:", response)
    except Exception as e:
        print("Failed to connect to Supabase:", e)