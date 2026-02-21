#!/usr/bin/env python3
"""
Live BTC Arb Trade - OPTIMIZED Bankr CLI
Pre-staged commands, minimal latency
"""

import subprocess
import time
import requests
import os
from datetime import datetime
import threading

def get_btc_price():
    """Fast price check"""
    try:
        r = requests.get(
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
            timeout=2
        )
        return r.json()['bitcoin']['usd']
    except:
        return None

def prepare_bankr_command(side: str, amount: int = 5):
    """Pre-build the Bankr command string"""
    return f'/opt/homebrew/bin/npx bankr "buy {amount} dollars of {side} on BTC updown 5m"'

def execute_bankr_trade(cmd: str, timeout: int = 30):
    """Execute Bankr CLI with optimized settings"""
    try:
        # Command already has full path from prepare_bankr_command
        env = os.environ.copy()
        env['NODE_OPTIONS'] = '--max-old-space-size=512'
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Timeout', 'timeout': True}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    print(f"⚡ OPTIMIZED BANKR TRADE - {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    print("Strategy: Pre-staged commands, 30s timeout, fast execution")
    print("="*60)
    
    # STEP 1: Get start price
    print("\n📊 Recording start price...")
    start_price = get_btc_price()
    if not start_price:
        print("❌ Failed to get price")
        return
    print(f"✅ Start: ${start_price}")
    
    # Pre-build both commands (saves time later)
    up_cmd = prepare_bankr_command("up", 5)
    down_cmd = prepare_bankr_command("down", 5)
    
    # STEP 2: Wait for window close
    print("\n⏳ Waiting 5 minutes...")
    print("Commands pre-built: UP and DOWN")
    
    for i in range(5, 0, -1):
        print(f"   {i} min...", end='\r')
        time.sleep(60)
    print("\n")
    
    # STEP 3: Get end price and determine winner
    print("📊 Getting end price...")
    end_price = get_btc_price()
    if not end_price:
        print("❌ Failed")
        return
    
    winner = "up" if end_price >= start_price else "down"
    change = abs(end_price - start_price)
    
    print(f"\n🏆 WINNER: {winner.upper()}")
    print(f"   Start: ${start_price}")
    print(f"   End: ${end_price}")
    print(f"   Change: ${change:.2f}")
    
    # STEP 4: Execute pre-built command
    cmd = up_cmd if winner == "up" else down_cmd
    print(f"\n💰 Executing: {cmd}")
    print("   Timeout: 30 seconds")
    
    exec_start = time.time()
    result = execute_bankr_trade(cmd, timeout=30)
    exec_time = time.time() - exec_start
    
    print(f"\n⏱️  Execution time: {exec_time:.1f}s")
    
    if result.get('timeout'):
        print("⚠️  TIMEOUT - Trade may have been submitted but confirmation failed")
        print("   Check positions manually: npx bankr 'show my polymarket positions'")
    elif result['success']:
        print("✅ Trade executed!")
        print(f"   Output: {result['stdout'][:300]}")
    else:
        print(f"❌ Error: {result.get('stderr', result.get('error', 'Unknown'))[:300]}")
    
    # STEP 5: Verify
    print("\n🔍 Verifying position...")
    time.sleep(3)
    verify = subprocess.run(
        '/opt/homebrew/bin/npx bankr "show my polymarket positions"',
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if 'no open' in verify.stdout.lower():
        print("   ❌ No position found")
    else:
        print(f"   ✅ Position found:\n{verify.stdout[:500]}")
    
    # Log
    trade_log = f"""
Trade - {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Winner: {winner.upper()}
- Change: ${change:.2f}
- Exec Time: {exec_time:.1f}s
- Timeout: {result.get('timeout', False)}
- Success: {result['success']}
"""
    with open('trade_log.txt', 'a') as f:
        f.write(trade_log)
    
    print("\n✅ Complete")

if __name__ == "__main__":
    main()
