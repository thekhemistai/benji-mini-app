"""
Kalshi API Client for Cross-Market Arbitrage
Handles authentication and market data retrieval.
"""

import os
import hmac
import hashlib
import time
from typing import Dict, List, Optional
import httpx
from pydantic import BaseModel


class KalshiMarket(BaseModel):
    """Kalshi market data model."""
    ticker: str
    title: str
    status: str
    yes_ask: float  # Price to buy YES (0-1)
    yes_bid: float  # Price to sell YES (0-1)
    no_ask: float   # Price to buy NO (0-1)
    no_bid: float   # Price to sell NO (0-1)
    volume: int
    open_interest: int
    last_price: Optional[float] = None
    

class KalshiClient:
    """Kalshi API client with HMAC authentication."""
    
    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
    
    def __init__(self):
        self.api_key = os.getenv("KALSHI_API_KEY")
        self.api_secret = os.getenv("KALSHI_API_SECRET")
        
        if not self.api_key or not self.api_secret:
            print("⚠️  KALSHI_API_KEY or KALSHI_API_SECRET not set")
            print("   Cross-market arb will be limited to Polymarket only")
    
    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        """Generate HMAC-SHA256 signature for Kalshi auth."""
        message = timestamp + method.upper() + path + body
        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_headers(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """Generate authentication headers."""
        timestamp = str(int(time.time()))
        signature = self._generate_signature(timestamp, method, path, body)
        
        return {
            "kalshiAccessKey": self.api_key,
            "kalshiAccessTimestamp": timestamp,
            "kalshiAccessSignature": signature,
            "Content-Type": "application/json"
        }
    
    def get_markets(self, limit: int = 100, status: str = "active") -> List[KalshiMarket]:
        """Get list of active markets."""
        path = f"/markets?status={status}&limit={limit}"
        url = self.BASE_URL + path
        
        headers = self._get_headers("GET", path)
        
        try:
            resp = httpx.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            
            markets = []
            for m in data.get("markets", []):
                markets.append(KalshiMarket(
                    ticker=m.get("ticker", ""),
                    title=m.get("title", ""),
                    status=m.get("status", ""),
                    yes_ask=m.get("yes_ask", 0) / 100,  # Convert from cents
                    yes_bid=m.get("yes_bid", 0) / 100,
                    no_ask=m.get("no_ask", 0) / 100,
                    no_bid=m.get("no_bid", 0) / 100,
                    volume=m.get("volume", 0),
                    open_interest=m.get("open_interest", 0),
                    last_price=m.get("last_price", 0) / 100 if m.get("last_price") else None
                ))
            
            return markets
            
        except Exception as e:
            print(f"❌ Kalshi API error: {e}")
            return []
    
    def get_market_by_ticker(self, ticker: str) -> Optional[KalshiMarket]:
        """Get specific market by ticker."""
        path = f"/markets/{ticker}"
        url = self.BASE_URL + path
        
        headers = self._get_headers("GET", path)
        
        try:
            resp = httpx.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            m = data.get("market", {})
            
            return KalshiMarket(
                ticker=m.get("ticker", ""),
                title=m.get("title", ""),
                status=m.get("status", ""),
                yes_ask=m.get("yes_ask", 0) / 100,
                yes_bid=m.get("yes_bid", 0) / 100,
                no_ask=m.get("no_ask", 0) / 100,
                no_bid=m.get("no_bid", 0) / 100,
                volume=m.get("volume", 0),
                open_interest=m.get("open_interest", 0),
                last_price=m.get("last_price", 0) / 100 if m.get("last_price") else None
            )
            
        except Exception as e:
            print(f"❌ Kalshi API error for {ticker}: {e}")
            return None
    
    def search_markets(self, query: str) -> List[KalshiMarket]:
        """Search markets by keyword."""
        all_markets = self.get_markets(limit=1000)
        query_lower = query.lower()
        
        return [
            m for m in all_markets 
            if query_lower in m.title.lower() or query_lower in m.ticker.lower()
        ]


class CrossMarketArbitrage:
    """Compare prices between Polymarket and Kalshi."""
    
    def __init__(self):
        from khem_arb.polymarket import GammaArbClient
        self.polymarket = GammaArbClient()
        self.kalshi = KalshiClient()
    
    def find_trump_opportunities(self) -> List[Dict]:
        """Find Trump-related arbitrage opportunities."""
        opportunities = []
        
        # Get Polymarket Trump markets
        pm_markets = self.polymarket.get_active_markets()
        pm_trump = [m for m in pm_markets if 'trump' in m.slug.lower()]
        
        # Get Kalshi Trump markets
        kalshi_trump = self.kalshi.search_markets("trump")
        
        # Compare overlapping markets
        for pm in pm_trump:
            for k in kalshi_trump:
                # Check if titles match (simple fuzzy matching)
                if self._titles_match(pm.title, k.title):
                    pm_price = float(pm.outcomePrices[0]) if pm.outcomePrices else 0.5
                    k_price = k.yes_ask  # Price to buy YES
                    
                    edge = abs(pm_price - k_price)
                    
                    if edge > 0.05:  # 5% threshold
                        opportunities.append({
                            "polymarket": {
                                "slug": pm.slug,
                                "title": pm.title,
                                "price": pm_price
                            },
                            "kalshi": {
                                "ticker": k.ticker,
                                "title": k.title,
                                "price": k_price
                            },
                            "edge": edge,
                            "recommendation": "Buy on Kalshi" if k_price < pm_price else "Buy on Polymarket"
                        })
        
        return opportunities
    
    def _titles_match(self, title1: str, title2: str) -> bool:
        """Simple title matching for market overlap."""
        # Extract key words
        words1 = set(title1.lower().split())
        words2 = set(title2.lower().split())
        
        # Check for significant overlap
        common = words1 & words2
        return len(common) >= 3  # At least 3 common words


if __name__ == "__main__":
    # Test the client
    print("🧪 Testing Kalshi client...")
    client = KalshiClient()
    
    if client.api_key:
        print("✅ API key found")
        markets = client.search_markets("trump")
        print(f"Found {len(markets)} Trump markets on Kalshi")
        for m in markets[:3]:
            print(f"  {m.ticker}: {m.title} (YES: {m.yes_ask:.2%})")
    else:
        print("⚠️  No API key - set KALSHI_API_KEY and KALSHI_API_SECRET")
