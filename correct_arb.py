#!/usr/bin/env python3
"""
Polymarket 15m Arbitrage - Correct Strategy
Wait until final moments, bet when outcome is certain.
"""

import time
import requests
from datetime import datetime, timedelta

# CONFIG
MARKET_DURATION = 15 * 60  # 15 minutes in seconds
BET_WINDOW = 45            # Bet in final 45 seconds only
MOVE_THRESHOLD = 0.15      # Price must have moved 0.15%+ 
CHECK_INTERVAL = 2         # Check every 2 seconds

# Track
market_start = None        # When current 15m window started
start_price = None         # Price at window start


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


def get_market_time_remaining():
    """
    Get time remaining in current 15m window.
    Returns seconds remaining, or None if no active market.
    """
    # This would check Polymarket API for active 15m market
    # For now, we'll simulate based on system time aligned to 15m intervals
    now = datetime.now()
    # 15m markets typically start at :00, :15, :30, :45
    minute = now.minute
    second = now.second
    
    # Find next 15m boundary
    if minute < 15:
        target = 15
    elif minute < 30:
        target = 30
    elif minute < 45:
        target = 45
    else:
        target = 60  # Next hour
    
    remaining_mins = target - minute - 1
    remaining_secs = 60 - second
    total_remaining = remaining_mins * 60 + remaining_secs
    
    return total_remaining


def check_active_market():
    """Check if there's an active 15m BTC market right now."""
    # Would query Polymarket Gamma API
    # For now assume markets run :00-:15, :15-:30, :30-:45, :45-:00
    now = datetime.now()
    return now.minute % 15 < 15  # Always true during a 15m window


def main():
    global market_start, start_price
    
    print("=" * 60)
    print("⚡ POLYMARKET 15M ARBITRAGE")
    print("Bet ONLY in final 45 seconds when outcome is certain")
    print("=" * 60)
    print(f"\nConfig:")
    print(f"  Bet window: Final {BET_WINDOW} seconds only")
    print(f"  Move threshold: {MOVE_THRESHOLD}%")
    print(f"  Check interval: {CHECK_INTERVAL}s")
    print("\nCtrl+C to stop\n")
    
    bet_made = False
    
    while True:
        now = datetime.now()
        
        # Check if we're in a 15m market window
        if not check_active_market():
            print(f"⏳ No active 15m market | {now.strftime('%H:%M:%S')}", end="\r")
            time.sleep(CHECK_INTERVAL)
            continue
        
        # Get time remaining in window
        time_left = get_market_time_remaining()
        
        # Get current price
        current_price = get_btc_price()
        
        if not current_price:
            print("⚠️  Price fetch failed, retrying...")
            time.sleep(CHECK_INTERVAL)
            continue
        
        # Track start price at beginning of window
        if time_left > 14 * 60:  # First minute of window
            start_price = current_price
            market_start = now
            bet_made = False
        
        # Calculate move from start
        if start_price:
            move_pct = ((current_price - start_price) / start_price) * 100
        else:
            move_pct = 0
        
        # LOGIC: Only bet in final window with clear direction
        in_bet_window = time_left <= BET_WINDOW
        clear_direction = abs(move_pct) >= MOVE_THRESHOLD
        
        if in_bet_window and clear_direction and not bet_made:
            direction = "UP" if move_pct > 0 else "DOWN"
            
            print(f"\n{'='*60}")
            print(f"🎯 BET TRIGGERED!")
            print(f"{'='*60}")
            print(f"Time remaining: {time_left}s")
            print(f"Start price: ${start_price:,.2f}")
            print(f"Current price: ${current_price:,.2f}")
            print(f"Move: {move_pct:+.3f}%")
            print(f"Direction: {direction}")
            print(f"\n🔥 ACTION: Bet {direction} on Polymarket NOW")
            print(f"   Oracle will resolve in {time_left}s")
            print(f"   Outcome is virtually certain - seize it!")
            print(f"{'='*60}\n")
            
            bet_made = True
            
            # Here: Execute trade via Bankr or CLOB API
            # For now just log it
            
        elif in_bet_window and not clear_direction:
            # In final window but move is too small - skip
            print(f"⏱️  FINAL {time_left}s | ${current_price:,.2f} | Move: {move_pct:+.3f}% | TOO CLOSE TO CALL", end="\r")
            
        elif in_bet_window and bet_made:
            # Already bet, waiting for resolution
            print(f"⏱️  FINAL {time_left}s | ${current_price:,.2f} | BET PLACED - WAITING", end="\r")
            
        else:
            # Normal monitoring
            print(f"🕐 {time_left//60}m{time_left%60}s left | ${current_price:,.2f} | Move: {move_pct:+.3f}% | Watching...", end="\r")
        
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Stopped.")
