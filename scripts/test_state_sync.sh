#!/bin/bash

# Smoke test for state endpoints

BASE_URL="http://localhost:10000"
BEARER_TOKEN="your_bearer_token_here"

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

echo "[PASS] All state endpoints are working as expected."