#!/usr/bin/env python3
"""
Polymarket Speed Arb - Ultra Simple
See price move in real world → Bet before oracle updates
"""

import time
import requests
from datetime import datetime

# Settings
CHECK_INTERVAL = 3      # Check price every 3 seconds
MOVE_THRESHOLD = 0.05   # 0.05% price move = trigger (adjust based on testing)

# Track
last_price = None
last_price_time = None


def get_btc_price():
    """Get current BTC price."""
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            timeout=3
        )
        return r.json()["bitcoin"]["usd"]
    except:
        return None


def main():
    global last_price, last_price_time
    
    print("=" * 50)
    print("⚡ POLYMARKET SPEED ARBITRAGE")
    print("Real price → Bet → Wait for oracle")
    print("=" * 50)
    print(f"\nChecking every {CHECK_INTERVAL}s")
    print(f"Trigger: {MOVE_THRESHOLD}% price move")
    print("\nCtrl+C to stop\n")
    
    while True:
        price = get_btc_price()
        now = datetime.now()
        
        if price and last_price:
            change_pct = ((price - last_price) / last_price) * 100
            
            if abs(change_pct) >= MOVE_THRESHOLD:
                # PRICE MOVED - this is the signal
                direction = "UP" if change_pct > 0 else "DOWN"
                
                print(f"\n🚨 {direction} MOVE: ${last_price:,.2f} → ${price:,.2f} ({change_pct:+.3f}%)")
                print(f"   TIME: {now.strftime('%H:%M:%S')}")
                print(f"   ACTION: Bet {direction} on Polymarket NOW")
                print(f"   REASON: Oracle hasn't updated yet - seize the window\n")
                
                # Here you'd execute the trade via Bankr or CLOB API
                # For now just log it
                
        # Update tracking
        last_price = price
        last_price_time = now
        
        print(f"BTC: ${price:,.2f} | Change: {change_pct:+.3f}% | {now.strftime('%H:%M:%S')}", end="\r")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nStopped.")
