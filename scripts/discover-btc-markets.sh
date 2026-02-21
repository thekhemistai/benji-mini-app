#!/bin/bash
# Polymarket 15-Minute BTC Market Discovery
# Usage: ./discover-btc-markets.sh [hours_ahead]

HOURS_AHEAD=${1:-2}  # Default: show markets for next 2 hours

# Get current Unix timestamp
NOW=$(date +%s)

# Round to nearest 15-minute boundary (900 seconds)
# Floor division to get the start of current 15-min window
CURRENT_WINDOW=$(( (NOW / 900) * 900 ))

# Calculate end timestamp (X hours ahead)
END_TIME=$(( NOW + (HOURS_AHEAD * 3600) ))

echo "==================================="
echo "BTC 15-Minute Markets"
echo "Current time: $(date -r $NOW '+%Y-%m-%d %H:%M:%S %Z')"
echo "Showing next $HOURS_AHEAD hours"
echo "==================================="
echo ""

# Generate URLs for each 15-minute window
TIMESTAMP=$CURRENT_WINDOW
while [ $TIMESTAMP -le $END_TIME ]; do
    HUMAN_TIME=$(date -r $TIMESTAMP '+%Y-%m-%d %H:%M:%S %Z')
    URL="https://polymarket.com/event/btc-updown-15m-$TIMESTAMP"
    
    echo "Window: $HUMAN_TIME"
    echo "URL:    $URL"
    echo ""
    
    TIMESTAMP=$(( TIMESTAMP + 900 ))
done

echo "==================================="
echo "Quick check command:"
echo "curl -s '$URL' -o /dev/null -w '%{http_code}'"
echo "==================================="
