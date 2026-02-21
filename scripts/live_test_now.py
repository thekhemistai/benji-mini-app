#!/usr/bin/env python3
"""
LIVE TEST - Cross-Market/Hourly Arbitrage
Execute RIGHT NOW on next hourly window
"""

import subprocess
import time
import requests
from datetime import datetime, timezone

def get_btc_price():
    try:
        r = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=5)
        return r.json()['bitcoin']['usd']
    except:
        return None

def get_next_hour_timestamp():
    """Get timestamp for next hour window"""
    now = datetime.now(timezone.utc)
    next_hour = now.replace(minute=0, second=0, microsecond=0)
    if now.minute >= 50:  # If close to next hour, use that
        next_hour = next_hour.replace(hour=(now.hour + 1) % 24)
    return int(next_hour.timestamp())

def main():
    print("="*70)
    print("LIVE CROSS-MARKET TEST - RIGHT NOW")
    print("="*70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    # Get current BTC price
    start_price = get_btc_price()
    print(f"\n📊 BTC Start Price: ${start_price:,}")
    
    # Calculate window
    window_ts = get_next_hour_timestamp()
    window_time = datetime.fromtimestamp(window_ts, tz=timezone.utc)
    print(f"⏳ Next Window: {window_time.strftime('%H:%M')} UTC")
    
    # Wait for window (simplified - just wait 5 min for test)
    print("\n⏳ Waiting 5 minutes for window...")
    for i in range(5, 0, -1):
        print(f"   {i} min remaining...", end='\r')
        time.sleep(60)
    print("\n")
    
    # Check end price
    end_price = get_btc_price()
    winner = "UP" if end_price >= start_price else "DOWN"
    
    print(f"📊 BTC End Price: ${end_price:,}")
    print(f"🏆 Winner: {winner}")
    print(f"   Change: ${abs(end_price - start_price):,.2f}")
    
    # Generate Bankr command
    print("\n💰 BANKR EXECUTION COMMAND:")
    print("-" * 70)
    cmd = f'npx bankr "buy 5 dollars of {winner} on bitcoin up or down hourly"'
    print(f"   {cmd}")
    print("-" * 70)
    
    # Ask for confirmation
    print("\n⚡ This is a REAL trade command.")
    print("Run it manually if you want to execute.")
    
    # Log paper trade
    log = f"""
Paper Trade - {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Strategy: Hourly BTC direction
- Start: ${start_price:,}
- End: ${end_price:,}
- Winner: {winner}
- Command: {cmd}
- Status: PAPER (not executed)
"""
    with open('live_test_paper_trades.txt', 'a') as f:
        f.write(log)
    
    print("\n✅ Paper trade logged to live_test_paper_trades.txt")

if __name__ == "__main__":
    main()
