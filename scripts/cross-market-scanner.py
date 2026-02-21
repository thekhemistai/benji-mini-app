#!/usr/bin/env python3
"""
Cross-Market Arbitrage Scanner - LIVE Sports
Monitors Polymarket /events endpoint and Kalshi API for price discrepancies.
"""

import os
import sys
import json
import base64
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# Load environment
load_dotenv('/Users/thekhemist/.openclaw/workspace/.env')

class KalshiClient:
    """Kalshi API client with RSA authentication."""
    
    BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
    
    def __init__(self):
        self.key_id = os.getenv('KALSHI_API_KEY_ID')
        key_file = os.getenv('KALSHI_KEY_FILE')
        
        with open(key_file, 'r') as f:
            pem_data = f.read()
        self.private_key = serialization.load_pem_private_key(pem_data.encode('utf-8'), password=None)
    
    def _sign_request(self, method: str, path: str) -> dict:
        timestamp = str(int(datetime.now().timestamp()))
        message = f"{timestamp}{method}{path}"
        signature = self.private_key.sign(message.encode('utf-8'), padding.PKCS1v15(), hashes.SHA256())
        sig_b64 = base64.b64encode(signature).decode('utf-8')
        
        return {
            'KALSHI-API-KEY-ID': self.key_id,
            'KALSHI-API-KEY-TIMESTAMP': timestamp,
            'KALSHI-API-KEY-SIGNATURE': sig_b64
        }
    
    def get_markets(self, limit: int = 1000):
        """Get all active markets from Kalshi."""
        url = f"{self.BASE_URL}/markets"
        headers = self._sign_request("GET", "/markets")
        
        try:
            response = requests.get(url, headers=headers, params={'limit': limit}, timeout=10)
            if response.status_code == 200:
                return response.json().get('markets', [])
            else:
                print(f"❌ Kalshi API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Kalshi request failed: {e}")
            return []


class PolymarketClient:
    """Polymarket API client - uses /events endpoint for live data."""
    
    BASE_URL = "https://gamma-api.polymarket.com"
    
    def get_sports_events(self, tag: str = "sports", limit: int = 200):
        """Get live sports events from Polymarket."""
        url = f"{self.BASE_URL}/events"
        params = {'tag_slug': tag, 'limit': limit}
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Polymarket API error: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Polymarket request failed: {e}")
            return []
    
    def get_event_by_slug(self, slug: str):
        """Get specific event by slug."""
        url = f"{self.BASE_URL}/events"
        params = {'slug': slug}
        
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data[0] if data else None
            else:
                return None
        except Exception as e:
            print(f"❌ Failed to fetch event: {e}")
            return None


