#!/bin/bash
# BTC Market Arb Monitor
# Monitors BTC markets AFTER resolution for price divergence
# 
# Usage: ./btc-arb-monitor.sh [market_slug]

MARKET_SLUG=${1:-"btc-updown-15m-$(($(date +%s) / 900 * 900))"}
RESOLUTION_TIME=$(echo $MARKET_SLUG | grep -o '[0-9]*$')

# Convert to human readable
RESOLVE_HUMAN=$(date -r $RESOLUTION_TIME '+%I:%M:%S %p %Z' 2>/dev/null || date -d @$RESOLUTION_TIME '+%I:%M:%S %p %Z')

echo "==================================="
echo "BTC Arb Monitor — Post-Resolution"
echo "Target Market: $MARKET_SLUG"
echo "Resolution: $RESOLVE_HUMAN"
echo "==================================="
echo ""
echo "Waiting for resolution window..."
echo ""

# Get current BTC price from Chainlink
echo "Current BTC/USD (Chainlink):"
curl -s "https://data.chain.link/streams/btc-usd" 2>/dev/null | grep -o '"price":[0-9.]*' | head -1 || echo "  Manual check: https://data.chain.link/streams/btc-usd"
echo ""

# Query market data from Polymarket
echo "Polymarket Market Data:"
API_RESPONSE=$(curl -s "https://gamma-api.polymarket.com/events?slug=$MARKET_SLUG" 2>/dev/null)

if [ -n "$API_RESPONSE" ]; then
    echo "$API_RESPONSE" | grep -o '"bestBid":[0-9.]*' | head -1
    echo "$API_RESPONSE" | grep -o '"bestAsk":[0-9.]*' | head -1
    echo "$API_RESPONSE" | grep -o '"endDate":"[^"]*"' | head -1
else
    echo "  Market: https://polymarket.com/event/$MARKET_SLUG"
fi

echo ""
echo "==================================="
echo "ARB CHECK PROTOCOL:"
echo "1. Wait for resolution time: $RESOLVE_HUMAN"
echo "2. Check Chainlink: Start vs End price"
echo "3. Confirm outcome (UP or DOWN)"
echo "4. Check Polymarket within 30-60 seconds"
echo "5. If winning side < $0.90, arb opportunity exists"
echo "6. Paper trade: Log entry, track to $1.00"
echo "==================================="
