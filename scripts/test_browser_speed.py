#!/usr/bin/env python3
"""
Quick browser speed test - Compare Brave vs Chrome launch times
"""

import asyncio
import time
from playwright.async_api import async_playwright

async def test_browser_speed(browser_name, executable_path=None):
    """Test how fast a browser loads Polymarket"""
    print(f"\n🧪 Testing {browser_name}...")
    
    start_total = time.time()
    
    async with async_playwright() as p:
        # Launch browser
        launch_start = time.time()
        if executable_path:
            browser = await p.chromium.launch(
                executable_path=executable_path,
                headless=False
            )
        else:
            browser = await p.chromium.launch(headless=False)
        launch_time = time.time() - launch_start
        
        # Create context and page
        context = await browser.new_context()
        page = await context.new_page()
        
        # Load Polymarket
        load_start = time.time()
        await page.goto("https://polymarket.com", wait_until="domcontentloaded")
        load_time = time.time() - load_start
        
        await browser.close()
        
    total_time = time.time() - start_total
    
    print(f"  Launch: {launch_time:.2f}s")
    print(f"  Page load: {load_time:.2f}s")
    print(f"  Total: {total_time:.2f}s")
    
    return {
        'browser': browser_name,
        'launch': launch_time,
        'load': load_time,
        'total': total_time
    }

async def main():
    results = []
    
    # Test Chrome (default)
    try:
        r = await test_browser_speed("Chrome (default)")
        results.append(r)
    except Exception as e:
        print(f"❌ Chrome failed: {e}")
    
    # Test Brave
    brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    try:
        r = await test_browser_speed("Brave", brave_path)
        results.append(r)
    except Exception as e:
        print(f"❌ Brave failed: {e}")
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    for r in results:
        print(f"{r['browser']}: {r['total']:.2f}s total")
    
    if len(results) == 2:
        faster = results[0] if results[0]['total'] < results[1]['total'] else results[1]
        slower = results[1] if results[0]['total'] < results[1]['total'] else results[0]
        diff = slower['total'] - faster['total']
        print(f"\n🏆 {faster['browser']} is {diff:.2f}s faster")

if __name__ == "__main__":
    asyncio.run(main())
