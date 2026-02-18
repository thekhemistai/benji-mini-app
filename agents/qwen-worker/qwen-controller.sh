#!/bin/bash
# Qwen Worker Controller
# Master script to run all Qwen tasks
# Called by cron every 15 minutes

set -euo pipefail

WORKSPACE="/Users/thekhemist/.openclaw/workspace"
LOG_FILE="$WORKSPACE/agents/qwen-worker/logs/qwen-worker-$(date +%Y%m%d).log"

# Ensure log directory exists
mkdir -p "$WORKSPACE/agents/qwen-worker/logs"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "=== Qwen Worker Starting ==="

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    log "⚠️  Ollama not running. Starting..."
    ollama serve &
    sleep 2
fi

# Task 1: Heartbeat (every 30 min - check if minute is 00 or 30)
MINUTE=$(date +%M)
if [[ "$MINUTE" == "00" || "$MINUTE" == "30" ]]; then
    log "Running heartbeat check..."
    python3 "$WORKSPACE/agents/qwen-worker/tasks/heartbeat.py" >> "$LOG_FILE" 2>&1 || log "⚠️  Heartbeat failed"
fi

# Task 2: Price data (every 15 min)
log "Running price data fetch..."
python3 "$WORKSPACE/agents/qwen-worker/tasks/data_fetcher.py" >> "$LOG_FILE" 2>&1 || log "⚠️  Data fetcher failed"

# Task 3: File organization (once per day at 00:00)
HOUR=$(date +%H)
if [[ "$HOUR" == "00" && "$MINUTE" == "00" ]]; then
    log "Running daily file organization..."
    python3 "$WORKSPACE/agents/qwen-worker/tasks/file_organizer.py" >> "$LOG_FILE" 2>&1 || log "⚠️  File organizer failed"
    log "✅ Daily tasks complete"
fi

log "=== Qwen Worker Complete ==="
