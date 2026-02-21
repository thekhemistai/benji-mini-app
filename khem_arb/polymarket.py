"""
Khem Polymarket Arbitrage Toolkit
Adapted from Polymarket's official agents framework

Key adaptations:
- Gamma API client (clean pagination, query patterns)
- Pydantic models for type safety
- Removed: RAG, LLM prediction, sentiment analysis (too slow for arb)
- Added: Resolution source monitoring, price staleness detection

Usage:
    from khem_arb.polymarket import GammaArbClient, ArbMarket
    
    client = GammaArbClient()
    btc_markets = client.get_btc_updown_markets(hours_ahead=24)
"""

import httpx
import json
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel, Field


class ArbMarket(BaseModel):
    """
    Streamlined market model for arbitrage operations.
    
    Only fields needed for arb decisions:
    - Identification (id, slug)
    - Timing (endDate, resolution window)
    - Pricing (outcomePrices, current odds)
    - Execution (clobTokenIds for orderbook lookup)
    """
    id: int
    slug: str = Field(..., description="URL slug like 'btc-updown-15m-1771552800'")
    question: str
    endDate: datetime = Field(..., description="Market resolution time (UTC)")
    active: bool
    closed: bool
    
    # Price data - parsed from JSON strings
    outcomePrices: List[float] = Field(default_factory=list)
    outcomes: List[str] = Field(default_factory=list)
    
    # Execution
    clobTokenIds: List[str] = Field(default_factory=list)
    
    # Metadata
    description: Optional[str] = None
    volume: float = 0.0
    liquidity: float = 0.0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ArbEvent(BaseModel):
    """
    Event wrapper for multi-market events.
    
    For BTC up/down, each event has one market.
    For complex events (elections), one event has multiple markets.
    """
    id: str
    slug: str
    title: str
    endDate: datetime
    active: bool
    closed: bool
    archived: bool
    restricted: bool
    
    # Tags for filtering (e.g., tag_slug=bitcoin)
    tags: List[dict] = Field(default_factory=list)
    
    # Nested markets
    markets: List[ArbMarket] = Field(default_factory=list)


