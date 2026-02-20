#!/usr/bin/env python3
"""
Live BTC Arb Trade - Full execution with price tracking
"""

import asyncio
import time
import requests
from datetime import datetime
from playwright.async_api import async_playwright

# Get BTC price from CoinGecko
def get_btc_price():
    try:
        r = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=5)
        return r.json()['bitcoin']['usd']
    except Exception as e:
        print(f"Price fetch error: {e}")
        return None

async def execute_trade():
    print(f"🔥 LIVE TRADE - {datetime.now().strftime('%H:%M:%S')}")
    print("="*50)
    
    # STEP 1: Record start price
    print("\n📊 STEP 1: Recording start price...")
    start_price = get_btc_price()
    if not start_price:
        print("❌ Failed to get start price. Aborting.")
        return
    print(f"✅ Start price: ${start_price}")
    
    # STEP 2: Wait for window close (5 minutes)
    print("\n⏳ STEP 2: Waiting 5 minutes for window close...")
    print("Browser will open at window close for immediate execution")
    
    # Wait 5 minutes
    for i in range(5, 0, -1):
        print(f"   {i} minutes remaining...", end='\r')
        time.sleep(60)
    print("\n")
    
    # STEP 3: Get end price immediately
    print("\n📊 STEP 3: Getting end price...")
    end_price = get_btc_price()
    if not end_price:
        print("❌ Failed to get end price. Aborting.")
        return
    print(f"✅ End price: ${end_price}")
    
    # STEP 4: Determine winner
    print("\n🏆 STEP 4: Determining winner...")
    if end_price >= start_price:
        winner = "UP"
        change = end_price - start_price
    else:
        winner = "DOWN"
        change = start_price - end_price
    
    print(f"   Start: ${start_price}")
    print(f"   End: ${end_price}")
    print(f"   Change: ${change:.2f}")
    print(f"   🎯 Winner: {winner}")
    
    # STEP 5: Execute trade
    print(f"\n💰 STEP 5: Executing {winner} trade...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Load current BTC market
        timestamp = int(time.time())
        url = f"https://polymarket.com/event/btc-updown-5m-{timestamp}"
        
        print(f"   Loading: {url}")
        await page.goto(url, wait_until='domcontentloaded')
        
        # Screenshot before trade
        await page.screenshot(path=f'trade_before_{datetime.now().strftime("%H%M")}.png')
        print("   📸 Screenshot saved")
        
        # Look for winner button
        try:
            # Try to find UP or DOWN button
            buttons = await page.query_selector_all('button')
            for btn in buttons:
                text = await btn.inner_text()
                if winner in text.upper():
                    print(f"   🖱️  Clicking {winner} button...")
                    await btn.click()
                    print(f"   ✅ Clicked {winner}")
                    break
            
            # Look for Buy/Submit button
            await asyncio.sleep(1)
            buy_buttons = await page.query_selector_all('button')
            for btn in buy_buttons:
                text = await btn.inner_text()
                if 'buy' in text.lower() or 'submit' in text.lower():
                    print("   🖱️  Clicking Buy...")
                    await btn.click()
                    print("   ✅ Buy clicked")
                    break
            
            # Wait for wallet confirmation
            print("\n⏳ Waiting 10s for wallet confirmation...")
            await asyncio.sleep(10)
            
            # Screenshot after
            await page.screenshot(path=f'trade_after_{datetime.now().strftime("%H%M")}.png')
            
        except Exception as e:
            print(f"   ❌ Trade error: {e}")
        
        await browser.close()
    
    # STEP 6: Log result
    print("\n📝 STEP 6: Logging result...")
    trade_log = f"""
Trade Log - {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Start Price: ${start_price}
- End Price: ${end_price}
- Winner: {winner}
- Change: ${change:.2f}
"""
    with open('trade_log.txt', 'a') as f:
        f.write(trade_log)
    print("   ✅ Logged to trade_log.txt")
    
    print("\n" + "="*50)
    print("TRADE COMPLETE")

if __name__ == "__main__":
    asyncio.run(execute_trade())
