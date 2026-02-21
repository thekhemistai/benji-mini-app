#!/usr/bin/env python3
"""
ACCURATE Hourly BTC Arbitrage - Proper Window Timing
"""

import time
import requests
from datetime import datetime, timezone, timedelta

def get_btc_price():
    try:
        r = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=3)
        return r.json()['bitcoin']['usd']
    except:
        return None

def get_next_hour_close():
    """Get the exact time of the next hourly close"""
    now = datetime.now(timezone.utc)
    # Next hour mark
    next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    return next_hour

def wait_until(target_time):
    """Wait until specific time"""
    while True:
        now = datetime.now(timezone.utc)
        if now >= target_time:
            break
        remaining = (target_time - now).total_seconds()
        if remaining > 60:
            print(f"   {int(remaining/60)} min {int(remaining%60)} sec to window close...", end='\r')
        else:
            print(f"   {int(remaining)} seconds to window close...", end='\r')
        time.sleep(1)
    print("\n   🔔 WINDOW CLOSED!")

def main():
    print("="*70)
    print("ACCURATE HOURLY BTC ARBITRAGE")
    print("="*70)
    print(f"Current Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    # Get start price BEFORE window
    start_price = get_btc_price()
    print(f"\n📊 BTC Start Price (pre-window): ${start_price:,}")
    
    # Calculate exact window close
    window_close = get_next_hour_close()
    print(f"⏳ Window Closes At: {window_close.strftime('%H:%M:%S')} UTC")
    print(f"   (Waiting {int((window_close - datetime.now(timezone.utc)).total_seconds()/60)} minutes)")
    
    # Wait for ACTUAL window close
    print("\n⏳ Waiting for window close...")
    wait_until(window_close)
    
    # Check price IMMEDIATELY after close
    print("\n📊 Checking price immediately after close...")
    end_price = get_btc_price()
    
    # Determine winner
    winner = "UP" if end_price >= start_price else "DOWN"
    change = end_price - start_price
    
    print(f"\n🏆 RESULT:")
    print(f"   Start: ${start_price:,}")
    print(f"   End:   ${end_price:,}")
    print(f"   Change: ${change:+,.2f}")
    print(f"   Winner: {winner}")
    
    # Generate execution command
    print(f"\n💰 EXECUTE NOW (within 30 seconds):")
    print("-" * 70)
    print(f'   npx bankr "buy 5 dollars of {winner} on bitcoin up or down hourly"')
    print("-" * 70)
    print("\n⚡ EXECUTE BEFORE PRICE UPDATES!")
    
    # Log
    with open('accurate_trades.txt', 'a') as f:
        f.write(f"""
{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC
Window: Hourly BTC
Start: ${start_price:,}
End: ${end_price:,}
Winner: {winner}
Command: npx bankr "buy 5 dollars of {winner} on bitcoin up or down hourly"
""")

if __name__ == "__main__":
    main()
