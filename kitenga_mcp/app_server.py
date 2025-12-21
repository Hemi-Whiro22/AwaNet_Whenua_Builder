# kitenga_mcp/app_server.py

from fastapi import FastAPI

# create the FastAPI application object
app = FastAPI(title="Kitenga MCP App", version="1.0.0")

@app.get("/mcp/health")
async def health():
    return {"status": "alive", "message": "MCP server responding"}
