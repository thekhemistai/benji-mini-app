#!/usr/bin/env python3
"""
Polymarket Browser Automation Bridge
Pre-positions browser on active market, auto-refreshes at resolution, minimizes click-path
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

# Playwright for browser automation
try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    print("Installing playwright...")
    import subprocess
    subprocess.run(["pip", "install", "playwright"], check=True)
    subprocess.run(["playwright", "install", "chromium"], check=True)
    from playwright.async_api import async_playwright, Page, Browser


@dataclass
class MarketWindow:
    """BTC up/down market window configuration"""
    slug: str
    start_time: datetime
    end_time: datetime
    timeframe: str  # "5m", "15m", "1h", "4h"
    resolution_source: str  # "chainlink" or "binance"
    start_price: Optional[float] = None


class PolymarketUIBridge:
    """
    Browser automation bridge for Polymarket trading.
    Reduces UI latency by pre-positioning and automating clicks.
    """
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.active_market: Optional[MarketWindow] = None
        self.is_positioned = False
        
    async def initialize(self):
        """Launch browser and prepare page"""
        playwright = await async_playwright().start()
        
        # Launch with args to reduce detection
        self.browser = await playwright.chromium.launch(
            headless=False,  # Visible for monitoring, set True for headless
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )
        
        # Create context with realistic viewport
        context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        )
        
        self.page = await context.new_page()
        print("✅ Browser initialized")
        
    async def navigate_to_market(self, market_slug: str):
        """Navigate to specific market page"""
        if not self.page:
            await self.initialize()
            
        url = f"https://polymarket.com/event/{market_slug}"
        print(f"🌐 Navigating to: {url}")
        
        await self.page.goto(url, wait_until='networkidle')
        
        # Wait for price elements to load
        try:
            await self.page.wait_for_selector('[data-testid="outcome-price"]', timeout=10000)
            print("✅ Market page loaded, prices visible")
            self.is_positioned = True
        except:
            print("⚠️ Price elements not detected, but page loaded")
            
    async def refresh_and_check(self) -> dict:
        """Refresh page and extract current prices"""
        if not self.page:
            return {'error': 'Browser not initialized'}
            
        print("🔄 Refreshing...")
        start = time.time()
        await self.page.reload(wait_until='networkidle')
        load_time = time.time() - start
        
        # Extract prices from the DOM
        prices = await self._extract_prices()
        prices['load_time_seconds'] = round(load_time, 2)
        
        return prices
        
    async def _extract_prices(self) -> dict:
        """Extract YES/NO prices from the market page"""
        try:
            # Try multiple selectors for price extraction
            selectors = [
                '[data-testid="outcome-price"]',
                '.text-2xl.font-semibold',
                '[class*="price"]',
                'button span[class*="text"]',
            ]
            
            prices = []
            for selector in selectors:
                elements = await self.page.query_selector_all(selector)
                for el in elements:
                    text = await el.inner_text()
                    if '¢' in text or '$' in text or '%' in text:
                        prices.append(text.strip())
                        
            return {
                'prices_found': prices,
                'timestamp': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            return {'error': str(e), 'timestamp': datetime.utcnow().isoformat()}
            
    async def execute_buy(self, side: str, size_usd: float = 10.0) -> dict:
        """
        Execute buy order on pre-positioned page
        side: "yes" or "no"
        """
        if not self.page or not self.is_positioned:
            return {'error': 'Not positioned on market page'}
            
        try:
            print(f"🎯 Executing {side.upper()} buy for ${size_usd}")
            start = time.time()
            
            # Click the outcome button (YES or NO)
            outcome_selector = f'button:has-text("{side.upper()}")'
            await self.page.click(outcome_selector)
            print(f"  ✓ Selected {side.upper()}")
            
            # Enter size
            size_input = await self.page.wait_for_selector('input[placeholder*="Amount"]')
            await size_input.fill(str(size_usd))
            print(f"  ✓ Entered ${size_usd}")
            
            # Click buy button
            buy_button = await self.page.wait_for_selector('button:has-text("Buy")')
            await buy_button.click()
            print(f"  ✓ Clicked Buy")
            
            # Confirm in wallet (manual step or auto-confirm if wallet connected)
            # This will vary based on wallet setup (MetaMask, Rainbow, etc.)
            
            execution_time = time.time() - start
            
            return {
                'status': 'submitted',
                'side': side,
                'size': size_usd,
                'execution_time_seconds': round(execution_time, 2),
                'timestamp': datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
            }
            
    async def monitor_and_execute(self, market: MarketWindow, side: str):
        """
        Full flow: Monitor until window close, refresh, check price, execute
        """
        print(f"\n🔔 Monitoring {market.timeframe} window")
        print(f"   Closes: {market.end_time.strftime('%H:%M:%S UTC')}")
        print(f"   Side to execute: {side.upper()}")
        
        # Navigate to market
        await self.navigate_to_market(market.slug)
        
        # Wait until 5 seconds before close
        now = datetime.utcnow()
        time_until_close = (market.end_time - now).total_seconds()
        
        if time_until_close > 5:
            wait_seconds = time_until_close - 5
            print(f"⏳ Waiting {wait_seconds:.0f}s until 5s before close...")
            await asyncio.sleep(wait_seconds)
            
        # Rapid refresh cycle around close time
        print("⚡ Entering rapid refresh cycle...")
        for i in range(10):  # 10 refreshes over ~20 seconds
            prices = await self.refresh_and_check()
            print(f"  Refresh {i+1}: {prices}")
            
            # Check if prices indicate opportunity (e.g., winning side < 0.90)
            # TODO: Add logic to auto-detect edge
            
            await asyncio.sleep(2)
            
        # Execute trade
        result = await self.execute_buy(side)
        print(f"\n📊 Execution result: {result}")
        
        return result
        
    async def close(self):
        """Clean up browser"""
        if self.browser:
            await self.browser.close()
            print("🛑 Browser closed")


async def quick_execute(market_slug: str, side: str, size: float = 10.0):
    """
    Standalone quick execution function
    Usage: quick_execute("btc-updown-15m-123456", "up", 50)
    """
    bridge = PolymarketUIBridge()
    
    try:
        print(f"⚡ Quick Execute: {side.upper()} on {market_slug}")
        print(f"   Size: ${size}")
        print(f"   Time: {datetime.utcnow().strftime('%H:%M:%S.%f')[:-3]} UTC")
        print("")
        
        await bridge.initialize()
        await bridge.navigate_to_market(market_slug)
        
        # Single refresh to confirm prices
        print("🔄 Refreshing page...")
        prices = await bridge.refresh_and_check()
        print(f"   Current prices: {prices}")
        print("")
        
        # Execute immediately
        result = await bridge.execute_buy(side, size)
        
        print("")
        print("📊 EXECUTION RESULT")
        print("=" * 50)
        for key, value in result.items():
            print(f"   {key}: {value}")
        print("=" * 50)
        
        # Keep browser open briefly to confirm
        await asyncio.sleep(5)
        
    finally:
        await bridge.close()


# Example usage and test
async def test_bridge():
    """Test the browser bridge"""
    bridge = PolymarketUIBridge()
    
    # Example: Next 15m BTC market
    # In production, calculate from current time
    now = datetime.utcnow()
    window_end = now.replace(minute=(now.minute // 15 + 1) * 15 % 60, second=0, microsecond=0)
    if window_end <= now:
        window_end += timedelta(minutes=15)
        
    market = MarketWindow(
        slug="btc-updown-15m-1771580100",  # Example, update dynamically
        start_time=window_end - timedelta(minutes=15),
        end_time=window_end,
        timeframe="15m",
        resolution_source="chainlink"
    )
    
    try:
        await bridge.initialize()
        await bridge.navigate_to_market(market.slug)
        
        # Quick test: refresh and get prices
        prices = await bridge.refresh_and_check()
        print(f"\nCurrent prices: {prices}")
        
        # Wait for user input before closing
        input("\nPress Enter to close browser...")
        
    finally:
        await bridge.close()


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Polymarket Browser Automation Bridge')
    parser.add_argument('--position', metavar='SLUG', help='Navigate to specific market slug')
    parser.add_argument('--execute', metavar='SIDE', choices=['up', 'down'], help='Execute trade side')
    parser.add_argument('--size', type=float, default=10.0, help='Trade size in USD')
    
    args = parser.parse_args()
    
    if args.position:
        # Just position and wait
        bridge = PolymarketUIBridge()
        asyncio.run(bridge.navigate_to_market(args.position))
        print(f"✅ Positioned on {args.position}")
        print("Browser will remain open. Press Ctrl+C to close.")
        try:
            while True:
                asyncio.sleep(1)
        except KeyboardInterrupt:
            asyncio.run(bridge.close())
    elif args.execute:
        # Quick execute
        asyncio.run(quick_execute(args.position or "unknown", args.execute, args.size))
    else:
        # Default: test mode
        print("🧪 Polymarket Browser Automation Bridge (Test Mode)")
        print("=" * 50)
        print("\nUsage:")
        print("  python polymarket_ui_bridge.py --position btc-updown-15m-123456")
        print("  python polymarket_ui_bridge.py --position btc-updown-15m-123456 --execute up --size 50")
        print("\nRunning test mode...\n")
        asyncio.run(test_bridge())


if __name__ == "__main__":
    main()
