#!/usr/bin/env python3
"""
Live BTC Arb Trade - OPTIMIZED (Direct HTTP)
No Bankr CLI overhead - direct to Polymarket API
"""

import requests
import time
from datetime import datetime

# Polymarket Gamma API endpoints
GAMMA_API = "https://gamma-api.polymarket.com"

def get_btc_price():
    """Fast price check"""
    try:
        r = requests.get(
            'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd',
            timeout=3
        )
        return r.json()['bitcoin']['usd']
    except:
        return None

def find_btc_market():
    """Find current BTC 5m market"""
    try:
        # Get active BTC markets
        r = requests.get(
            f"{GAMMA_API}/events?active=true&tag_slug=bitcoin&limit=5",
            timeout=10
        )
        events = r.json()
        
        # Find 5m up/down market
        for event in events:
            if 'updown' in event.get('slug', '') and '5m' in event.get('slug', ''):
                return event
        return None
    except Exception as e:
        print(f"Error finding market: {e}")
        return None

def get_market_prices(market_id):
    """Get current market prices"""
    try:
        r = requests.get(
            f"{GAMMA_API}/events/{market_id}",
            timeout=3
        )
        data = r.json()
        
        # Extract YES/NO prices
        prices = {}
        for token in data.get('tokens', []):
            if 'outcome' in token:
                prices[token['outcome']] = token.get('price', 0)
        
        return prices
    except:
        return {}

def main():
    print(f"⚡ OPTIMIZED TRADE - {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    print("Method: Direct HTTP (no Bankr CLI overhead)")
    print("="*60)
    
    # STEP 1: Find market and get start price
    print("\n📊 Finding market...")
    market = find_btc_market()
    if not market:
        print("❌ No active BTC 5m market found")
        return
    
    market_id = market['id']
    market_slug = market['slug']
    print(f"✅ Market: {market_slug}")
    
    # Get start price
    start_price = get_btc_price()
    if not start_price:
        print("❌ Failed to get BTC price")
        return
    print(f"✅ Start price: ${start_price}")
    
    # Get initial market prices
    print("\n💰 Current market prices:")
    prices = get_market_prices(market_id)
    for outcome, price in prices.items():
        print(f"   {outcome}: {price:.2f}¢")
    
    # STEP 2: Wait for window close
    print("\n⏳ Waiting for window close...")
    # For 5m window, wait 5 minutes
    for i in range(5, 0, -1):
        print(f"   {i} min...", end='\r')
        time.sleep(60)
    print("\n")
    
    # STEP 3: Get end price and determine winner
    end_price = get_btc_price()
    if not end_price:
        print("❌ Failed to get end price")
        return
    
    winner = "YES" if end_price >= start_price else "NO"
    change = abs(end_price - start_price)
    
    print(f"\n🏆 WINNER: {winner}")
    print(f"   Start: ${start_price}")
    print(f"   End: ${end_price}")
    print(f"   Change: ${change:.2f}")
    
    # STEP 4: Get post-resolution market prices
    print("\n📊 Post-resolution prices:")
    time.sleep(2)  # Brief delay for market to update
    new_prices = get_market_prices(market_id)
    for outcome, price in new_prices.items():
        print(f"   {outcome}: {price:.2f}¢")
    
    # STEP 5: Check for arb opportunity
    winner_price = new_prices.get(winner, 0)
    
    if winner_price < 0.95:  # If winner trading below 95¢
        print(f"\n💎 ARB OPPORTUNITY: {winner} at {winner_price:.2f}¢")
        print("   Should be $1.00 - potential profit!")
        
        # Log for manual execution
        print("\n⚡ EXECUTE NOW:")
        print(f"   npx bankr 'buy 5 dollars of {winner.lower()} on {market_slug}'")
        
    else:
        print(f"\n⏭️  No arb opportunity - {winner} at {winner_price:.2f}¢ (already near $1)")
    
    # Log
    trade_log = f"""
Trade Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M')}
- Market: {market_slug}
- Start: ${start_price}
- End: ${end_price}
- Winner: {winner}
- Winner Price: {winner_price:.2f}¢
- Arb Opportunity: {'YES' if winner_price < 0.95 else 'NO'}
"""
    with open('trade_analysis.txt', 'a') as f:
        f.write(trade_log)
    
    print("\n✅ Analysis complete")

if __name__ == "__main__":
    main()
