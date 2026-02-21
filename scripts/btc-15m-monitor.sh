#!/bin/bash
# BTC 15m Window Monitor
# Usage: ./scripts/btc-15m-monitor.sh <window_timestamp>

WINDOW_TS=$1
WINDOW_DATE=$(date -u -r $WINDOW_TS '+%H:%M UTC' 2>/dev/null || echo "unknown")
LOG_FILE="memory/trading/sessions/paper-session-2026-02-20.md"

echo "=== BTC 15m Window Monitor ==="
echo "Window: $WINDOW_TS ($WINDOW_DATE)"
echo ""

# Get start price (assumes recorded in /tmp)
START_PRICE_FILE="/tmp/btc_start_${WINDOW_TS}.txt"
if [ -f "$START_PRICE_FILE" ]; then
    START_PRICE=$(cat "$START_PRICE_FILE")
    echo "Start Price: $START_PRICE"
else
    echo "⚠️ No start price recorded for this window"
    START_PRICE="unknown"
fi

# Wait for window close
CURRENT_TS=$(date -u +%s)
if [ $CURRENT_TS -lt $WINDOW_TS ]; then
    SLEEP_SEC=$((WINDOW_TS - CURRENT_TS + 5))  # +5s buffer
    echo "Waiting $SLEEP_SEC seconds for window close..."
    sleep $SLEEP_SEC
fi

echo ""
echo "=== Window Closed: $(date -u '+%H:%M:%S UTC') ==="

# Get end price from multiple sources
echo "Fetching end prices..."
END_COINGECKO=$(curl -s 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd' | jq -r '.bitcoin.usd')
END_COINBASE=$(curl -s 'https://api.coinbase.com/v2/exchange-rates?currency=BTC' | jq -r '.data.rates.USD')
END_KRAKEN=$(curl -s 'https://api.kraken.com/0/public/Ticker?pair=XBTUSD' | jq -r '.result.XXBTZUSD.c[0]')

echo "  CoinGecko: $END_COINGECKO"
echo "  Coinbase:  $END_COINBASE"
echo "  Kraken:    $END_KRAKEN"

# Determine outcome (if we have start price)
if [ "$START_PRICE" != "unknown" ]; then
    # Use CoinGecko as primary
    if (( $(echo "$END_COINGECKO >= $START_PRICE" | bc -l) )); then
        OUTCOME="UP"
    else
        OUTCOME="DOWN"
    fi
    echo ""
    echo "Outcome: $OUTCOME (Start: $START_PRICE, End: $END_COINGECKO)"
    
    # Log to file
    echo "" >> "$LOG_FILE"
    echo "### Window $WINDOW_DATE" >> "$LOG_FILE"
    echo "- Start Price: $START_PRICE" >> "$LOG_FILE"
    echo "- End Price: $END_COINGECKO" >> "$LOG_FILE"
    echo "- Outcome: $OUTCOME" >> "$LOG_FILE"
    echo "- Status: Pending Polymarket check" >> "$LOG_FILE"
fi

echo ""
echo "Next: Check Polymarket market for $OUTCOME side price"
echo "If price < \$0.90, log paper trade with edge calculation"
