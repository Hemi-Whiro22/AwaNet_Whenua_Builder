#!/usr/bin/env bash
set -euo pipefail

UVICORN=${UVICORN:-uvicorn}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-6000}

exec "$UVICORN" te_po.kaitiaki.whiro.http_bridge:app --host "$HOST" --port "$PORT"
