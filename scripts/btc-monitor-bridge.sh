#!/bin/bash
#
# BTC Market Monitor with Browser Bridge Integration
# Watches windows, confirms resolution, triggers browser automation
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/../memory/trading/sessions"
BRIDGE_SCRIPT="$SCRIPT_DIR/polymarket_ui_bridge.py"

# Get next BTC window (5m or 15m)
get_next_window() {
    local timeframe=$1  # "5m" or "15m"
    local now=$(date -u +%s)
    
    if [ "$timeframe" = "5m" ]; then
        local interval=300
        local minutes=$(date -u +%M)
        local next_minute=$(((minutes / 5 + 1) * 5))
    else
        local interval=900
        local minutes=$(date -u +%M)
        local next_minute=$(((minutes / 15 + 1) * 15))
    fi
    
    local current_hour=$(date -u +%H)
    local current_day=$(date -u +%d)
    
    if [ $next_minute -ge 60 ]; then
        next_minute=0
        current_hour=$((current_hour + 1))
    fi
    
    if [ $current_hour -ge 24 ]; then
        current_hour=0
        current_day=$((current_day + 1))
    fi
    
    echo "$(date -u -d "${current_day}T${current_hour}:${next_minute}:00" +%s)"
}

# Calculate market slug from timestamp
calculate_slug() {
    local ts=$1
    local timeframe=$2
    echo "btc-updown-${timeframe}-${ts}"
}

# Fetch current BTC price from CoinGecko
get_btc_price() {
    curl -s "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd" | \
        grep -o '"usd":[0-9.]*' | cut -d':' -f2
}

# Log trade to file
log_trade() {
    local timestamp=$1
    local market=$2
    local side=$3
    local start_price=$4
    local end_price=$5
    local pm_prices=$6
    local status=$7
    
    local log_file="$LOG_DIR/browser-bridge-$(date -u +%Y-%m-%d).jsonl"
    
    echo "{\"timestamp\":\"$timestamp\",\"market\":\"$market\",\"side\":\"$side\",\"start_price\":$start_price,\"end_price\":$end_price,\"pm_prices\":\"$pm_prices\",\"status\":\"$status\"}" >> "$log_file"
}

# Monitor a window and trigger bridge
monitor_window() {
    local timeframe=$1
    local window_end=$2
    local start_price=$3
    local market_slug=$4
    
    echo ""
    echo "═══════════════════════════════════════════════════"
    echo "  Monitoring BTC ${timeframe} window"
    echo "  Market: $market_slug"
    echo "  Start price: \$$start_price"
    echo "  Window closes: $(date -u -d "@$window_end" '+%H:%M:%S UTC')"
    echo "═══════════════════════════════════════════════════"
    
    # Wait until 10 seconds before close
    local now=$(date -u +%s)
    local wait_time=$((window_end - now - 10))
    
    if [ $wait_time -gt 0 ]; then
        echo "⏳ Waiting ${wait_time}s until 10s before close..."
        sleep $wait_time
    fi
    
    # At 10s before close: Launch browser and position
    echo "🚀 Launching browser bridge..."
    python3 "$BRIDGE_SCRIPT" --position "$market_slug" &
    local bridge_pid=$!
    
    # Wait for window to close
    sleep 10
    
    # Window closed - fetch resolution price
    echo "📊 Window closed, fetching resolution price..."
    local end_price=$(get_btc_price)
    echo "   Start: \$$start_price"
    echo "   End:   \$$end_price"
    
    # Determine outcome
    local outcome
    if (( $(echo "$end_price >= $start_price" | bc -l) )); then
        outcome="UP"
    else
        outcome="DOWN"
    fi
    
    echo "   Outcome: $outcome"
    
    # Trigger browser refresh and execution
    echo "⚡ Triggering browser execution for $outcome..."
    
    # Signal bridge to execute (via file or API - simplified here)
    # In full implementation, use IPC or HTTP endpoint
    
    # For now, log the opportunity
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    log_trade "$timestamp" "$market_slug" "$outcome" "$start_price" "$end_price" "pending" "executing"
    
    # Wait for bridge to complete
    wait $bridge_pid 2>/dev/null || true
    
    echo "✅ Window complete"
    echo ""
}

# Main loop
main() {
    echo "🤖 BTC Market Monitor + Browser Bridge"
    echo "Press Ctrl+C to stop"
    echo ""
    
    mkdir -p "$LOG_DIR"
    
    while true; do
        # Get next 15m window
        local window_end=$(get_next_window "15m")
        local start_time=$((window_end - 900))
        local market_slug=$(calculate_slug $window_end "15m")
        
        # Record start price
        echo "📈 Recording start price for next window..."
        local start_price=$(get_btc_price)
        
        echo "   Window: $(date -u -d "@$start_time" '+%H:%M') - $(date -u -d "@$window_end" '+%H:%M') UTC"
        echo "   BTC Price: \$$start_price"
        echo ""
        
        # Wait until 2 minutes before window starts
        local now=$(date -u +%s)
        local pre_window_wait=$((start_time - now - 120))
        
        if [ $pre_window_wait -gt 0 ]; then
            echo "⏳ Next window in ${pre_window_wait}s, waiting..."
            sleep $pre_window_wait
        fi
        
        # Monitor the window
        monitor_window "15m" $window_end $start_price "$market_slug"
        
        # Brief pause between windows
        sleep 5
    done
}

# Handle interrupt
trap 'echo ""; echo "🛑 Monitor stopped"; exit 0' INT

main "$@"
