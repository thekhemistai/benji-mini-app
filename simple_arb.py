#!/usr/bin/env python3
"""
Polymarket Oracle Lag Arbitrage - Minimal Version
Monitors real price vs oracle price, bets when there's a gap.
"""

import time
import json
import csv
import requests
from datetime import datetime
from pathlib import Path

# CONFIG
PRICE_CHECK_INTERVAL = 5  # seconds - check prices every 5s
MIN_GAP_PERCENT = 0.1     # 0.1% price difference to trigger signal
PAPER_TRADE_SIZE = 10     # $10 per trade

# API endpoints
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
POLYMARKET_GAMMA = "https://gamma-api.polymarket.com/markets"
POLYMARKET_CLOB = "https://clob.polymarket.com"

# Track state
price_history = []
last_signal = None


def get_real_price(asset="bitcoin"):
    """Get real-time price from CoinGecko."""
    try:
        r = requests.get(
            f"{COINGECKO_URL}?ids={asset}&vs_currencies=usd",
            timeout=5
        )
        data = r.json()
        return data[asset]["usd"]
    except Exception as e:
        print(f"⚠️  Price fetch error: {e}")
        return None


def get_oracle_price(asset="BTC"):
    """Get oracle price from Polymarket/Chainlink data."""
    # Try to get from Polymarket's oracle feed
    # For now, we'll track this via the market data itself
    return None  # Placeholder - we'll implement Chainlink feed


def get_polymarket_odds(condition_id):
    """Get current YES/NO prices from Polymarket."""
    try:
        r = requests.get(f"{POLYMARKET_CLOB}/markets/{condition_id}", timeout=10)
        data = r.json()
        tokens = data.get("tokens", [])
        for token in tokens:
            if token.get("outcome") == "Yes":
                yes_price = token.get("price", 0)
            elif token.get("outcome") == "No":
                no_price = token.get("price", 0)
        return {"yes": yes_price, "no": no_price}
    except Exception as e:
        print(f"⚠️  Odds fetch error: {e}")
        return None


def calculate_edge(real_price, oracle_price, market_odds):
    """
    Simple edge calculation:
    - If real > oracle and odds < 0.9 → buy YES
    - If real < oracle and odds < 0.9 → buy NO
    """
    if not all([real_price, oracle_price, market_odds]):
        return None
    
    price_diff = real_price - oracle_price
    price_diff_pct = (price_diff / oracle_price) * 100
    
    yes_odds = market_odds.get("yes", 0)
    no_odds = market_odds.get("no", 0)
    
    signal = None
    confidence = 0
    
    if price_diff_pct > MIN_GAP_PERCENT:
        # Real price higher than oracle
        if yes_odds < 0.9:  # Not already too expensive
            signal = "BUY_YES"
            confidence = min(abs(price_diff_pct) * 10, 100)
            print(f"🎯 GAP: Real ${real_price:,.2f} > Oracle ${oracle_price:,.2f} ({price_diff_pct:+.3f}%)")
            print(f"   Market: YES at {yes_odds:.3f}¢ → Signal: BUY_YES (conf: {confidence:.0f}%)")
    
    elif price_diff_pct < -MIN_GAP_PERCENT:
        # Real price lower than oracle
        if no_odds < 0.9:
            signal = "BUY_NO"
            confidence = min(abs(price_diff_pct) * 10, 100)
            print(f"🎯 GAP: Real ${real_price:,.2f} < Oracle ${oracle_price:,.2f} ({price_diff_pct:+.3f}%)")
            print(f"   Market: NO at {no_odds:.3f}¢ → Signal: BUY_NO (conf: {confidence:.0f}%)")
    
    return {
        "signal": signal,
        "confidence": confidence,
        "price_diff_pct": price_diff_pct,
        "real_price": real_price,
        "oracle_price": oracle_price,
        "yes_odds": yes_odds,
        "no_odds": no_odds
    }


def paper_trade(signal_data, market_id):
    """Log a paper trade - no real money."""
    global last_signal
    
    signal = signal_data["signal"]
    if signal == last_signal:
        return  # Don't double-trade
    
    last_signal = signal
    
    trade = {
        "timestamp": datetime.now().isoformat(),
        "market_id": market_id,
        "signal": signal,
        "confidence": signal_data["confidence"],
        "entry_price": signal_data["yes_odds"] if "YES" in signal else signal_data["no_odds"],
        "trade_size": PAPER_TRADE_SIZE,
        "real_price": signal_data["real_price"],
        "oracle_price": signal_data["oracle_price"],
        "price_diff_pct": signal_data["price_diff_pct"]
    }
    
    # Log to CSV
    csv_file = Path("paper_trades.csv")
    file_exists = csv_file.exists()
    
    with open(csv_file, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=trade.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(trade)
    
    print(f"📝 PAPER TRADE: {signal} ${PAPER_TRADE_SIZE} @ {trade['entry_price']:.3f}¢")
    print(f"   Logged to paper_trades.csv")


def main():
    """Main loop - monitor and trade."""
    print("=" * 60)
    print("🎯 POLYMARKET ORACLE LAG ARBITRAGE")
    print("Simple mode: Real price vs Oracle price")
    print("=" * 60)
    
    # Market to monitor (BTC 5m up/down)
    # This would be the active market ID
    market_id = "0xe9cee59a1b59cfb07a71c6b30b69d9d7ac6923affa6aa0aab2b95baf5734f229"
    
    print(f"\nMonitoring: {market_id[:20]}...")
    print(f"Check interval: {PRICE_CHECK_INTERVAL}s")
    print(f"Min gap: {MIN_GAP_PERCENT}%")
    print(f"Paper trade size: ${PAPER_TRADE_SIZE}")
    print("\nPress Ctrl+C to stop\n")
    
    try:
        while True:
            # Get real price
            real_price = get_real_price("bitcoin")
            
            # For now, we'll track oracle price differently
            # In reality, this comes from Chainlink or the market's oracle
            # For testing, we'll simulate based on market odds
            market_odds = get_polymarket_odds(market_id)
            
            if real_price and market_odds:
                # Calculate implied oracle price from market odds
                # This is a simplification - in reality we'd get Chainlink feed
                yes_odds = market_odds["yes"]
                oracle_price = real_price * (1 - (yes_odds - 0.5))
                
                # Check for edge
                edge = calculate_edge(real_price, oracle_price, market_odds)
                
                if edge and edge["signal"]:
                    paper_trade(edge, market_id)
                else:
                    print(f"✓ Real: ${real_price:,.2f} | Oracle: ${oracle_price:,.2f} | YES: {yes_odds:.3f}¢ | Waiting...")
            else:
                print("⚠️  Missing data, retrying...")
            
            time.sleep(PRICE_CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n👋 Stopping arbitrage bot")
        print("Check paper_trades.csv for results")


if __name__ == "__main__":
    main()
