#!/usr/bin/env python3
"""
Conway Token Price Tracker
Quick price checks for both Conway ecosystem tokens
"""

import requests
import json
from datetime import datetime

TOKENS = {
    "CONWAY": {
        "address": "0x86cdd90bc48f7b5a866feaaf5023b8802dc2ab07",
        "chain": "base",
        "symbol": "CONWAY"
    },
    "CONWAY_AGENT": {
        "address": "0x14f78F655451f4C85641E46F9D196920CA54cba3", 
        "chain": "base",
        "symbol": "CONWAY-AGENT"
    }
}

def get_token_price_birdeye(address, chain="base"):
    """Fetch price from BirdEye API (free tier available)"""
    try:
        # Using GeckoTerminal as alternative (no API key needed for basic data)
        url = f"https://api.geckoterminal.com/api/v2/networks/{chain}/tokens/{address}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            attrs = data.get("data", {}).get("attributes", {})
            return {
                "price_usd": float(attrs.get("price_usd", 0)),
                "market_cap_usd": float(attrs.get("market_cap_usd", 0) or 0),
                "fdv_usd": float(attrs.get("fdv_usd", 0) or 0),
                "volume_24h": float(attrs.get("volume_usd", {}).get("h24", 0) or 0),
                "source": "geckoterminal"
            }
    except Exception as e:
        pass
    
    return None

def get_token_price_dexscreener(address, chain="base"):
    """Fetch price from DexScreener (no API key)"""
    try:
        url = f"https://api.dexscreener.com/latest/dex/tokens/{address}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            pairs = data.get("pairs", [])
            if pairs:
                # Get highest liquidity pair
                best_pair = max(pairs, key=lambda x: float(x.get("liquidity", {}).get("usd", 0) or 0))
                return {
                    "price_usd": float(best_pair.get("priceUsd", 0)),
                    "market_cap_usd": float(best_pair.get("marketCap", 0) or 0),
                    "fdv_usd": float(best_pair.get("fdv", 0) or 0),
                    "volume_24h": float(best_pair.get("volume", {}).get("h24", 0) or 0),
                    "liquidity_usd": float(best_pair.get("liquidity", {}).get("usd", 0) or 0),
                    "dex": best_pair.get("dexId", "unknown"),
                    "source": "dexscreener"
                }
    except Exception as e:
        pass
    
    return None

def track_conway_tokens():
    """Track both Conway tokens and print summary"""
    print("🧪 Conway Token Tracker")
    print("=" * 70)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("")
    
    results = {}
    
    for name, token in TOKENS.items():
        print(f"📊 {token['symbol']} ({name})")
        print(f"   Address: {token['address'][:20]}...")
        
        # Try DexScreener first (usually more reliable for Base)
        data = get_token_price_dexscreener(token['address'], token['chain'])
        
        if not data:
            data = get_token_price_birdeye(token['address'], token['chain'])
        
        if data:
            results[name] = data
            print(f"   💰 Price: ${data['price_usd']:.6f}")
            if data.get('market_cap_usd'):
                print(f"   📈 Mcap: ${data['market_cap_usd']:,.0f}")
            if data.get('volume_24h'):
                print(f"   📊 24h Volume: ${data['volume_24h']:,.0f}")
            if data.get('liquidity_usd'):
                print(f"   💧 Liquidity: ${data['liquidity_usd']:,.0f}")
            print(f"   Source: {data.get('source', 'unknown')}")
        else:
            print("   ❌ Could not fetch price data")
            results[name] = None
        
        print("")
    
    # Save to history file
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "prices": results
    }
    
    try:
        with open("conway_price_history.jsonl", "a") as f:
            f.write(json.dumps(history_entry) + "\n")
    except:
        pass
    
    print("=" * 70)
    print("✅ Tracking complete")
    print("History saved to: conway_price_history.jsonl")
    
    return results

if __name__ == "__main__":
    track_conway_tokens()
