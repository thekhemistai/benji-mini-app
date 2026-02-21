#!/usr/bin/env python3
"""
Live BTC Arb Trade - FIXED (Browser-based with specific market targeting)
Targets exact market URLs with timestamps
"""

import asyncio
import time
import requests
from datetime import datetime
from playwright.async_api import async_playwright

def get_btc_price():
    try:
        r = requests.get(
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
            timeout=2
        )
        return r.json()['bitcoin']['usd']
    except:
        return None

def get_current_timestamp():
    """Get current Unix timestamp for market URL"""
    return int(time.time())

def calculate_window_timestamps():
    """Calculate BTC 5m window start/end timestamps"""
    now = datetime.utcnow()
    # BTC windows are at :00, :05, :10, :15, :20, :25, :30, :35, :40, :45, :50, :55
    minute = now.minute
    window_minute = (minute // 5) * 5
    
    # Current window start
    window_start = now.replace(minute=window_minute, second=0, microsecond=0)
    window_start_ts = int(window_start.timestamp())
    
    # Next window start (5 min later)
    window_end_ts = window_start_ts + 300
    
    return window_start_ts, window_end_ts

async def execute_browser_trade(winner: str, amount: int = 5):
    """Execute trade via browser with specific market URL"""
    
    # Calculate the market URL for the window that just closed
    _, window_ts = calculate_window_timestamps()
    
    # Build specific market URL
    market_url = f"https://polymarket.com/event/btc-updown-5m-{window_ts}"
    
    print(f"🌐 Targeting market: {market_url}")
    print(f"   Winner: {winner.upper()}")
    print(f"   Amount: ${amount}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Load specific market
        await page.goto(market_url, wait_until='domcontentloaded')
        await asyncio.sleep(2)
        
        # Screenshot to verify we're on right market
        await page.screenshot(path=f'market_{window_ts}.png')
        print(f"   📸 Screenshot saved")
        
        # Check if market shows as resolved/closed
        content = await page.content()
        if 'closed' in content.lower() or 'resolved' in content.lower():
            print("   ✅ Market appears resolved")
        
        # Try to find and click winner button
        try:
            # Look for buttons containing UP or DOWN
            buttons = await page.query_selector_all('button')
            for btn in buttons:
                text = await btn.inner_text()
                if winner.upper() in text and len(text) < 15:
                    print(f"   🖱️  Clicking {winner.upper()}...")
                    await btn.click()
                    await asyncio.sleep(1)
                    break
            
            # Look for amount input
            inputs = await page.query_selector_all('input')
            for inp in inputs:
                placeholder = await inp.get_attribute('placeholder')
                if placeholder and ('amount' in placeholder.lower() or 'size' in placeholder.lower()):
                    await inp.fill(str(amount))
                    print(f"   💰 Filled amount: ${amount}")
                    await asyncio.sleep(0.5)
                    break
            
            # Click Buy
            buy_buttons = await page.query_selector_all('button')
            for btn in buy_buttons:
                text = await btn.inner_text()
                if 'buy' in text.lower():
                    print("   🖱️  Clicking Buy...")
                    await btn.click()
                    await asyncio.sleep(2)
                    break
            
            # Screenshot after trade attempt
            await page.screenshot(path=f'trade_attempt_{window_ts}.png')
            print("   📸 Trade attempt captured")
            
            print("\n⚠️  WALLET CONFIRMATION REQUIRED")
            print("   If wallet popup appeared, please confirm manually")
            print("   Trade will complete on-chain after confirmation")
            
            # Wait for manual confirmation
            await asyncio.sleep(10)
            
        except Exception as e:
            print(f"   ❌ Browser error: {e}")
        
        await browser.close()
    
    return window_ts

async def main():
    print(f"🔥 FIXED BTC ARB - {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    print("Method: Browser with specific market URL targeting")
    print("="*60)
    
    # STEP 1: Record start price
    print("\n📊 Recording start price...")
    start_price = get_btc_price()
    if not start_price:
        print("❌ Failed to get price")
        return
    print(f"✅ Start: ${start_price}")
    
    # Show window timing
    window_start, window_end = calculate_window_timestamps()
    print(f"   Current window: {window_start} → {window_end}")
    
    # STEP 2: Wait for window close
    print("\n⏳ Waiting for window close...")
    for i in range(5, 0, -1):
        print(f"   {i} min...", end='\r')
        time.sleep(60)
    print("\n")
    
    # STEP 3: Get end price
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
    
    # STEP 4: Execute via browser
    print(f"\n💰 Executing trade...")
    window_ts = await execute_browser_trade(winner, 5)
    
    # Log
    print("\n📝 Logging...")
    trade_log = f"""
Trade Attempt - {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Winner: {winner.upper()}
- Change: ${change:.2f}
- Market TS: {window_ts}
- Method: Browser (specific URL)
"""
    with open('trade_log_fixed.txt', 'a') as f:
        f.write(trade_log)
    print("✅ Complete")

if __name__ == "__main__":
    asyncio.run(main())
