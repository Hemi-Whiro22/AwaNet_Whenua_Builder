#!/bin/bash

echo "🌐 Booting Awa Network: Kitenga Whiro"

# Start Cloudflare Tunnels
echo "🔐 Starting Den (private)..."
cloudflared tunnel --config .cloudflared/kitenga_whiro_den.yml run kitenga_whiro_den &

echo "🌍 Starting Awanet (public)..."
cloudflared tunnel --config .cloudflared/kitenga_whiro_public.yml run kitenga_whiro_public &

# Start FastAPI backend
echo "🚀 Starting FastAPI (backend)..."
uvicorn te_po.core.main:app --host 0.0.0.0 --port 8000 --reload &

# Start Vite frontend (if needed)
echo "🎨 Starting Vite (frontend)..."
cd te_ao && npm run dev &

# Start Codex MCP server (optional for dev)
echo "🧠 Starting Codex MCP..."
# cd te_hau && python start_mcp.py &

wait  # Keep script alive until all child processes end
echo "🌟 Awa Network: Kitenga Whiro is up and running!"