#!/usr/bin/env python3
"""
Khem 5-Minute BTC Arbitrage Bot

Full execution pipeline:
1. Monitor 5m window via Gamma API
2. Query Chainlink at resolution
3. Confirm winner (UP or DOWN)
4. Execute via direct CLOB API

Target: <10s from resolution to fill
"""

import os
import sys
import time
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv

# Add workspace to path
sys.path.insert(0, '/Users/thekhemist/.openclaw/workspace')

from khem_arb.polymarket import GammaArbClient, ArbMarket
from khem_arb.clob_trader import KhemCLOBTrader

load_dotenv()


class BTC5mArbBot:
    """
    Automated 5-minute BTC arbitrage bot.
    
    Monitors 5m windows, confirms resolution, executes winning side.
    """
    
    def __init__(self):
        self.gamma = GammaArbClient()
        self.trader: Optional[KhemCLOBTrader] = None
        
        # Initialize trader if private key available
        if os.getenv("POLYGON_WALLET_PRIVATE_KEY"):
            try:
                self.trader = KhemCLOBTrader()
                print("✅ CLOB Trader initialized")
            except Exception as e:
                print(f"⚠️  CLOB Trader init failed: {e}")
                print("   Running in PAPER MODE")
        else:
            print("⏸️  POLYGON_WALLET_PRIVATE_KEY not set")
            print("   Running in PAPER MODE (no live trades)")
    
    def get_current_5m_window(self) -> Optional[ArbMarket]:
        """
        Find the current active 5m BTC window.
        
        5m windows run every 5 minutes (:00, :05, :10, etc.)
        """
        from datetime import datetime
        
        now = datetime.utcnow()
        
        # Calculate current 5m window
        current_5m = (now.minute // 5) * 5
        window_start = datetime(now.year, now.month, now.day, now.hour, current_5m)
        ts = int(window_start.timestamp())
        
        slug = f'btc-updown-5m-{ts}'
        
        try:
            market = self.gamma.get_market_by_slug(slug)
            if market and not market.closed:
                return market
        except Exception as e:
            print(f"Error fetching window: {e}")
        
        return None
    
    def query_chainlink_btc(self) -> Optional[float]:
        """
        Query Chainlink BTC/USD price.
        
        Returns current BTC price or None on failure.
        """
        import httpx
        
        # Chainlink data streams API
        # Note: This is a placeholder - actual Chainlink API may differ
        url = "https://data.chain.link/streams/btc-usd"
        
        try:
            response = httpx.get(url, timeout=5)
            # Parse response based on actual Chainlink format
            # For now, return None to indicate manual verification needed
            return None
        except Exception as e:
            print(f"Chainlink query failed: {e}")
            return None
    
    def determine_winner(self, start_price: float, end_price: float) -> str:
        """
        Determine winning outcome.
        
        Args:
            start_price: BTC price at window start
            end_price: BTC price at window end
        
        Returns:
            "UP" if end >= start, "DOWN" otherwise
        """
        if end_price >= start_price:
            return "UP"
        return "DOWN"
    
    async def execute_arbitrage(
        self,
        market: ArbMarket,
        winning_outcome: str,
        paper_mode: bool = True
    ):
        """
        Execute arbitrage trade.
        
        Args:
            market: Market to trade
            winning_outcome: "UP" or "DOWN"
            paper_mode: If True, log only. If False, execute live.
        """
        print(f"\n🎯 ARBITRAGE OPPORTUNITY")
        print(f"   Market: {market.slug}")
        print(f"   Winner: {winning_outcome}")
        
        if paper_mode or not self.trader:
            # Paper trade - log only
            print(f"\n📝 PAPER TRADE")
            print(f"   Would buy {winning_outcome}")
            print(f"   Target price: < $0.90")
            print(f"   Expected exit: $1.00")
            print(f"   Min edge: 10%")
            
            # Log to file
            self._log_paper_trade(market, winning_outcome)
            
        else:
            # Live trade
            print(f"\n🚀 LIVE TRADE")
            result = self.trader.execute_arbitrage_trade(
                market=market,
                winning_outcome=winning_outcome,
                max_entry_price=0.90,
                position_size=50.0  # Start small
            )
            
            if result:
                print(f"✅ Trade executed successfully")
                print(f"   Time: {result['execution_time']:.2f}s")
            else:
                print(f"❌ Trade not executed (no spread or error)")
    
    def _log_paper_trade(self, market: ArbMarket, outcome: str):
        """Log paper trade to file."""
        import json
        from datetime import datetime
        
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "market": market.slug,
            "outcome": outcome,
            "type": "paper",
            "prices": market.outcomePrices
        }
        
        log_file = "/Users/thekhemist/.openclaw/workspace/memory/trading/paper_trades_5m.jsonl"
        
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        print(f"   Logged to: {log_file}")
    
    async def monitor_and_trade(self):
        """
        Main monitoring loop.
        
        Continuously monitors for 5m windows and executes arbitrage.
        """
        print("🤖 Khem 5m BTC Arb Bot Starting...")
        print(f"⏰ Current UTC: {datetime.utcnow()}")
        print()
        
        # Find current window
        market = self.get_current_5m_window()
        
        if not market:
            print("❌ No active 5m window found")
            print("   Markets may be offline or we're between windows")
            return
        
        print(f"✅ Found active window:")
        print(f"   Slug: {market.slug}")
        print(f"   Closes: {market.endDate}")
        print(f"   Prices: {market.outcomePrices}")
        print()
        
        # Calculate time until close
        now = datetime.utcnow()
        time_until_close = market.endDate.replace(tzinfo=None) - now
        
        print(f"⏳ Window closes in: {time_until_close}")
        print(f"   Waiting...")
        
        # Wait until close (with buffer)
        wait_seconds = time_until_close.total_seconds() + 2  # 2s buffer
        
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)
        
        print(f"\n🔔 Window closed!")
        print(f"   Querying resolution...")
        
        # In production: Query Chainlink for actual prices
        # For now: Prompt user to confirm
        print("\n⚠️  MANUAL CONFIRMATION REQUIRED")
        print("   Please check Chainlink BTC/USD for window close price")
        print(f"   Market: {market.slug}")
        print()
        
        # Simulate for now
        winner = "UP"  # This would come from Chainlink query
        
        await self.execute_arbitrage(market, winner, paper_mode=True)
    
    def test_connection(self):
        """Test all connections."""
        print("🧪 Testing Connections...")
        print()
        
        # Test Gamma API
        print("1. Gamma API...")
        try:
            m = self.gamma.get_market_by_slug("btc-updown-5m-1771659900")
            if m:
                print(f"   ✅ Working | {m.slug}")
            else:
                print("   ⚠️  Market not found")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Test CLOB
        print("\n2. CLOB API...")
        if self.trader:
            try:
                balance = self.trader.get_balance()
                print(f"   ✅ Working | Balance: {balance['usdc']:.2f} USDC")
            except Exception as e:
                print(f"   ⚠️  Error: {e}")
        else:
            print("   ⏸️  Skipped (no private key)")
        
        print("\n✅ Connection tests complete")


async def main():
    """Main entry point."""
    bot = BTC5mArbBot()
    
    # Test connections first
    bot.test_connection()
    
    print("\n" + "="*50)
    print()
    
    # Run monitor
    await bot.monitor_and_trade()


if __name__ == "__main__":
    asyncio.run(main())
