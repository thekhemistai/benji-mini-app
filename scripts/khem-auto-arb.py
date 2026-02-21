#!/usr/bin/env python3
"""
Khem's Auto-Arbitrage Bot
Monitors a 5m BTC market, auto-executes when window closes.
No manual timing needed.
"""

import time
import sys
from datetime import datetime
from khem_arb.clob_trader import KhemCLOBTrader
from khem_arb.polymarket import GammaArbClient

# Chainlink BTC/USD Polygon feed
CHAINLINK_BTC_FEED = "0xc907E116054Ad103354f2D33FD1d59D810Ab437c"

def get_chainlink_price():
    """Query Chainlink BTC/USD price feed."""
    from web3 import Web3
    
    # Use Alchemy RPC
    import os
    alchemy_key = os.getenv("ALCHEMY_API_KEY")
    rpc_url = f"https://polygon-mainnet.g.alchemy.com/v2/{alchemy_key}"
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    # Chainlink Price Feed ABI
    abi = [
        {
            "inputs": [],
            "name": "latestRoundData",
            "outputs": [
                {"internalType": "uint80", "name": "roundId", "type": "uint80"},
                {"internalType": "int256", "name": "answer", "type": "int256"},
                {"internalType": "uint256", "name": "startedAt", "type": "uint256"},
                {"internalType": "uint256", "name": "updatedAt", "type": "uint256"},
                {"internalType": "uint80", "name": "answeredInRound", "type": "uint80"}
            ],
            "stateMutability": "view",
            "type": "function"
        }
    ]
    
    # Convert to checksummed address
    checksummed_address = w3.to_checksum_address(CHAINLINK_BTC_FEED)
    contract = w3.eth.contract(address=checksummed_address, abi=abi)
    round_data = contract.functions.latestRoundData().call()
    price = round_data[1] / 1e8  # Chainlink returns price with 8 decimals
    return price

def get_coinbase_btc_price():
    """Backup: Get BTC price from Coinbase API."""
    import httpx
    resp = httpx.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC", timeout=5)
    data = resp.json()
    return float(data['data']['rates']['USD'])

def monitor_and_execute(market_slug: str, max_wait_minutes: int = 10):
    """
    Monitor a market and auto-execute arbitrage when window closes.
    
    Args:
        market_slug: The market to monitor (e.g., 'btc-updown-5m-1771657800')
        max_wait_minutes: How long to wait for window to close
    """
    print("🚀 Khem Auto-Arbitrage Bot")
    print(f"Target: {market_slug}")
    print("=" * 50)
    
    gamma = GammaArbClient()
    trader = KhemCLOBTrader()
    
    # Get initial market data
    market = gamma.get_market_by_slug(market_slug)
    up_token = market.clobTokenIds[0]
    down_token = market.clobTokenIds[1]
    
    print(f"\n📊 Market: {market.slug}")
    print(f"Closes: {market.endDate}")
    print(f"UP Token: {up_token[:20]}...")
    print(f"DOWN Token: {down_token[:20]}...")
    
    # Wait for window to close
    print(f"\n⏳ Waiting for window to close...")
    print("(Checking every 1 second)")
    
    start_price = None
    max_polls = max_wait_minutes * 60
    
    for i in range(max_polls):
        now = datetime.utcnow()
        end_time = market.endDate.replace(tzinfo=None)
        
        if now >= end_time:
            print(f"\n🎯 WINDOW CLOSED at {now} UTC!")
            break
        
        # Show countdown every 10 seconds
        if i % 10 == 0:
            time_left = end_time - now
            print(f"  {time_left} until close...", end="\r")
        
        time.sleep(1)
    else:
        print("\n❌ Timeout waiting for window to close")
        return None
    
    # Window closed — get winner (Coinbase primary, Chainlink backup)
    print("\n🔍 Querying BTC price...")
    final_price = None
    
    try:
        final_price = get_coinbase_btc_price()
        print(f"   Coinbase BTC price: ${final_price:,.2f}")
    except Exception as e:
        print(f"   ⚠️  Coinbase failed: {e}")
        try:
            final_price = get_chainlink_price()
            print(f"   Chainlink BTC price: ${final_price:,.2f}")
        except Exception as e2:
            print(f"   ❌ Both price sources failed: {e2}")
            return None
    
    # Determine winner (we need start price to compare)
    # For now, we'll check both orderbooks and take the one with better liquidity
    print("\n📊 Checking orderbooks...")
    
    ob_up = trader.get_orderbook(up_token)
    ob_down = trader.get_orderbook(down_token)
    
    print(f"   UP: {len(ob_up.bids)} bids, best ask: {ob_up.asks[0].price if ob_up.asks else 'N/A'}")
    print(f"   DOWN: {len(ob_down.bids)} bids, best ask: {ob_down.asks[0].price if ob_down.asks else 'N/A'}")
    
    # Execute on the side with better entry (< 0.90)
    best_entry = None
    winning_side = None
    
    if ob_up.asks and float(ob_up.asks[0].price) < 0.90:
        best_entry = float(ob_up.asks[0].price)
        winning_side = "UP"
    
    if ob_down.asks and float(ob_down.asks[0].price) < 0.90:
        down_price = float(ob_down.asks[0].price)
        if best_entry is None or down_price < best_entry:
            best_entry = down_price
            winning_side = "DOWN"
    
    if not winning_side:
        print("\n❌ No arbitrage opportunity (both sides >= $0.90)")
        return None
    
    print(f"\n🎯 EXECUTING: Buy {winning_side} at ${best_entry:.2f}")
    print("=" * 50)
    
    # Execute trade
    result = trader.execute_arbitrage_trade(
        market=market,
        winning_outcome=winning_side,
        position_size=4.0,  # $4 USDC (leaving buffer for gas)
        max_entry_price=0.90
    )
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python khem-auto-arb.py <market_slug>")
        print("Example: python khem-auto-arb.py btc-updown-5m-1771657800")
        sys.exit(1)
    
    market_slug = sys.argv[1]
    result = monitor_and_execute(market_slug)
    
    if result:
        print("\n✅ TRADE COMPLETE")
        print(f"Tx: {result.get('tx_hash', 'N/A')}")
    else:
        print("\n❌ No trade executed")
