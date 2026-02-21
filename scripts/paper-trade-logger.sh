#!/bin/bash
# Polymarket Paper Trade Logger
# Logs paper trades for information arbitrage analysis

TRADE_LOG="memory/trading/arb-results.md"
SESSION_LOG="memory/trading/sessions/paper-session-2026-02-20.md"

log_paper_trade() {
    local trade_num=$1
    local timestamp=$2
    local market=$3
    local side=$4
    local entry=$5
    local edge=$6
    local source=$7
    local status=$8
    
    cat >> "$SESSION_LOG" << EOF

### Paper Trade #$trade_num
- **Time:** $timestamp
- **Market:** $market
- **Side:** $side
- **Entry:** $entry
- **Edge:** $edge
- **Source Confirm:** $source
- **Status:** $status

EOF

    echo "✅ Paper trade #$trade_num logged"
}

# Export function for use in other scripts
export -f log_paper_trade
