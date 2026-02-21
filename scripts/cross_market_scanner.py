#!/usr/bin/env python3
"""
Cross-Market Arbitrage Scanner & Paper Trade Logger
Tests cross-market strategies without real money
"""

import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class CrossMarketArbitrage:
    def __init__(self):
        self.gamma_api = "https://gamma-api.polymarket.com"
        self.paper_trades = []
        
    def get_active_btc_markets(self) -> List[Dict]:
        """Fetch all active BTC-related markets"""
        try:
            url = f"{self.gamma_api}/events?active=true&tag_slug=bitcoin&limit=20"
            response = requests.get(url, timeout=10)
            data = response.json()
            return data if isinstance(data, list) else []
        except Exception as e:
            print(f"Error fetching markets: {e}")
            return []
    
    def get_daily_price_markets(self, markets: List[Dict]) -> List[Dict]:
        """Filter for daily/weekly price prediction markets"""
        daily_markets = []
        for market in markets:
            slug = market.get('slug', '').lower()
            title = market.get('title', '').lower()
            
            # Look for price threshold markets
            if any(x in slug for x in ['above', 'below', 'reach', 'price']) and \
               any(x in slug for x in ['friday', 'april', 'may', 'june']):
                daily_markets.append(market)
        
        return daily_markets
    
    def extract_price_threshold(self, market: Dict) -> Optional[Tuple[str, int]]:
        """Extract price threshold from market title/slug"""
        import re
        
        title = market.get('title', '')
        slug = market.get('slug', '')
        text = f"{title} {slug}"
        
        # Look for price patterns like 70000, 65000, etc.
        matches = re.findall(r'(\d{4,6})', text)
        if matches:
            # Get the highest number (most likely the price)
            price = max(int(m) for m in matches)
            
            # Determine if it's "above" or "below"
            if 'above' in text.lower() or 'reach' in text.lower():
                direction = 'above'
            elif 'below' in text.lower() or 'dip' in text.lower():
                direction = 'below'
            else:
                direction = 'unknown'
            
            return (direction, price)
        
        return None
    
    def get_market_price(self, market: Dict) -> Optional[float]:
        """Get current YES token price"""
        try:
            tokens = market.get('tokens', [])
            for token in tokens:
                if token.get('outcome', '').upper() == 'YES':
                    return float(token.get('price', 0))
            return None
        except:
            return None
    
    def find_cross_market_opportunities(self) -> List[Dict]:
        """Find arbitrage opportunities across related markets"""
        print(f"\n{'='*70}")
        print("CROSS-MARKET ARBITRAGE SCANNER")
        print(f"{'='*70}\n")
        
        # Get all BTC markets
        markets = self.get_active_btc_markets()
        print(f"Found {len(markets)} active BTC markets\n")
        
        # Filter for price-based markets
        price_markets = self.get_daily_price_markets(markets)
        print(f"Found {len(price_markets)} price-threshold markets")
        print("-" * 70)
        
        opportunities = []
        
        # Extract price data
        market_data = []
        for market in price_markets:
            threshold = self.extract_price_threshold(market)
            price = self.get_market_price(market)
            
            if threshold and price is not None:
                direction, amount = threshold
                market_data.append({
                    'market': market,
                    'slug': market.get('slug', ''),
                    'title': market.get('title', '')[:60],
                    'direction': direction,
                    'threshold': amount,
                    'yes_price': price,
                    'no_price': 1 - price,
                    'volume': market.get('volume', 0)
                })
        
        # Sort by threshold
        market_data.sort(key=lambda x: x['threshold'])
        
        print("\n📊 PRICE MARKETS (sorted by threshold):")
        print(f"{'Market':<45} {'Threshold':<12} {'YES Price':<12} {'Volume':<15}")
        print("-" * 85)
        
        for m in market_data[:10]:
            print(f"{m['title'][:44]:<45} ${m['threshold']:<11,} {m['yes_price']:<11.2f} ${m['volume']:>10,.0f}")
        
        # Look for temporal arbitrage opportunities
        print("\n\n🔍 SCANNING FOR ARBITRAGE OPPORTUNITIES:")
        print("-" * 70)
        
        # Type 1: Nested thresholds (if $70K is hit, $65K must be hit)
        for i, market_a in enumerate(market_data):
            for market_b in market_data[i+1:]:
                # Check if A is higher threshold than B
                if market_a['threshold'] > market_b['threshold']:
                    higher = market_a
                    lower = market_b
                    
                    # Logic: If higher threshold wins, lower MUST win
                    # So higher_yes_price should be <= lower_yes_price
                    
                    if higher['yes_price'] > lower['yes_price']:
                        edge = higher['yes_price'] - lower['yes_price']
                        opportunity = {
                            'type': 'nested_threshold',
                            'higher_market': higher,
                            'lower_market': lower,
                            'edge': edge,
                            'strategy': f"Buy NO on {higher['title'][:30]} at {higher['yes_price']:.2f}, " +
                                       f"Buy YES on {lower['title'][:30]} at {lower['yes_price']:.2f}",
                            'expected_profit': edge * 100
                        }
                        opportunities.append(opportunity)
                        
                        print(f"\n⚠️  ARBITRAGE FOUND (Nested Threshold):")
                        print(f"   Higher (${higher['threshold']:,}): YES at {higher['yes_price']:.2f}")
                        print(f"   Lower  (${lower['threshold']:,}): YES at {lower['yes_price']:.2f}")
                        print(f"   Edge: {edge:.2f}¢ ({edge*100:.1f}%)")
                        print(f"   Strategy: {opportunity['strategy']}")
        
        # Type 2: Sum to less than $1.00 (buy both sides)
        print("\n\n📉 SUM-TO-ONE OPPORTUNITIES:")
        print("-" * 70)
        
        for market in market_data:
            yes_price = market['yes_price']
            no_price = market['no_price']
            total = yes_price + no_price
            
            if total < 0.98:  # Less than 98¢ combined
                edge = 1.00 - total
                opportunity = {
                    'type': 'sum_to_one',
                    'market': market,
                    'yes_price': yes_price,
                    'no_price': no_price,
                    'total': total,
                    'edge': edge,
                    'strategy': f"Buy BOTH YES ({yes_price:.2f}) and NO ({no_price:.2f}) on {market['title'][:30]}",
                    'expected_profit': edge * 100
                }
                opportunities.append(opportunity)
                
                print(f"\n💎 OPPORTUNITY: {market['title'][:40]}")
                print(f"   YES: {yes_price:.2f}¢ | NO: {no_price:.2f}¢ | Total: {total:.2f}¢")
                print(f"   Guaranteed profit: {edge:.2f}¢ per share ({edge*100:.1f}%)")
                print(f"   Strategy: Buy both sides")
        
        return opportunities
    
    def log_paper_trade(self, opportunity: Dict, position_size: float = 5.0):
        """Log a paper trade"""
        trade = {
            'timestamp': datetime.now().isoformat(),
            'type': opportunity['type'],
            'strategy': opportunity['strategy'],
            'edge': opportunity['edge'],
            'position_size': position_size,
            'expected_profit': opportunity['expected_profit'] * position_size / 100
        }
        
        self.paper_trades.append(trade)
        
        print(f"\n📝 PAPER TRADE LOGGED:")
        print(f"   Time: {trade['timestamp']}")
        print(f"   Type: {trade['type']}")
        print(f"   Strategy: {trade['strategy']}")
        print(f"   Position: ${position_size}")
        print(f"   Expected Profit: ${trade['expected_profit']:.2f}")
        
        return trade
    
    def generate_bankr_commands(self, opportunity: Dict, amount: int = 5) -> List[str]:
        """Generate Bankr CLI commands for execution"""
        commands = []
        
        if opportunity['type'] == 'nested_threshold':
            higher = opportunity['higher_market']
            lower = opportunity['lower_market']
            
            commands.append(f'npx bankr "buy {amount} dollars of NO on {higher["slug"]}"')
            commands.append(f'npx bankr "buy {amount} dollars of YES on {lower["slug"]}"')
            
        elif opportunity['type'] == 'sum_to_one':
            market = opportunity['market']
            
            commands.append(f'npx bankr "buy {amount} dollars of YES on {market["slug"]}"')
            commands.append(f'npx bankr "buy {amount} dollars of NO on {market["slug"]}"')
        
        return commands
    
    def save_paper_trades(self, filename: str = 'cross_market_paper_trades.json'):
        """Save paper trades to file"""
        with open(filename, 'w') as f:
            json.dump(self.paper_trades, f, indent=2)
        print(f"\n💾 Saved {len(self.paper_trades)} paper trades to {filename}")


def main():
    """Run cross-market arbitrage scanner"""
    print("\n" + "="*70)
    print("CROSS-MARKET ARBITRAGE PAPER TRADING SYSTEM")
    print("="*70 + "\n")
    
    arb = CrossMarketArbitrage()
    
    # Find opportunities
    opportunities = arb.find_cross_market_opportunities()
    
    print(f"\n\n{'='*70}")
    print(f"SCAN COMPLETE: Found {len(opportunities)} opportunities")
    print(f"{'='*70}\n")
    
    # Log paper trades for each opportunity
    for i, opp in enumerate(opportunities[:3], 1):  # Top 3 only
        print(f"\n--- Opportunity {i} ---")
        arb.log_paper_trade(opp, position_size=5.0)
        
        # Show Bankr commands
        commands = arb.generate_bankr_commands(opp, amount=5)
        print(f"\n💰 Bankr Commands:")
        for cmd in commands:
            print(f"   {cmd}")
    
    # Save results
    arb.save_paper_trades()
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("1. Review paper trades above")
    print("2. Run Bankr commands for real execution")
    print("3. Monitor positions until resolution")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
