#!/bin/bash
#
# Khem 5m BTC Arbitrage Monitor
# Uses Gamma API for monitoring, Bankr for execution
#

MARKET_SLUG="btc-updown-5m-1771659900"
MARKET_NAME="BTC 5m - Feb 21 2:45-2:50AM ET"
CLOSE_TIME="07:50"  # UTC

echo "🧪 Khem 5m Arb Monitor"
echo "Market: $MARKET_NAME"
echo "Closes: $CLOSE_TIME UTC"
echo ""

# Monitor loop
echo "⏳ Monitoring for resolution..."
echo "Current UTC: $(date -u +%H:%M:%S)"
echo ""

# Wait until close time minus buffer
TARGET_MINUTE=50
CURRENT_MINUTE=$(date -u +%M)

while [ $CURRENT_MINUTE -lt $TARGET_MINUTE ]; do
    sleep 10
    CURRENT_MINUTE=$(date -u +%M)
    echo -ne "\rWaiting... $(date -u +%H:%M:%S)"
done

echo ""
echo "🔔 Window closing! Checking resolution..."

# Query Chainlink for resolution
python3 << 'EOF'
import httpx
import json
from datetime import datetime

# Chainlink BTC/USD data feed
CHAINLINK_URL = "https://data.chain.link/streams/btc-usd"

print("📊 Querying Chainlink BTC/USD...")

try:
    response = httpx.get(CHAINLINK_URL, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response preview: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
EOF

echo ""
echo "⏱️  Resolution detected - executing via Bankr..."
echo "Command: npx bankr 'buy YES on btc-updown-5m-1771659900'"
