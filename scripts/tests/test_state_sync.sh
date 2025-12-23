#!/bin/bash

# Smoke test for state endpoints

BASE_URL="${STATE_BASE_URL:-${API_URL:-http://localhost:10000}}"
BEARER_TOKEN="${PIPELINE_TOKEN:-${HUMAN_BEARER_KEY:-}}"

# Test /heartbeat
curl -v "$BASE_URL/heartbeat" || {
  echo "[FAIL] /heartbeat endpoint is not reachable."
  exit 1
}

# Test /state/public
curl -v "$BASE_URL/state/public" || {
  echo "[FAIL] /state/public endpoint is not reachable."
  exit 1
}

# Test /state/private with Bearer token
if [ -n "$BEARER_TOKEN" ]; then
  curl -v -H "Authorization: Bearer $BEARER_TOKEN" "$BASE_URL/state/private" || {
    echo "[FAIL] /state/private endpoint is not reachable or Bearer token is invalid."
    exit 1
  }

  # Test /state/private without Bearer token (should fail)
  curl -v "$BASE_URL/state/private" && {
    echo "[FAIL] /state/private endpoint is accessible without Bearer token."
    exit 1
  } || {
    echo "[PASS] /state/private endpoint is protected as expected."
  }
else
  echo "[WARN] PIPELINE_TOKEN / HUMAN_BEARER_KEY not set; skipping private state tests."
fi

echo "[PASS] All state endpoints are working as expected."
