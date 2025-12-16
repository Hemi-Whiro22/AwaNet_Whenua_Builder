import os
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv

import anyio
from mcp.server.fastmcp import FastMCP

from tools.supabase_tools import supabase_search, supabase_insert
from tools.file_tools import read_file, list_files


# ────────────────────────────────────────────────
# 💠 Environment + Config
# ────────────────────────────────────────────────
def load_environment():
    """Load environment from .env.kitenga_whiro or fallbacks."""
    env_path = os.getenv("DOTENV_PATH")
    
    if env_path:
        dotenv_file = PROJECT_ROOT / env_path
    else:
        # Priority: .env.kitenga_whiro > .env > .env.kaitiaki
        dotenv_file = PROJECT_ROOT / ".env.kitenga_whiro"
        if not dotenv_file.exists():
            dotenv_file = PROJECT_ROOT / ".env"
        if not dotenv_file.exists():
            dotenv_file = PROJECT_ROOT / ".env.kaitiaki"
    
    if dotenv_file.exists():
        load_dotenv(dotenv_path=dotenv_file)
        print(f"💠 Loaded env from: {dotenv_file.name}")
    else:
        load_dotenv()
        print("💠 Loaded env from system")

    kitenga_id = os.getenv("KITENGA_ASSISTANT_ID", "")
    qa_id = os.getenv("OPENAI_ASSISTANT_ID_QA", "")
    vector_id = os.getenv("OPENAI_VECTOR_STORE_ID", os.getenv("KITENGA_VECTOR_STORE_ID", ""))

    print("🐺 Kitenga Whiro Env:")
    print(f"   KITENGA_ASSISTANT_ID: {kitenga_id[:20]}..." if kitenga_id else "   KITENGA_ASSISTANT_ID: Not set")
    print(f"   VECTOR_STORE_ID: {vector_id[:20]}..." if vector_id else "   VECTOR_STORE_ID: Not set")

    return kitenga_id, qa_id, vector_id


KITENGA_ASSISTANT_ID, QA_ASSISTANT_ID, VECTOR_STORE_ID = load_environment()


# ────────────────────────────────────────────────
# 🛡️ Manifest Validation (optional - use new manifest)
# ────────────────────────────────────────────────
def load_manifest_safe():
    """Load manifest from mauri/te_kete if available."""
    manifest_path = PROJECT_ROOT / "mauri" / "te_kete" / "kitenga_whiro.manifest.json"
    if manifest_path.exists():
        import json
        with open(manifest_path) as f:
            return json.load(f)
    return {"tools": [], "name": "kitenga_whiro"}


manifest = load_manifest_safe()

print(f"\n🛡️ Kitenga Whiro ({manifest.get('role', 'kaitiaki')}):")
print(f"   Purpose: {manifest.get('purpose', 'Not defined')}")
print(f"   Tools: {len(manifest.get('tools', []))} registered")


# ────────────────────────────────────────────────
# 🧠 MCP Server Bootstrap
# ────────────────────────────────────────────────
app = FastMCP(
    "kitenga_whiro",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "39285")),
    streamable_http_path="/mcp",
)

app.add_tool(
    supabase_search,
    name="supabase_search",
    description="Search a Supabase table by ilike on the 'content' column.",
)
app.add_tool(
    supabase_insert,
    name="supabase_insert",
    description="Insert a record into a Supabase table.",
)
app.add_tool(
    read_file,
    name="read_file",
    description="Read a UTF-8 file from disk.",
)
app.add_tool(
    list_files,
    name="list_files",
    description="List directory contents.",
)


if __name__ == "__main__":
    anyio.run(app.run_streamable_http_async)
