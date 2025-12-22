#!/usr/bin/env bash
# Test script to verify QUEUE_MODE behavior in run_dev.sh

set -euo pipefail

ROOT_DIR="/workspaces/The_Awa_Network"
BACKEND_LOG="/tmp/uvicorn.log"
WORKER_URGENT_LOG="/tmp/rq_worker_urgent.log"
WORKER_DEFAULT_LOG="/tmp/rq_worker_default.log"
WORKER_SLOW_LOG="/tmp/rq_worker_slow.log"

cleanup() {
  echo "Cleaning up test processes..."
  pkill -f "uvicorn te_po.core.main" || true
  pkill -f "npm run dev" || true
  pkill -f "rq worker" || true
  docker stop kitenga-redis 2>/dev/null || true
  sleep 1
}

test_inline_mode() {
  echo ""
  echo "================================================================================"
  echo "TEST 1: INLINE MODE (QUEUE_MODE=inline, default)"
  echo "================================================================================"
  
  cleanup
  
  # Clear old logs
  rm -f "${BACKEND_LOG}" "${WORKER_URGENT_LOG}" "${WORKER_DEFAULT_LOG}" "${WORKER_SLOW_LOG}"
  
  echo "Starting run_dev.sh with QUEUE_MODE=inline..."
  cd "${ROOT_DIR}"
  timeout 8 bash -c 'QUEUE_MODE=inline ./run_dev.sh' 2>&1 || true
  
  sleep 3
  
  echo ""
  echo "Checking results:"
  echo "───────────────────────────────────────────────────────────────────────────────"
  
  # Check backend log for queue mode message
  if grep -q "Queue Mode: inline" "${BACKEND_LOG}"; then
    echo "✅ Backend reported 'Queue Mode: inline'"
  else
    echo "❌ Backend did not report inline mode"
  fi
  
  if grep -q "Starting with Inline mode" "${BACKEND_LOG}"; then
    echo "✅ Backend reported 'Starting with Inline mode (Redis + workers disabled)'"
  else
    echo "❌ Backend did not report inline mode message"
  fi
  
  # Check if Redis is running
  if docker ps 2>/dev/null | grep -q kitenga-redis; then
    echo "❌ Redis container is running (should NOT be running in inline mode)"
  else
    echo "✅ Redis container is NOT running (correct for inline mode)"
  fi
  
  # Check if RQ workers are running
  if pgrep -f "rq worker" >/dev/null 2>&1; then
    echo "❌ RQ worker processes are running (should NOT be running in inline mode)"
    pgrep -f "rq worker" || true
  else
    echo "✅ RQ worker processes are NOT running (correct for inline mode)"
  fi
  
  # Check if worker log files were created
  if [[ -f "${WORKER_URGENT_LOG}" ]]; then
    echo "❌ Worker log files were created (should NOT be in inline mode)"
  else
    echo "✅ Worker log files were NOT created (correct for inline mode)"
  fi
  
  # Check if backend is running
  if pgrep -f "uvicorn te_po.core.main" >/dev/null 2>&1; then
    echo "✅ Backend process is running (expected)"
  else
    echo "⚠️  Backend process not found (may have exited due to timeout)"
  fi
  
  cleanup
}

test_rq_mode() {
  echo ""
  echo "================================================================================"
  echo "TEST 2: RQ MODE (QUEUE_MODE=rq)"
  echo "================================================================================"
  
  cleanup
  
  # Clear old logs
  rm -f "${BACKEND_LOG}" "${WORKER_URGENT_LOG}" "${WORKER_DEFAULT_LOG}" "${WORKER_SLOW_LOG}"
  
  echo "Starting run_dev.sh with QUEUE_MODE=rq..."
  cd "${ROOT_DIR}"
  timeout 10 bash -c 'QUEUE_MODE=rq ./run_dev.sh' 2>&1 || true
  
  sleep 4
  
  echo ""
  echo "Checking results:"
  echo "───────────────────────────────────────────────────────────────────────────────"
  
  # Check backend log for queue mode message
  if grep -q "Queue Mode: rq" "${BACKEND_LOG}"; then
    echo "✅ Backend reported 'Queue Mode: rq'"
  else
    echo "❌ Backend did not report RQ mode"
  fi
  
  if grep -q "Starting with RQ mode" "${BACKEND_LOG}"; then
    echo "✅ Backend reported 'Starting with RQ mode (Redis + workers enabled)'"
  else
    echo "❌ Backend did not report RQ mode message"
  fi
  
  # Check if Redis is running
  if docker ps 2>/dev/null | grep -q kitenga-redis; then
    echo "✅ Redis container is running (correct for RQ mode)"
  else
    echo "❌ Redis container is NOT running (should be running in RQ mode)"
  fi
  
  # Check if RQ workers are running
  if pgrep -f "rq worker" >/dev/null 2>&1; then
    count=$(pgrep -f "rq worker" | wc -l)
    echo "✅ RQ worker processes are running ($count processes, expected 3 for urgent/default/slow)"
  else
    echo "❌ RQ worker processes are NOT running (should be running in RQ mode)"
  fi
  
  # Check if worker log files were created
  if [[ -f "${WORKER_URGENT_LOG}" ]] && [[ -f "${WORKER_DEFAULT_LOG}" ]] && [[ -f "${WORKER_SLOW_LOG}" ]]; then
    echo "✅ All 3 worker log files were created"
    echo "   - ${WORKER_URGENT_LOG}"
    echo "   - ${WORKER_DEFAULT_LOG}"
    echo "   - ${WORKER_SLOW_LOG}"
  else
    echo "❌ Not all worker log files were created"
    [[ -f "${WORKER_URGENT_LOG}" ]] && echo "   ✓ Urgent" || echo "   ✗ Urgent"
    [[ -f "${WORKER_DEFAULT_LOG}" ]] && echo "   ✓ Default" || echo "   ✗ Default"
    [[ -f "${WORKER_SLOW_LOG}" ]] && echo "   ✓ Slow" || echo "   ✗ Slow"
  fi
  
  # Check if backend is running
  if pgrep -f "uvicorn te_po.core.main" >/dev/null 2>&1; then
    echo "✅ Backend process is running (expected)"
  else
    echo "⚠️  Backend process not found (may have exited due to timeout)"
  fi
  
  cleanup
}

main() {
  echo ""
  echo "╔════════════════════════════════════════════════════════════════════════════╗"
  echo "║         run_dev.sh QUEUE MODE BEHAVIOR VERIFICATION                       ║"
  echo "╚════════════════════════════════════════════════════════════════════════════╝"
  
  test_inline_mode
  test_rq_mode
  
  echo ""
  echo "================================================================================"
  echo "TEST COMPLETE"
  echo "================================================================================"
}

main
