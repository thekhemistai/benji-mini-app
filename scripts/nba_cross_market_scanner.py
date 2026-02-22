#!/usr/bin/env python3
"""
NBA Cross-Market Arbitrage Scanner - OPERATIONAL
Scans Polymarket vs Kalshi for price discrepancies on NBA games.
Logs opportunities to memory/trading/arb-results.md
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64

# ========== CONFIGURATION ==========
MIN_SPREAD = 0.04  # 4% minimum for profit after fees
KALSHI_KEY_ID = os.getenv('KALSHI_API_KEY_ID')
KALSHI_KEY_FILE = os.getenv('KALSHI_KEY_FILE')

# Team code mapping: Kalshi -> Polymarket
KALSHI_TO_PM = {
    '1OR': 'ORL', '2OR': 'ORL', 'ORL': 'ORL',
    'LPH': 'PHX', 'RPH': 'PHX', 'PHX': 'PHX',
    '1PH': 'PHI', '2PH': 'PHI', 'PHI': 'PHI',
    'INO': 'NOP', 'NOP': 'NOP',
    '3SA': 'SAC', '1SA': 'SAC', 'SAC': 'SAC', 'CSA': 'SAC',
    'CME': 'MEM', 'MEM': 'MEM', '1ME': 'MEM', 'MMI': 'MEM',
    '3UT': 'UTA', 'UTA': 'UTA',
    'AHO': 'HOU', 'HOU': 'HOU', '1HO': 'HOU', 'UNY': 'NYK',
    '3SA': 'SAS', 'SAS': 'SAS', 'SDE': 'DET', 'DET': 'DET', '1DE': 'DET', 'TCH': 'CHI',
    'CHI': 'CHI', 'KCH': 'CHI', '2PO': 'POR', 'POR': 'POR', 'RPH': 'PHX',
    'LLA': 'LAC', 'LAC': 'LAC', '2OR': 'ORL',
    '2NY': 'NYK', 'NYK': 'NYK', '2CH': 'CHA', 'CHA': 'CHA',
    'AWA': 'WAS', 'WAS': 'WAS', '2PH': 'PHI', 'IMI': 'MIN',
    '2BO': 'BOS', 'BOS': 'BOS', 'SLA': 'LAL', 'LAL': 'LAL',
    '2DA': 'DAL', 'DAL': 'DAL', 'LIN': 'IND', 'IND': 'IND',
    '2DE': 'DEN', 'DEN': 'DEN', 'NGS': 'GSW', 'GSW': 'GSW',
    '2BK': 'BKN', 'BKN': 'BKN', 'NAT': 'ATL', 'ATL': 'ATL',
    '2TO': 'TOR', 'TOR': 'TOR', 'RMI': 'MIL', 'MIL': 'MIL',
    '2CL': 'CLE', 'CLE': 'CLE', 'EOK': 'OKC', 'OKC': 'OKC',
    'MIA': 'MIA',
}

TEAM_NAMES = {
    'ORL': 'Magic', 'PHX': 'Suns', 'PHI': '76ers', 'NOP': 'Pelicans',
    'SAC': 'Kings', 'SAS': 'Spurs', 'DET': 'Pistons', 'CHI': 'Bulls',
    'HOU': 'Rockets', 'NYK': 'Knicks', 'MEM': 'Grizzlies', 'MIA': 'Heat',
    'DEN': 'Nuggets', 'GSW': 'Warriors', 'CLE': 'Cavaliers', 'OKC': 'Thunder',
    'POR': 'Blazers', 'BOS': 'Celtics', 'LAL': 'Lakers', 'TOR': 'Raptors',
    'MIL': 'Bucks', 'LAC': 'Clippers', 'DAL': 'Mavericks', 'IND': 'Pacers',
    'BKN': 'Nets', 'ATL': 'Hawks', 'WAS': 'Wizards', 'CHA': 'Hornets',
    'UTA': 'Jazz', 'MIN': 'Timberwolves'
}


class KalshiClient:
    """Kalshi API client."""
    
    def __init__(self):
        self.key_id = KALSHI_KEY_ID
        self.key_file = KALSHI_KEY_FILE
        
        with open(self.key_file, 'r') as f:
            pem_data = f.read()
        self.private_key = serialization.load_pem_private_key(pem_data.encode('utf-8'), password=None)
    
    def request(self, path, params=None):
        timestamp = str(int(datetime.now().timestamp()))
        message = f"{timestamp}GET{path}"
        signature = self.private_key.sign(message.encode('utf-8'), padding.PKCS1v15(), hashes.SHA256())
        sig_b64 = base64.b64encode(signature).decode('utf-8')
        
        headers = {
            'KALSHI-API-KEY-ID': self.key_id,
            'KALSHI-API-KEY-TIMESTAMP': timestamp,
            'KALSHI-API-KEY-SIGNATURE': sig_b64
        }
        
        response = requests.get(
            f"https://api.elections.kalshi.com/trade-api/v2{path}",
            headers=headers,
            params=params,
            timeout=10
        )
        return response.json() if response.status_code == 200 else {}
    
    def get_nba_games(self):
        """Get NBA daily games with moneylines."""
        markets_data = self.request("/markets", {"series_ticker": "KXNBAGAME", "status": "open", "limit": 500})
        markets = markets_data.get('markets', [])
        
        games = {}
        for m in markets:
            title = m.get('title', '')
            event = m.get('event_ticker', '')
            
            if 'winner' in title.lower() and 'KXNBAGAME' in event:
                date_teams = event.split('-')[1] if '-' in event else ''
                if len(date_teams) >= 11:
                    away_k = date_teams[6:9]
                    home_k = date_teams[9:12]
                    
                    away_pm = KALSHI_TO_PM.get(away_k, away_k)
                    home_pm = KALSHI_TO_PM.get(home_k, home_k)
                    
                    yes_price = m.get('yes_ask_dollars') or (m.get('yes_ask', 0) / 100)
                    vol = m.get('volume_24h', 0)
                    
                    key = f"{away_pm} vs {home_pm}"
                    if key not in games or vol > games[key].get('vol', 0):
                        games[key] = {
                            'away': away_pm,
                            'home': home_pm,
                            'yes': float(yes_price) if yes_price else 0,
                            'vol': vol,
                            'title': title
                        }
        
        return games


class PolymarketClient:
    """Polymarket API client."""
    
    def get_nba_games(self):
        """Get NBA games with volume."""
        response = requests.get(
            "https://gamma-api.polymarket.com/events",
            params={"tag_slug": "nba", "active": "true", "closed": "false", "limit": 200},
            timeout=30
        )
        
        events = response.json()
        today = datetime.now(timezone.utc)
        
        games = {}
        for e in events:
            if not isinstance(e, dict):
                continue
            
            vol_24h = float(e.get('volume24hr', 0) or 0)
            if vol_24h < 10000:
                continue
            
            end = e.get('endDate')
            if not end:
                continue
            
            try:
                end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
                days = (end_dt - today).days
                if days > 2 or days < -1:
                    continue
            except:
                continue
            
            slug = e.get('slug', '')
            if 'nba-' in slug:
                parts = slug.split('-')
                if len(parts) >= 4:
                    away = parts[1].upper()
                    home = parts[2].upper()
                    
                    markets = e.get('markets', [])
                    if markets:
                        try:
                            prices_raw = markets[0].get('outcomePrices')
                            if prices_raw:
                                if isinstance(prices_raw, str):
                                    prices = json.loads(prices_raw)
                                else:
                                    prices = prices_raw
                                
                                if isinstance(prices, list) and len(prices) > 0:
                                    yes = float(prices[0])
                                    key = f"{away} vs {home}"
                                    games[key] = {
                                        'yes': yes,
                                        'vol': vol_24h,
                                        'days': days
                                    }
                        except:
                            pass
        
        return games


def log_opportunity(match, timestamp):
    """Log arbitrage opportunity to file."""
    log_file = "/Users/thekhemist/.openclaw/workspace/memory/trading/arb-results.md"
    
    status = "LIVE" if match['days'] < 0 else f"T+{match['days']}"
    
    log_entry = f"""
