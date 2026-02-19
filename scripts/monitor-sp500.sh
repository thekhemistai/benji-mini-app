#!/bin/bash
# Polymarket Arb Monitor - S&P 500 Market
# Runs: Feb 19, 2026 starting 9:00 AM ET

MARKET_ID="spx-opens-up-or-down-on-february-19-2026"
RESOLUTION_TIME="09:30"  # Market open ET
LOG_FILE="/Users/thekhemist/.openclaw/workspace/memory/trading/monitor-$(date +%Y%m%d).log"

echo "[$(date)] Starting S&P 500 monitor for Feb 19" >> $LOG_FILE

# Check pre-market futures every minute starting 9:00 AM
while true; do
  CURRENT_TIME=$(date +%H:%M)
  
  if [[ "$CURRENT_TIME" == "09:30" ]]; then
    # Market open - check first print
    echo "[$(date)] MARKET OPEN - Checking S&P 500 direction..." >> $LOG_FILE
    
    # Source 1: Yahoo Finance API
    SPY_DATA=$(curl -s "https://query1.finance.yahoo.com/v8/finance/chart/SPY?interval=1m&range=1d" 2>/dev/null)
    
    # Source 2: Alpha Vantage or backup
    
    # Parse direction
    PREV_CLOSE=$(echo $SPY_DATA | jq -r '.chart.result[0].meta.previousClose' 2>/dev/null)
    FIRST_PRINT=$(echo $SPY_DATA | jq -r '.chart.result[0].indicators.quote[0].open[0]' 2>/dev/null)
    
    if [[ -n "$PREV_CLOSE" && -n "$FIRST_PRINT" ]]; then
      if (( $(echo "$FIRST_PRINT > $PREV_CLOSE" | bc -l) )); then
        DIRECTION="UP"
      else
        DIRECTION="DOWN"
      fi
      
      echo "[$(date)] RESOLUTION: S&P 500 opened $DIRECTION" >> $LOG_FILE
      echo "[$(date)] Prev close: $PREV_CLOSE, First print: $FIRST_PRINT" >> $LOG_FILE
      
      # Check Polymarket price (via API)
      PM_DATA=$(curl -s "https://gamma-api.polymarket.com/markets?slug=spx-opens-up-or-down-on-february-19-2026" 2>/dev/null)
      UP_PRICE=$(echo $PM_DATA | jq -r '.[0].outcomePrices' | jq -r '.[0]' 2>/dev/null)
      
      echo "[$(date)] Polymarket UP price: $UP_PRICE" >> $LOG_FILE
      
      # Log paper trade if edge exists
      if [[ "$DIRECTION" == "UP" && $(echo "$UP_PRICE < 0.90" | bc -l) -eq 1 ]]; then
        echo "[$(date)] PAPER TRADE OPPORTUNITY: Buy UP at $UP_PRICE" >> $LOG_FILE
      elif [[ "$DIRECTION" == "DOWN" && $(echo "(1 - $UP_PRICE) < 0.90" | bc -l) -eq 1 ]]; then
        DOWN_PRICE=$(echo "1 - $UP_PRICE" | bc -l)
        echo "[$(date)] PAPER TRADE OPPORTUNITY: Buy DOWN at $DOWN_PRICE" >> $LOG_FILE
      fi
    fi
    
    break  # Done for today
  fi
  
  # Check futures every minute before open
  if [[ "$CURRENT_TIME" > "08:30" && "$CURRENT_TIME" < "09:30" ]]; then
    FUTURES=$(curl -s "https://query1.finance.yahoo.com/v8/finance/chart/ES=F?interval=1m&range=1d" 2>/dev/null)
    FUTURES_PRICE=$(echo $FUTURES | jq -r '.chart.result[0].meta.regularMarketPrice' 2>/dev/null)
    echo "[$(date)] Pre-market futures: $FUTURES_PRICE" >> $LOG_FILE
  fi
  
  sleep 60
done
