#!/usr/bin/env python3
"""
Polymarket Trade Execution - Direct Playwright (Kelly Alternative)
No API keys needed - direct browser control
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

def get_window_timestamp():
    """Calculate current 5-min window timestamp"""
    now = datetime.utcnow()
    minute = now.minute
    window_minute = (minute // 5) * 5
    window_start = now.replace(minute=window_minute, second=0, microsecond=0)
    return int(window_start.timestamp())

async def execute_trade():
    print(f"🚀 KELLY-STYLE EXECUTION - {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    print("Method: Direct Playwright (no Kelly API needed)")
    print("="*60)
    
    # STEP 1: Get start price
    print("\n📊 Recording start price...")
    start_price = get_btc_price()
    if not start_price:
        print("❌ Failed")
        return
    print(f"✅ Start: ${start_price}")
    
    # Calculate market URL
    window_ts = get_window_timestamp()
    market_url = f"https://polymarket.com/event/btc-updown-5m-{window_ts}"
    print(f"   Market: {market_url}")
    
    # STEP 2: Wait for window close
    print("\n⏳ Waiting 5 minutes for window close...")
    for i in range(5, 0, -1):
        print(f"   {i} min...", end='\r')
        time.sleep(60)
    print("\n")
    
    # STEP 3: Determine winner
    end_price = get_btc_price()
    if not end_price:
        print("❌ Failed to get end price")
        return
    
    winner = "up" if end_price >= start_price else "down"
    change = abs(end_price - start_price)
    
    print(f"\n🏆 WINNER: {winner.upper()}")
    print(f"   Start: ${start_price}")
    print(f"   End: ${end_price}")
    print(f"   Change: ${change:.2f}")
    
    # STEP 4: Execute via Playwright (like Kelly but direct)
    print(f"\n💰 Executing trade...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Navigate to exact market
        print(f"   Loading: {market_url}")
        await page.goto(market_url, wait_until='domcontentloaded')
        await asyncio.sleep(2)
        
        # Screenshot for verification
        await page.screenshot(path=f'kelly_trade_{window_ts}_start.png')
        
        # Try to click winner
        try:
            buttons = await page.query_selector_all('button')
            for btn in buttons:
                text = await btn.inner_text()
                if winner.upper() in text and len(text) < 15:
                    print(f"   🖱️  Clicking {winner.upper()}...")
                    await btn.click()
                    await asyncio.sleep(1)
                    break
            
            # Fill amount
            inputs = await page.query_selector_all('input')
            for inp in inputs:
                placeholder = await inp.get_attribute('placeholder')
                if placeholder and ('amount' in placeholder.lower() or 'size' in placeholder.lower()):
                    await inp.fill('5')
                    print("   💰 Amount: $5")
                    break
            
            # Click Buy
            await asyncio.sleep(1)
            buttons = await page.query_selector_all('button')
            for btn in buttons:
                text = await btn.inner_text()
                if 'buy' in text.lower():
                    print("   🖱️  Clicking Buy...")
                    await btn.click()
                    await asyncio.sleep(2)
                    break
            
            # Screenshot after
            await page.screenshot(path=f'kelly_trade_{window_ts}_executed.png')
            
            print("\n" + "="*60)
            print("⚡ ACTION REQUIRED")
            print("="*60)
            print("If wallet popup appeared, click CONFIRM")
            print("Waiting 10 seconds...")
            print("="*60)
            
            await asyncio.sleep(10)
            
            # Final screenshot
            await page.screenshot(path=f'kelly_trade_{window_ts}_final.png')
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        await browser.close()
    
    # Log
    print("\n📝 Logging...")
    log = f"""
Kelly Trade - {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Winner: {winner.upper()}
- Change: ${change:.2f}
- Market: {window_ts}
- Status: Executed
"""
    with open('kelly_trades.txt', 'a') as f:
        f.write(log)
    print("✅ Complete")

if __name__ == "__main__":
    asyncio.run(execute_trade())
