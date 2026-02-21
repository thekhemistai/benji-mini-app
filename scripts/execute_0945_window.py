#!/usr/bin/env python3
"""
Automated execution for 09:45 UTC window
Silent execution - logs to file only
"""

import asyncio
import json
import time
import sys
sys.path.insert(0, '/Users/thekhemist/.openclaw/workspace/scripts')

from polymarket_ui_bridge import PolymarketUIBridge
from datetime import datetime
import requests

START_PRICE = 68135
WINDOW_CLOSE_TS = 1771605900
MARKET_SLUG = "btc-updown-15m-1771605900"

async def get_btc_price():
    """Fetch current BTC price"""
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=5)
        return r.json()['bitcoin']['usd']
    except:
        return None

async def main():
    bridge = PolymarketUIBridge()
    log_file = "/Users/thekhemist/.openclaw/workspace/memory/trading/sessions/browser-bridge-2026-02-20.jsonl"
    
    try:
        # Initialize and navigate
        await bridge.initialize()
        await bridge.navigate_to_market(MARKET_SLUG)
        
        # Wait until 5 seconds before close
        now = datetime.utcnow()
        target = datetime.utcfromtimestamp(WINDOW_CLOSE_TS)
        wait_secs = (target - now).total_seconds() - 5
        
        if wait_secs > 0:
            await asyncio.sleep(wait_secs)
        
        # Rapid refresh at close
        for i in range(5):
            prices = await bridge.refresh_and_check()
            await asyncio.sleep(1)
        
        # Window closed - get resolution price
        end_price = await get_btc_price()
        
        # Determine outcome
        if end_price and end_price >= START_PRICE:
            side = "up"
            outcome = "UP"
        else:
            side = "down"
            outcome = "DOWN"
        
        # Execute trade
        result = await bridge.execute_buy(side, size_usd=10.0)
        
        # Log result
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "window": "09:30-09:45 UTC",
            "market": MARKET_SLUG,
            "start_price": START_PRICE,
            "end_price": end_price,
            "outcome": outcome,
            "side_executed": side,
            "execution_result": result,
            "mode": "browser_automation_test"
        }
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"✅ Execution complete: {outcome}")
        print(f"   Start: ${START_PRICE}")
        print(f"   End: ${end_price}")
        print(f"   Result: {result}")
        
    except Exception as e:
        error_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "market": MARKET_SLUG
        }
        with open(log_file, 'a') as f:
            f.write(json.dumps(error_entry) + '\n')
        print(f"❌ Error: {e}")
        
    finally:
        await bridge.close()

if __name__ == "__main__":
    asyncio.run(main())
