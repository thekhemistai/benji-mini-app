#!/usr/bin/env python3
"""
Live BTC Arb Trade - FULLY AUTOMATED via Bankr CLI
"""

import subprocess
import time
import requests
from datetime import datetime

def get_btc_price():
    try:
        r = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=5)
        return r.json()['bitcoin']['usd']
    except:
        return None

def execute_bankr_trade(side: str, amount: int = 5):
    """Execute trade via Bankr CLI"""
    try:
        # Use Bankr CLI to place the trade
        cmd = f'npx bankr "buy {amount} dollars of {side} on BTC updown 5m"'
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"

def main():
    print(f"🔥 FULLY AUTOMATED TRADE - {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    
    # STEP 1: Get start price
    print("\n📊 Getting start price...")
    start_price = get_btc_price()
    if not start_price:
        print("❌ Failed to get price")
        return
    print(f"✅ Start price: ${start_price}")
    
    # STEP 2: Wait for window close
    print("\n⏳ Waiting 5 minutes for window close...")
    for i in range(5, 0, -1):
        print(f"   {i} min remaining...", end='\r')
        time.sleep(60)
    print("\n")
    
    # STEP 3: Get end price
    end_price = get_btc_price()
    if not end_price:
        print("❌ Failed to get end price")
        return
    
    # Determine winner
    if end_price >= start_price:
        winner = "UP"
        change = end_price - start_price
    else:
        winner = "DOWN"
        change = start_price - end_price
    
    print(f"\n🏆 WINNER: {winner}")
    print(f"   Start: ${start_price}")
    print(f"   End: ${end_price}")
    print(f"   Change: ${change:.2f}")
    
    # STEP 4: Execute via Bankr CLI
    print(f"\n💰 Executing {winner} trade via Bankr CLI...")
    print("   Amount: $5")
    
    result = execute_bankr_trade(winner.lower(), 5)
    print(f"\n📤 Bankr Response:\n{result}")
    
    # STEP 5: Verify position
    print("\n🔍 Verifying position...")
    time.sleep(5)
    verify = subprocess.run(
        'npx bankr "show my polymarket positions"',
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    print(f"\n📊 Positions:\n{verify.stdout}")
    
    # Log result
    print("\n📝 Logging...")
    trade_log = f"""
Trade Attempt - {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Start: ${start_price}
- End: ${end_price}
- Winner: {winner}
- Change: ${change:.2f}
- Bankr Result: {result[:200]}...
"""
    with open('trade_log.txt', 'a') as f:
        f.write(trade_log)
    print("✅ Complete")

if __name__ == "__main__":
    main()
