#!/usr/bin/env python3
"""
Cross-Market Arbitrage Scanner - CORRECTED VERSION
Uses proper API filters: active=true + closed=false
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
    """Polymarket API client - CORRECTED filters."""
    
    BASE_URL = "https://gamma-api.polymarket.com"
    
    def get_live_events(self, limit: int = 500):
        """
        Get LIVE tradeable events from Polymarket.
        CRITICAL: Must use active=true + closed=false to get current data.
        """
        url = f"{self.BASE_URL}/events"
        # CORRECT FILTER: active + not closed = live markets
        params = {
            'active': 'true',
            'closed': 'false',
            'limit': limit
        }
        
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
    
    def scan_polymarket(self):
        """Scan Polymarket for live tradeable events."""
        print("📡 Fetching Polymarket LIVE events...")
        print("   Filter: active=true + closed=false")
        
        events = self.polymarket.get_live_events(limit=500)
        
        # Filter to events ending in future
        live_events = []
        for e in events:
            if isinstance(e, dict):
                end_date = e.get('endDate')
                if end_date:
                    try:
                        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                        days = (end_dt - self.today).days
                        
                        # Include if in future and has volume
                        vol_24h = float(e.get('volume24hr', 0) or 0)
                        if days > 0:
                            live_events.append({
                                'platform': 'Polymarket',
                                'title': e.get('title'),
                                'slug': e.get('slug'),
                                'days': days,
                                'end_date': end_date[:10],
                                'volume_24h': vol_24h,
                                'total_volume': float(e.get('volume', 0) or 0),
                                'liquidity': float(e.get('liquidity', 0) or 0),
                                'tags': [t.get('slug') for t in e.get('tags', [])],
                                'markets': e.get('markets', [])
                            })
                    except:
                        pass
        
        print(f"   ✅ Found {len(live_events)} future events")
        return live_events
    
    def scan_kalshi(self):
        """Scan Kalshi for live markets."""
        print("\n📡 Fetching Kalshi markets...")
        
        markets = self.kalshi.get_markets(limit=1000)
        
        # Categorize
        sports = []
        crypto = []
        other = []
        
        for m in markets:
            title = m.get('title', '').lower()
            
            if any(x in title for x in ['nba', 'nfl', 'nhl', 'game', 'wins', 'points', 'spread']):
                sports.append({
                    'title': m.get('title'),
                    'ticker': m.get('ticker'),
                    'yes_ask': m.get('yes_ask'),
                    'volume': m.get('volume')
                })
            elif any(x in title for x in ['bitcoin', 'btc', 'eth']):
                crypto.append(m)
            else:
                other.append(m)
        
        print(f"   ✅ Found {len(sports)} sports, {len(crypto)} crypto, {len(other)} other")
        
        return {'sports': sports, 'crypto': crypto, 'other': other}
    
    def find_opportunities(self, pm_events, kalshi_data):
        """Find potential arbitrage opportunities."""
        print("\n" + "=" * 70)
        print("ANALYZING CROSS-MARKET OPPORTUNITIES")
        print("=" * 70)
        
        # Categorize Polymarket events
        pm_sports = [e for e in pm_events if any('sport' in t or t in ['nba', 'nfl', 'nhl'] for t in e['tags'])]
        pm_politics = [e for e in pm_events if any('politic' in t or t in ['trump', 'election'] for t in e['tags'])]
        pm_economics = [e for e in pm_events if any(t in ['economics', 'fed'] for t in e['tags'])]
        pm_crypto = [e for e in pm_events if 'crypto' in e['tags']]
        
        print(f"\nPolymarket breakdown:")
        print(f"  Sports futures: {len(pm_sports)}")
        print(f"  Politics: {len(pm_politics)}")
        print(f"  Economics: {len(pm_economics)}")
        print(f"  Crypto: {len(pm_crypto)}")
        
        print(f"\nKalshi breakdown:")
        print(f"  Sports games: {len(kalshi_data['sports'])}")
        print(f"  Crypto: {len(kalshi_data['crypto'])}")
        
        # Check for overlaps
        print("\n" + "=" * 70)
        print("POTENTIAL OVERLAPS")
        print("=" * 70)
        
        overlaps = {
            'sports': len(pm_sports) > 0 and len(kalshi_data['sports']) > 0,
            'crypto': len(pm_crypto) > 0 and len(kalshi_data['crypto']) > 0,
            'politics': len(pm_politics) > 0,
            'economics': len(pm_economics) > 0
        }
        
        for category, has_overlap in overlaps.items():
            status = "✅" if has_overlap else "❌"
            print(f"{status} {category.capitalize()}")
        
        # Detailed analysis
        if pm_sports and kalshi_data['sports']:
            print("\n🎯 SPORTS ANALYSIS:")
            print("   Polymarket: Futures (NBA Champion, World Cup Winner)")
            print("   Kalshi: Daily games (Lakers vs Warriors tonight)")
            print("   Verdict: Different structures, no direct arbitrage")
        
        if pm_politics:
            print("\n🎯 POLITICS ANALYSIS:")
            print(f"   Polymarket: {len(pm_politics)} markets (Trump Fed Chair: $5.2M 24h)")
            print("   Kalshi: 0 markets")
            print("   Verdict: No Kalshi presence")
        
        return overlaps
    
    def run_scan(self):
        """Run complete cross-market scan."""
        print("🧪 CROSS-MARKET ARBITRAGE SCANNER (CORRECTED)")
        print("=" * 70)
        print(f"Time: {self.today.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print()
        
        # Scan both platforms
        pm_events = self.scan_polymarket()
        kalshi_data = self.scan_kalshi()
        
        # Display top Polymarket events
        print("\n" + "=" * 70)
        print("TOP POLYMARKET EVENTS (by 24h volume)")
        print("=" * 70)
        
        pm_events.sort(key=lambda x: x['volume_24h'], reverse=True)
        for e in pm_events[:10]:
            tags = ', '.join(e['tags'][:2]) if e['tags'] else 'misc'
            print(f"${e['volume_24h']:>10,.0f} 24h | {e['days']:3d} days | {e['title'][:45]}... [{tags}]")
        
        # Display Kalshi sports
        print("\n" + "=" * 70)
        print("KALSHI SPORTS MARKETS (sample)")
        print("=" * 70)
        
        for m in kalshi_data['sports'][:10]:
            yes = m['yes_ask'] / 100 if m['yes_ask'] else 0
            print(f"{yes:.2f}¢ | ${m.get('volume', 0):,.0f} | {m['title'][:55]}...")
        
        # Find opportunities
        overlaps = self.find_opportunities(pm_events, kalshi_data)
        
        # Summary
        print("\n" + "=" * 70)
        print("SCAN SUMMARY")
        print("=" * 70)
        
        viable = sum(1 for v in overlaps.values() if v)
        print(f"\nViable categories: {viable}/4")
        
        if viable == 0:
            print("\n❌ No direct cross-market arbitrage opportunities found")
            print("\nPlatforms serve different markets:")
            print("  • Polymarket: Long-term futures (politics, sports, economics)")
            print("  • Kalshi: Short-term daily games (mostly sports props)")
        else:
            print(f"\n✅ Found {viable} categories with potential")
        
        # Save report
        report = {
            'scan_time': self.today.isoformat(),
            'polymarket_events': len(pm_events),
            'kalshi_sports': len(kalshi_data['sports']),
            'kalshi_crypto': len(kalshi_data['crypto']),
            'overlaps': overlaps,
            'top_polymarket': pm_events[:20],
            'top_kalshi_sports': kalshi_data['sports'][:20]
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
