from te_po.utils.supabase_client import get_client

client = get_client()
if client:
    print("Supabase client initialized successfully.")
else:
    print("Failed to initialize Supabase client.")