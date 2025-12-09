from dotenv import load_dotenv
load_dotenv()

import anyio
import os
from mcp.server.fastmcp import FastMCP

from tools.supabase_tools import supabase_search, supabase_insert
from tools.file_tools import read_file, list_files

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
