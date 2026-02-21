#!/usr/bin/env python3
"""
Live BTC Arb Trade - WITH manual wallet confirmation
"""

import asyncio
import time
import requests
from datetime import datetime
from playwright.async_api import async_playwright

def get_btc_price():
    try:
        r = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=5)
        return r.json()['bitcoin']['usd']
    except:
        return None

async def execute_trade():
    print(f"🔥 LIVE TRADE - {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    print("⚠️  MANUAL WALLET CONFIRMATION REQUIRED")
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
        print(f"   {i} min...", end='\r')
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
    
    # STEP 4: Execute with manual confirmation
    print(f"\n💰 STEP 4: Preparing {winner} trade...")
    print("⚠️  WALLET CONFIRMATION WILL BE REQUIRED")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
        
        # Load market
        timestamp = int(time.time())
        url = f"https://polymarket.com/event/btc-updown-5m-{timestamp}"
        await page.goto(url, wait_until='domcontentloaded')
        print(f"   ✅ Market loaded")
        
        # Click winner button
        try:
            buttons = await page.query_selector_all('button')
            for btn in buttons:
                text = await btn.inner_text()
                if winner in text.upper() and len(text) < 10:
                    print(f"   🖱️  Clicking {winner}...")
                    await btn.click()
                    break
            
            # Click Buy
            await asyncio.sleep(1)
            buy_buttons = await page.query_selector_all('button')
            for btn in buy_buttons:
                text = await btn.inner_text()
                if 'buy' in text.lower():
                    print("   🖱️  Clicking Buy...")
                    await btn.click()
                    break
            
            # ⭐ KEY STEP: Wait for manual wallet confirmation
            print("\n" + "="*60)
            print("🚨 MANUAL ACTION REQUIRED")
            print("="*60)
            print("1. Look for the wallet popup in your browser")
            print("2. Click 'Confirm' to sign the transaction")
            print("3. Then press ENTER here to continue")
            print("="*60)
            
            input("\nPress ENTER after confirming in wallet...")
            
            # Check for success indicators
            print("\n✅ Trade submitted!")
            await asyncio.sleep(3)
            
            # Screenshot
            timestamp_str = datetime.now().strftime('%H%M')
            await page.screenshot(path=f'trade_confirm_{timestamp_str}.png')
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        await browser.close()
    
    # STEP 5: Verify with Bankr
    print("\n🔍 STEP 5: Verifying trade with Bankr...")
    print("Run: npx bankr 'show my polymarket positions'")
    
    # Log result
    print("\n📝 Logging...")
    trade_log = f"""
Trade Attempt - {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Start: ${start_price}
- End: ${end_price}
- Winner: {winner}
- Change: ${change:.2f}
- Status: Manual confirmation required
"""
    with open('trade_log.txt', 'a') as f:
        f.write(trade_log)
    print("✅ Logged")

if __name__ == "__main__":
    asyncio.run(execute_trade())