## Cross-Market Arb | {match['game']} | {timestamp}

**Status:** {status}
**Platforms:** Polymarket vs Kalshi

### Prices
- Polymarket YES: {match['pm_yes']:.2f}¢ | ${match['pm_vol']:,.0f} vol
- Kalshi YES: {match['k_yes']:.2f}¢ | ${match['k_vol']:,.0f} vol
- **Spread: {match['spread']:.2f} ({match['spread']*100:.1f}%)**

### Action
"""
    
    if match['pm_yes'] > match['k_yes']:
        no_pm = 1 - match['pm_yes']
        cost = match['k_yes'] + no_pm
        profit = 1 - cost
        log_entry += f"""- Buy Kalshi YES @ {match['k_yes']:.2f}¢
- Buy Polymarket NO @ {no_pm:.2f}¢
- Total cost: {cost:.2f}¢
- **Gross profit: {profit:.2f}¢ ({profit*100:.1f}%)**
"""
    else:
        no_k = 1 - match['k_yes']
        cost = match['pm_yes'] + no_k
        profit = 1 - cost
        log_entry += f"""- Buy Polymarket YES @ {match['pm_yes']:.2f}¢
- Buy Kalshi NO @ {no_k:.2f}¢
- Total cost: {cost:.2f}¢
- **Gross profit: {profit:.2f}¢ ({profit*100:.1f}%)**
"""
    
    log_entry += f"""