class GammaArbClient:
    """
    Clean Gamma API client adapted for arbitrage operations.
    
    Key differences from official client:
    - No Pydantic parsing overhead on hot paths (optional)
    - Time-range queries for discovering upcoming BTC markets
    - Tag-based filtering for specific market types
    """
    
    GAMMA_URL = "https://gamma-api.polymarket.com"
    
    def __init__(self):
        self.markets_endpoint = f"{self.GAMMA_URL}/markets"
        self.events_endpoint = f"{self.GAMMA_URL}/events"
        self.client = httpx.Client(timeout=10.0)
    
    def _get(self, endpoint: str, params: dict = None) -> dict:
        """Base GET with error handling."""
        response = self.client.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()
    
    def _parse_market(self, data: dict) -> ArbMarket:
        """Parse Gamma market response into ArbMarket."""
        # Parse JSON-encoded arrays
        outcome_prices = json.loads(data.get("outcomePrices", "[]"))
        outcomes = json.loads(data.get("outcomes", "[]"))
        token_ids = json.loads(data.get("clobTokenIds", "[]"))
        
        # Parse ISO datetime
        end_date = datetime.fromisoformat(data["endDate"].replace("Z", "+00:00"))
        
        return ArbMarket(
            id=data["id"],
            slug=data.get("slug", ""),
            question=data.get("question", ""),
            endDate=end_date,
            active=data.get("active", False),
            closed=data.get("closed", False),
            outcomePrices=[float(p) for p in outcome_prices],
            outcomes=outcomes,
            clobTokenIds=token_ids,
            description=data.get("description"),
            volume=float(data.get("volume", 0)),
            liquidity=float(data.get("liquidity", 0)),
        )
    
    def get_market_by_slug(self, slug: str) -> Optional[ArbMarket]:
        """Fetch single market by slug (e.g., 'btc-updown-15m-1771552800')."""
        params = {"slug": slug}
        data = self._get(self.markets_endpoint, params)
        
        if data and len(data) > 0:
            return self._parse_market(data[0])
        return None
    
    def get_market_by_id(self, market_id: int) -> Optional[ArbMarket]:
        """Fetch single market by numeric ID."""
        url = f"{self.markets_endpoint}/{market_id}"
        data = self._get(url)
        
        if data:
            return self._parse_market(data)
        return None
    
    def get_active_markets(
        self,
        tag_slug: Optional[str] = None,
        limit: int = 100,
        parse: bool = True
    ) -> List[ArbMarket]:
        """
        Get active, non-closed markets with optional tag filter.
        
        Args:
            tag_slug: Filter by tag (e.g., 'bitcoin', 'crypto', 'sports')
            limit: Max results per page
            parse: If True, return ArbMarket objects; if False, return raw JSON
        """
        params = {
            "active": True,
            "closed": False,
            "archived": False,
            "limit": limit,
        }
        
        if tag_slug:
            params["tag_slug"] = tag_slug
        
        data = self._get(self.markets_endpoint, params)
        
        if not parse:
            return data
        
        markets = []
        for item in data:
            try:
                markets.append(self._parse_market(item))
            except Exception as e:
                print(f"[WARN] Failed to parse market {item.get('id')}: {e}")
                continue
        
        return markets
    
    def get_btc_updown_markets(
        self,
        hours_ahead: int = 24,
        timeframes: List[str] = None
    ) -> List[ArbMarket]:
        """
        Discover upcoming BTC up/down markets for arbitrage.
        
        Args:
            hours_ahead: How many hours into the future to search
            timeframes: Which timeframes to include ('5m', '15m', '1h', '4h')
            
        Returns:
            List of BTC up/down markets closing within the window
        """
        if timeframes is None:
            timeframes = ['5m', '15m', '1h', '4h']
        
        # Get all bitcoin-tagged markets
        all_btc = self.get_active_markets(tag_slug="bitcoin", limit=100)
        
        # Filter for up/down markets in our time window
        now = datetime.utcnow()
        cutoff = now + timedelta(hours=hours_ahead)
        
        arb_markets = []
        for market in all_btc:
            # Check if it's an up/down market
            if "updown" not in market.slug and "up or down" not in market.question.lower():
                continue
            
            # Check timeframe
            if not any(tf in market.slug for tf in timeframes):
                continue
            
            # Check if within our monitoring window
            if now <= market.endDate <= cutoff:
                arb_markets.append(market)
        
        # Sort by resolution time
        arb_markets.sort(key=lambda m: m.endDate)
        return arb_markets
    
    def get_events_by_tag(
        self,
        tag_slug: str,
        limit: int = 100
    ) -> List[ArbEvent]:
        """
        Get events by tag slug.
        
        For BTC up/down, events and markets are 1:1, so this returns
        the same data as get_active_markets but grouped by event.
        """
        params = {
            "active": True,
            "closed": False,
            "archived": False,
            "limit": limit,
            "tag_slug": tag_slug,
        }
        
        data = self._get(self.events_endpoint, params)
        
        events = []
        for item in data:
            try:
                # Parse nested markets
                markets_data = item.get("markets", [])
                markets = [self._parse_market(m) for m in markets_data]
                
                event = ArbEvent(
                    id=str(item["id"]),
                    slug=item.get("slug", ""),
                    title=item.get("title", ""),
                    endDate=datetime.fromisoformat(item["endDate"].replace("Z", "+00:00")),
                    active=item.get("active", False),
                    closed=item.get("closed", False),
                    archived=item.get("archived", False),
                    restricted=item.get("restricted", False),
                    tags=item.get("tags", []),
                    markets=markets,
                )
                events.append(event)
            except Exception as e:
                print(f"[WARN] Failed to parse event {item.get('id')}: {e}")
                continue
        
        return events


class ArbOpportunity(BaseModel):
    """
    Represents a detected arbitrage opportunity.
    
    This is the output of the arb detection engine, ready for
    execution decision.
    """
    market: ArbMarket
    detected_at: datetime
    
    # Resolution status
    resolution_confirmed: bool = False
    resolution_source: Optional[str] = None  # e.g., "chainlink"
    winning_outcome: Optional[str] = None    # "UP" or "DOWN"
    
    # Market status
    market_price: float = 0.0    # Current price on Polymarket
    expected_price: float = 1.0  # Should be ~$1.00 after resolution
    price_staleness_seconds: float = 0.0
    
    # Execution
    potential_profit: float = 0.0  # (expected - market) * position_size
    executable: bool = False
    
    def __str__(self) -> str:
        status = "✅ EXECUTABLE" if self.executable else "⏳ WAITING"
        return (
            f"{status} | {self.market.slug}\n"
            f"  Price: ${self.market_price:.2f} (should be ${self.expected_price:.2f})\n"
            f"  Potential: ${self.potential_profit:.2f}\n"
            f"  Stale: {self.price_staleness_seconds:.1f}s"
        )


# --- Quick Test ---
if __name__ == "__main__":
    client = GammaArbClient()
    
    print("Fetching BTC up/down markets for next 24 hours...")
    markets = client.get_btc_updown_markets(hours_ahead=24)
    
    print(f"\nFound {len(markets)} markets:\n")
    for m in markets:
        print(f"  {m.slug}")
        print(f"    Closes: {m.endDate.strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"    Prices: {m.outcomePrices}")
        print(f"    Token IDs: {m.clobTokenIds}")
        print()
