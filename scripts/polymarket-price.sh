#!/bin/bash
# Polymarket Price Fetcher via Gamma API
# Usage: ./scripts/polymarket-price.sh <market_slug>

SLUG=$1

if [ -z "$SLUG" ]; then
    echo "Usage: $0 <market_slug>"
    echo "Example: $0 btc-updown-15m-1771569900"
    exit 1
fi

# Fetch market data
MARKET_DATA=$(curl -s "https://gamma-api.polymarket.com/markets?slug=${SLUG}")

if [ -z "$MARKET_DATA" ] || [ "$MARKET_DATA" = "[]" ]; then
    echo "Error: Market not found"
    exit 1
fi

# Extract key fields
MARKET_ID=$(echo "$MARKET_DATA" | jq -r '.[0].id')
QUESTION=$(echo "$MARKET_DATA" | jq -r '.[0].question')
OUTCOME_PRICES=$(echo "$MARKET_DATA" | jq -r '.[0].outcomePrices')
OUTCOMES=$(echo "$MARKET_DATA" | jq -r '.[0].outcomes')
CLOB_TOKEN_IDS=$(echo "$MARKET_DATA" | jq -r '.[0].clobTokenIds')

# Parse outcomes and prices
OUTCOME_1=$(echo "$OUTCOMES" | jq -r '.[0]')
OUTCOME_2=$(echo "$OUTCOMES" | jq -r '.[1]')
PRICE_1=$(echo "$OUTCOME_PRICES" | jq -r '.[0]')
PRICE_2=$(echo "$OUTCOME_PRICES" | jq -r '.[1]')
TOKEN_1=$(echo "$CLOB_TOKEN_IDS" | jq -r '.[0]')
TOKEN_2=$(echo "$CLOB_TOKEN_IDS" | jq -r '.[1]')

echo "=== Polymarket Market Data ==="
echo "Market ID: $MARKET_ID"
echo "Question: $QUESTION"
echo ""
echo "=== Outcome Prices ==="
printf "%-10s %s\n" "$OUTCOME_1" "$PRICE_1"
printf "%-10s %s\n" "$OUTCOME_2" "$PRICE_2"
echo ""

# Fetch order book for first token (usually YES/UP)
echo "=== Order Book (Best Bids) ==="
curl -s "https://clob.polymarket.com/book?token_id=${TOKEN_1}" | jq -r '.bids | sort_by(.price) | reverse | .[0:5] | .[] | "\(.price) | \(.size)"' | head -5

echo ""
echo "=== Quick Links ==="
echo "Market: https://polymarket.com/event/${SLUG}"
echo "API: https://gamma-api.polymarket.com/markets?slug=${SLUG}"
