#!/usr/bin/env python3
"""Test 4-hour BTC Up/Down arbitrage"""
import json
import time
from datetime import datetime, timezone
import requests
import subprocess
import re

def get_btc_price():
    try:
        resp = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=BTC', timeout=5)
        return float(resp.json()['data']['rates']['USD'])
    except:
        return None

def get_polymarket_4h():
    """Get the active 4-hour market odds"""
    try:
        result = subprocess.run(
            ['bankr', 'show odds for bitcoin up or down 4 hour market'],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            return None
        
        output = result.stdout
        # Look for Up (X%), Down (Y%)
        up_match = re.search(r'Up\s*\(\s*([\d.]+)%\s*\)', output)
        down_match = re.search(r'Down\s*\(\s*([\d.]+)%\s*\)', output)
        
        if up_match and down_match:
            return {
                'up': float(up_match.group(1)) / 100,
                'down': float(down_match.group(1)) / 100,
                'source': 'bankr',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

print("="*70)
print("4-HOUR BTC ARBITRAGE TEST")
print("="*70)

# Get BTC price
btc = get_btc_price()
if btc:
    print(f"BTC Price: ${btc:,.2f}")
else:
    print("Failed to get BTC price")
    exit(1)

# Get 4h market odds
print("\nFetching 4-hour Polymarket odds...")
start = time.time()
odds = get_polymarket_4h()
elapsed = time.time() - start

if odds:
    print(f"Fetched in {elapsed:.1f}s")
    print(f"Polymarket 4h odds: UP {odds['up']:.1%}, DOWN {odds['down']:.1%}")
    
    # Simulate scenarios
    print("\n--- Paper Trade Scenarios ---")
    scenarios = [
        ("Small move UP", 0.008),
        ("Small move DOWN", -0.010),
        ("Medium move UP", 0.015),
        ("Medium move DOWN", -0.020),
        ("Large move UP", 0.030),
    ]
    
    for name, change_pct in scenarios:
        fair_odds = 0.5 + (change_pct * 10) if change_pct > 0 else 0.5 - (abs(change_pct) * 10)
        fair_odds = max(0.05, min(0.95, fair_odds))
        
        if change_pct > 0:
            current_odds = odds['up']
            edge = fair_odds - current_odds
            direction = 'UP'
        else:
            current_odds = odds['down']
            edge = fair_odds - current_odds
            direction = 'DOWN'
        
        status = '✅ TRADE' if edge >= 0.05 else '❌ SKIP'
        print(f"{name}: {direction} {abs(change_pct)*100:.1f}% | Current: {current_odds:.1%} | Fair: {fair_odds:.1%} | Edge: {edge:+.1%} | {status}")
else:
    print("Failed to get 4h market odds")

print("\n" + "="*70)
print(f"Latency: {elapsed:.1f}s - ACCEPTABLE for 4-hour markets")
print("="*70)
