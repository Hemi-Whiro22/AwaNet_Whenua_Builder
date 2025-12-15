import os
from pathlib import Path

from dotenv import load_dotenv
from mauri.te_kete.load_manifest import load_manifest

import anyio
from mcp.server.fastmcp import FastMCP

from tools.supabase_tools import supabase_search, supabase_insert
from tools.file_tools import read_file, list_files


# ────────────────────────────────────────────────
# 💠 Environment + Config
# ────────────────────────────────────────────────
def load_environment():
    env_dir = Path.cwd()
    primary_env = env_dir / ".env"
    fallback_env = env_dir / ".env.kaitiaki"

    if primary_env.exists():
        load_dotenv(dotenv_path=primary_env)
    elif fallback_env.exists():
        load_dotenv(dotenv_path=fallback_env)
    else:
        load_dotenv()

    kitenga_id = os.getenv("KITENGA_ASSISTANT_ID", "")
    qa_id = os.getenv("OPENAI_ASSISTANT_ID_QA", "")
    vector_id = os.getenv("OPENAI_VECTOR_STORE_ID", "")

    print("💠 Kitenga Env Loaded:")
    print(f"🔑 KITENGA_ASSISTANT_ID: {kitenga_id}")
    print(f"🧪 QA_ASSISTANT_ID: {qa_id}")
    print(f"🧠 VECTOR_STORE_ID: {vector_id}")

    return kitenga_id, qa_id, vector_id


KITENGA_ASSISTANT_ID, QA_ASSISTANT_ID, VECTOR_STORE_ID = load_environment()


# ────────────────────────────────────────────────
# 🛡️ Manifest Validation
# ────────────────────────────────────────────────
kitenga_dir = Path(__file__).resolve().parent
manifest_path = kitenga_dir / "kitenga_manifest.json"
manifest = load_manifest(str(manifest_path))

print("\n🛡️ Kaitiaki Manifest Tools:")
for tool_name in manifest.get("tools", []):
    print(f"🛠️  Tool loaded: {tool_name}")

manifest_assistant_id = manifest.get("assistant_id")
if manifest_assistant_id != KITENGA_ASSISTANT_ID:
    print("⚠️  Mismatch between manifest and .env assistant_id")
else:
    print("✅ Assistant ID matches manifest.")


# ────────────────────────────────────────────────
# 🧠 LLM + MCP Bootstrap
# ────────────────────────────────────────────────
def init_openai_client():
    """Placeholder for OpenAI client initialization."""
    return None


init_openai_client()

app = FastMCP(
    "kitenga",
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
