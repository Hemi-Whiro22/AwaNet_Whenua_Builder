from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Test loading of environment variables
required_keys = [
    "SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY",
    "POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD",
    "OPENAI_API_KEY", "OPENAI_ADMIN_KEY", "OPENAI_ORG_ID", "OPENAI_ORGANIZATION",
    "PIPELINE_TOKEN", "HUMAN_BEARER_KEY"
]

missing_keys = [key for key in required_keys if os.getenv(key) is None]

if missing_keys:
    print("Missing keys:", missing_keys)
else:
    print("All required keys are loaded successfully.")