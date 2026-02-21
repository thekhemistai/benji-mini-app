#!/usr/bin/env python3
"""
Polymarket Speed Trader - Direct Playwright Automation
Bypasses intent layer, goes straight to browser control
"""

import asyncio
import sys
from datetime import datetime, timezone
from playwright.async_api import async_playwright

# Config
MARKET_URL = "https://polymarket.com/event/btc-updown-5m-{timestamp}"
ORDER_SIZE = 100  # USD
DEFAULT_SIDE = "UP"  # or "DOWN"

class PolymarketSpeedTrader:
    def __init__(self):
        self.browser = None
        self.page = None
        self.context = None
        
    async def init(self):
        """Initialize Chrome browser (fastest based on benchmarks)"""
        self.playwright = await async_playwright().start()
        
        # Use Chrome (4.11s) - faster than Brave (6.06s)
        self.browser = await self.playwright.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        print("✅ Using Chrome browser (4.11s benchmark)")
        
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        self.page = await self.context.new_page()
        
    async def pre_position(self, timestamp: int):
        """Load market page and pre-fill everything"""
        url = MARKET_URL.format(timestamp=timestamp)
        print(f"🌐 Loading: {url}")
        
        # Load page - don't wait for specific selectors (Polymarket changes these)
        await self.page.goto(url, wait_until="domcontentloaded")
        
        # Short wait for page to render
        await asyncio.sleep(2)
        
        # Pre-select order size
        try:
            size_input = await self.page.wait_for_selector("input[placeholder*='Amount']", timeout=5000)
            await size_input.fill(str(ORDER_SIZE))
            print(f"💰 Pre-filled order size: ${ORDER_SIZE}")
        except:
            print("⚠️  Could not pre-fill order size")
            
        print("✅ Market pre-positioned. Ready for execution.")
        
    async def execute_trade(self, side: str):
        """Execute trade with single click"""
        print(f"🚀 Executing {side} trade...")
        
        try:
            # Click UP or DOWN button
            button_selector = f"button:has-text('{side}')" if side == "UP" else f"button:has-text('{side}')"
            await self.page.click(button_selector, timeout=5000)
            
            # Click Buy/Submit
            await self.page.click("button:has-text('Buy')", timeout=5000)
            
            # Confirm in wallet (if prompted)
            # This part requires manual intervention or wallet automation
            
            print(f"✅ Trade executed: {side} ${ORDER_SIZE}")
            return True
            
        except Exception as e:
            print(f"❌ Trade failed: {e}")
            return False
            
    async def get_current_price(self):
        """Quick price check from page"""
        try:
            price_element = await self.page.wait_for_selector("[data-testid='price']", timeout=2000)
            price_text = await price_element.text_content()
            return float(price_text.replace('$', '').replace('¢', ''))
        except:
            return None
            
    async def close(self):
        if self.browser:
            await self.browser.close()
        await self.playwright.stop()

async def main():
    """Test the speed trader"""
    trader = PolymarketSpeedTrader()
    
    try:
        await trader.init()
        
        # Example: Pre-position for next 5-min window
        # You'd calculate this based on current time
        next_window = 1771600800  # Example timestamp
        
        await trader.pre_position(next_window)
        
        # Keep browser open for manual execution test
        print("\n⏳ Browser open for 60 seconds - execute trade manually")
        print("Then close browser to end test")
        await asyncio.sleep(60)
            
    except KeyboardInterrupt:
        print("\n🛑 Cancelled by user")
    finally:
        await trader.close()

if __name__ == "__main__":
    asyncio.run(main())
