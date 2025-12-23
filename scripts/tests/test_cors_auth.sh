#!/bin/bash
# Test CORS and Bearer auth behavior locally and on Render
# Usage: ./scripts/test_cors_auth.sh [local|render]

TARGET="${1:-local}"
API_OVERRIDE="${2:-}"

case "$TARGET" in
  render)
    API_DEFAULT="https://tiwhanawhana-backend.onrender.com"
    ;;
  *)
    API_DEFAULT="http://localhost:10000"
    ;;
esac

API_URL="${API_OVERRIDE:-$API_DEFAULT}"
HEARTBEAT_ROUTE="/heartbeat"
PROTECTED_ROUTE="/api/intake"

# Get token from environment
TOKEN="${PIPELINE_TOKEN:-${HUMAN_BEARER_KEY}}"

echo "═══════════════════════════════════════════════════════════"
echo "CORS & Auth Tests - Target: $TARGET"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Test 1: Unprotected route without auth
echo "✓ Test 1: Unprotected route (/heartbeat) - NO auth required"
echo "  Command: curl -i $API_URL$HEARTBEAT_ROUTE"
curl -s -i "$API_URL$HEARTBEAT_ROUTE" | head -1
echo ""

# Test 2: Protected route without auth
echo "✓ Test 2: Protected route ($PROTECTED_ROUTE) - NO token → 401"
echo "  Command: curl -i $API_URL$PROTECTED_ROUTE"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL$PROTECTED_ROUTE")
echo "  Result: HTTP $HTTP_CODE (expected 401)"
echo ""

# Test 3: Protected route with invalid token
echo "✓ Test 3: Protected route ($PROTECTED_ROUTE) - INVALID token → 403"
echo "  Command: curl -i -H 'Authorization: Bearer invalid' $API_URL$PROTECTED_ROUTE"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer invalid" \
    "$API_URL$PROTECTED_ROUTE")
echo "  Result: HTTP $HTTP_CODE (expected 403)"
echo ""

# Test 4: Protected route with valid token
if [ -z "$TOKEN" ]; then
    echo "⚠ Test 4: SKIPPED (PIPELINE_TOKEN not set)"
    echo "  Set \$PIPELINE_TOKEN to test with valid token"
else
    echo "✓ Test 4: Protected route ($PROTECTED_ROUTE) - VALID token"
    echo "  Command: curl -i -H 'Authorization: Bearer <token>' $API_URL$PROTECTED_ROUTE"
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: Bearer $TOKEN" \
        "$API_URL$PROTECTED_ROUTE")
    echo "  Result: HTTP $HTTP_CODE (expected 200, 400, or other non-401/403)"
fi
echo ""

# Test 5: CORS Preflight
if [ "$TARGET" = "local" ]; then
    echo "✓ Test 5: CORS Preflight - OPTIONS request"
    echo "  Command: curl -i -X OPTIONS -H 'Origin: http://localhost:5173' $API_URL$PROTECTED_ROUTE"
    curl -s -i -X OPTIONS \
        -H "Origin: http://localhost:5173" \
        -H "Access-Control-Request-Method: POST" \
        "$API_URL$PROTECTED_ROUTE" | head -5
else
    echo "⚠ Test 5: CORS Preflight - SKIPPED (requires local testing)"
fi
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "Summary:"
echo "  ✓ /heartbeat should return 200 without auth"
echo "  ✓ Protected routes without token should return 401"
echo "  ✓ Protected routes with invalid token should return 403"
echo "  ✓ Protected routes with valid token should return 200+ (not 401/403)"
echo "═══════════════════════════════════════════════════════════"