class CrossMarketScanner:
    """Scans for arbitrage opportunities between Polymarket and Kalshi."""
    
    def __init__(self):
        self.kalshi = KalshiClient()
        self.polymarket = PolymarketClient()
        self.today = datetime.now(timezone.utc)
    
    def find_upcoming_games(self, days_ahead: int = 7):
        """Find upcoming games on both platforms."""
        print("🔍 Scanning for upcoming games...")
        print("=" * 70)
        
        # Get Polymarket events
        print("\n📡 Fetching Polymarket sports events...")
        pm_events = self.polymarket.get_sports_events(limit=200)
        
        # Filter to upcoming games
        upcoming_pm = []
        for e in pm_events:
            if isinstance(e, dict) and not e.get('ended', False):
                end_date = e.get('endDate')
                if end_date:
                    try:
                        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                        days = (end - self.today).days
                        if 0 <= days <= days_ahead:
                            upcoming_pm.append({
                                'platform': 'Polymarket',
                                'title': e.get('title'),
                                'slug': e.get('slug'),
                                'days': days,
                                'end_date': end_date,
                                'volume': float(e.get('volume', 0) or 0),
                                'liquidity': float(e.get('liquidity', 0) or 0),
                                'markets': e.get('markets', [])
                            })
                    except:
                        pass
        
        print(f"   ✅ Found {len(upcoming_pm)} upcoming Polymarket events")
        
        # Get Kalshi markets
        print("\n📡 Fetching Kalshi markets...")
        kalshi_markets = self.kalshi.get_markets(limit=1000)
        
        # Filter to sports markets
        sports_keywords = ['nba', 'nfl', 'nhl', 'mlb', 'soccer', 'game', 'vs', 'win', 'spread', 'points']
        upcoming_kalshi = []
        
        for m in kalshi_markets:
            title = m.get('title', '').lower()
            if any(kw in title for kw in sports_keywords):
                upcoming_kalshi.append({
                    'platform': 'Kalshi',
                    'title': m.get('title'),
                    'ticker': m.get('ticker'),
                    'yes_ask': m.get('yes_ask'),
                    'no_ask': m.get('no_ask'),
                    'volume': m.get('volume')
                })
        
        print(f"   ✅ Found {len(upcoming_kalshi)} Kalshi sports markets")
        
        return upcoming_pm, upcoming_kalshi
    
    def find_matches(self, pm_events, kalshi_markets):
        """Find potential matches between platforms."""
        print("\n" + "=" * 70)
        print("FINDING CROSS-MARKET MATCHES")
        print("=" * 70)
        
        matches = []
        
        for pm in pm_events:
            pm_title = pm['title'].lower()
            
            # Extract team names
            teams = []
            common_teams = [
                'manchester', 'city', 'newcastle', 'liverpool', 'arsenal', 'chelsea',
                'lakers', 'warriors', 'celtics', 'bulls', 'knicks', 'heat',
                'chiefs', 'eagles', 'ravens', '49ers', 'cowboys',
                'braves', 'yankees', 'dodgers', 'red sox'
            ]
            
            for team in common_teams:
                if team in pm_title:
                    teams.append(team)
            
            # Find matching Kalshi markets
            for kal in kalshi_markets:
                kal_title = kal['title'].lower()
                
                # Check if any team names match
                if teams and all(team in kal_title for team in teams):
                    matches.append({
                        'polymarket': pm,
                        'kalshi': kal,
                        'teams': teams
                    })
        
        return matches
    
    def calculate_arbitrage(self, matches):
        """Calculate potential arbitrage opportunities."""
        print(f"\n📊 Analyzing {len(matches)} potential matches...")
        
        opportunities = []
        
        for match in matches:
            pm = match['polymarket']
            kal = match['kalshi']
            
            # Get Polymarket prices
            pm_markets = pm.get('markets', [])
            if not pm_markets:
                continue
            
            # Find moneyline market (typically first)
            pm_market = pm_markets[0]
            pm_prices = pm_market.get('outcomePrices', [])
            
            if pm_prices and len(pm_prices) >= 2:
                try:
                    pm_yes = float(pm_prices[0])
                    pm_no = float(pm_prices[1])
                except:
                    continue
            else:
                continue
            
            # Get Kalshi prices
            kal_yes = kal.get('yes_ask', 0) / 100 if kal.get('yes_ask') else 0
            kal_no = kal.get('no_ask', 0) / 100 if kal.get('no_ask') else 0
            
            # Calculate spreads
            spread_yes = abs(pm_yes - kal_yes)
            spread_no = abs(pm_no - kal_no)
            
            if spread_yes > 0.05 or spread_no > 0.05:  # >5% difference
                opportunities.append({
                    'match': match,
                    'pm_yes': pm_yes,
                    'pm_no': pm_no,
                    'kal_yes': kal_yes,
                    'kal_no': kal_no,
                    'spread_yes': spread_yes,
                    'spread_no': spread_no
                })
        
        return opportunities
    
    def run_scan(self):
        """Run complete cross-market scan."""
        print("🧪 CROSS-MARKET ARBITRAGE SCANNER")
        print("=" * 70)
        print(f"Time: {self.today.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
        
        # Find upcoming games
        pm_events, kalshi_markets = self.find_upcoming_games(days_ahead=7)
        
        # Display upcoming games
        print("\n" + "=" * 70)
        print("UPCOMING POLYMARKET EVENTS")
        print("=" * 70)
        
        for e in sorted(pm_events, key=lambda x: x['days'])[:10]:
            print(f"\n  📊 {e['title'][:60]}")
            print(f"     End: {e['end_date'][:10]} ({e['days']} days)")
            print(f"     Vol: ${e['volume']:,.0f} | Liq: ${e['liquidity']:,.0f}")
            
            for m in e['markets'][:2]:
                prices = m.get('outcomePrices', [])
                if prices:
                    try:
                        yes = float(prices[0])
                        print(f"     • {m['question'][:45]}... ({yes:.2f})")
                    except:
                        print(f"     • {m['question'][:45]}...")
        
        print("\n" + "=" * 70)
        print("KALSHI SPORTS MARKETS (Sample)")
        print("=" * 70)
        
        for m in kalshi_markets[:10]:
            yes = m.get('yes_ask', 0) / 100 if m.get('yes_ask') else 0
            print(f"  {m['title'][:60]}")
            print(f"     Yes: {yes:.2f}¢ | Vol: ${m.get('volume', 0):,.0f}")
        
        # Find matches
        matches = self.find_matches(pm_events, kalshi_markets)
        
        if matches:
            print(f"\n✅ Found {len(matches)} potential matches!")
            
            # Check for arbitrage
            opportunities = self.calculate_arbitrage(matches)
            
            if opportunities:
                print(f"\n🚨 ARBITRAGE OPPORTUNITIES: {len(opportunities)}")
                print("=" * 70)
                
                for opp in opportunities:
                    pm = opp['match']['polymarket']
                    kal = opp['match']['kalshi']
                    
                    print(f"\n  📈 {pm['title'][:50]}")
                    print(f"     Polymarket: Yes {opp['pm_yes']:.2f}¢ | No {opp['pm_no']:.2f}¢")
                    print(f"     Kalshi:     Yes {opp['kal_yes']:.2f}¢ | No {opp['kal_no']:.2f}¢")
                    print(f"     Spread:     Yes {opp['spread_yes']:.2f} ({opp['spread_yes']*100:.0f}%)")
            else:
                print("\nℹ️  No arbitrage opportunities found (>5% spread)")
        else:
            print("\n❌ No matching events found between platforms")
            print("\nPossible reasons:")
            print("  • Different market structures (moneyline vs props)")
            print("  • Different game schedules")
            print("  • No overlapping games currently")
        
        # Save report
        report = {
            'scan_time': self.today.isoformat(),
            'polymarket_count': len(pm_events),
            'kalshi_count': len(kalshi_markets),
            'matches': len(matches),
            'opportunities': len(opportunities) if matches else 0,
            'polymarket_events': pm_events,
            'kalshi_markets': kalshi_markets
        }
        
        output_file = f"/Users/thekhemist/.openclaw/workspace/memory/trading/cross_market_scan_{self.today.strftime('%Y%m%d_%H%M')}.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📝 Report saved: {output_file}")


def main():
    """Main entry point."""
    scanner = CrossMarketScanner()
    scanner.run_scan()


if __name__ == '__main__':
    main()