### Paper Trade
- [ ] Check order book depth on both platforms
- [ ] Execute less liquid side first
- [ ] Log fill prices
- [ ] Calculate net profit after fees

---
"""
    
    with open(log_file, 'a') as f:
        f.write(log_entry)


def run_scan():
    """Execute full cross-market scan."""
    print("=" * 80)
    print("NBA CROSS-MARKET ARBITRAGE SCANNER")
    print("=" * 80)
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Min spread: {MIN_SPREAD*100:.0f}%\n")
    
    # Fetch from both platforms
    kalshi = KalshiClient()
    polymarket = PolymarketClient()
    
    print("📡 Fetching Kalshi NBA games...")
    kalshi_games = kalshi.get_nba_games()
    print(f"   ✅ {len(kalshi_games)} games")
    
    print("📡 Fetching Polymarket NBA games...")
    pm_games = polymarket.get_nba_games()
    print(f"   ✅ {len(pm_games)} games\n")
    
    # Find matches
    matches = []
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    
    for pm_key, pm_data in pm_games.items():
        if pm_key in kalshi_games:
            k_data = kalshi_games[pm_key]
            spread = abs(pm_data['yes'] - k_data['yes'])
            away, home = pm_key.split(' vs ')
            
            match = {
                'game': f"{TEAM_NAMES.get(away, away)} vs {TEAM_NAMES.get(home, home)}",
                'pm_yes': pm_data['yes'],
                'k_yes': k_data['yes'],
                'pm_vol': pm_data['vol'],
                'k_vol': k_data['vol'],
                'spread': spread,
                'days': pm_data.get('days', 0)
            }
            matches.append(match)
            
            # Log if above threshold
            if spread >= MIN_SPREAD:
                log_opportunity(match, timestamp)
    
    # Display results
    print("=" * 80)
    print(f"Found {len(matches)} matching games")
    print("=" * 80)
    
    if not matches:
        print("\n⚠️ No matching games found")
        return
    
    # Sort by spread
    matches.sort(key=lambda x: -x['spread'])
    
    arb_count = 0
    for m in matches:
        status = "🔴 LIVE" if m['days'] < 0 else f"⏳ T+{m['days']}"
        
        print(f"\n{status} | {m['game']}")
        print(f"   PM: {m['pm_yes']:.2f}¢ | K: {m['k_yes']:.2f}¢ | Spread: {m['spread']*100:.1f}%")
        
        if m['spread'] >= MIN_SPREAD:
            print(f"   🚨 ARBITRAGE (logged to arb-results.md)")
            arb_count += 1
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total games: {len(matches)}")
    print(f"Arbitrage ops (>{MIN_SPREAD*100:.0f}%): {arb_count}")
    
    if arb_count > 0:
        print(f"\n✅ {arb_count} opportunities logged to memory/trading/arb-results.md")


if __name__ == "__main__":
    run_scan()
