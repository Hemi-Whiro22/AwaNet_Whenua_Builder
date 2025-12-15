#!/bin/bash
echo "🔧 Forcing DNS to Cloudflare..."
echo "nameserver 1.1.1.1" | sudo tee /etc/resolv.conf > /dev/null

echo "🌐 Launching Kitenga Whiro tunnel..."
cloudflared tunnel --config ./.cloudflared/config.yml run &
sleep 3

echo "🔥 Starting FastAPI server..."
uvicorn te_po.main:app --host 0.0.0.0 --port 8000
