#!/usr/bin/env python3
"""
Collect 10 paper trades for NBA cross-market arbitrage
"""

import os
import json
import requests
from datetime import datetime, timezone
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import base64

# Setup
key_id = os.getenv('KALSHI_API_KEY_ID')
key_file = os.getenv('KALSHI_KEY_FILE')

with open(key_file, 'r') as f:
    pem_data = f.read()
private_key = serialization.load_pem_private_key(pem_data.encode('utf-8'), password=None)

def kalshi_request(path, params=None):
    timestamp = str(int(datetime.now().timestamp()))
    message = f"{timestamp}GET{path}"
    signature = private_key.sign(message.encode('utf-8'), padding.PKCS1v15(), hashes.SHA256())
    sig_b64 = base64.b64encode(signature).decode('utf-8')
    headers = {
        'KALSHI-API-KEY-ID': key_id,
        'KALSHI-API-KEY-TIMESTAMP': timestamp,
        'KALSHI-API-KEY-SIGNATURE': sig_b64
    }
    response = requests.get(f"https://api.elections.kalshi.com/trade-api/v2{path}", headers=headers, params=params, timeout=10)
    return response.json() if response.status_code == 200 else {}

# Team mappings
PM_TO_K = {
    'PHI': '1PH', 'MIN': 'IMI', 'TOR': '2TO', 'MIL': 'RMI',
    'DAL': '2DA', 'IND': 'LIN', 'HOU': 'AHO', 'NYK': 'UNY',
    'ORL': '1OR', 'PHX': 'LPH', 'BOS': '2BO', 'LAL': 'SLA',
    'DEN': '2DE', 'GSW': 'NGS', 'SAC': '3SA', 'SAS': '3SA',
    'DET': 'SDE', 'CHI': 'TCH', 'POR': '2PO', 'LAC': 'LLA',
    'MEM': 'CME', 'MIA': 'MIA', 'ATL': 'NAT', 'BKN': '2BK',
    'CLE': '2CL', 'OKC': 'EOK', 'WAS': 'AWA', 'CHA': '2CH',
    'UTA': '3UT', 'NOP': 'INO'
}

TEAM_NAMES = {
    'PHI': '76ers', 'MIN': 'Timberwolves', 'TOR': 'Raptors', 'MIL': 'Bucks',
    'DAL': 'Mavericks', 'IND': 'Pacers', 'HOU': 'Rockets', 'NYK': 'Knicks',
    'ORL': 'Magic', 'PHX': 'Suns', 'BOS': 'Celtics', 'LAL': 'Lakers',
    'DEN': 'Nuggets', 'GSW': 'Warriors', 'SAC': 'Kings', 'SAS': 'Spurs',
    'DET': 'Pistons', 'CHI': 'Bulls', 'POR': 'Blazers', 'LAC': 'Clippers',
    'MEM': 'Grizzlies', 'MIA': 'Heat', 'ATL': 'Hawks', 'BKN': 'Nets',
    'CLE': 'Cavaliers', 'OKC': 'Thunder', 'WAS': 'Wizards', 'CHA': 'Hornets',
    'UTA': 'Jazz', 'NOP': 'Pelicans'
}

print("=" * 80)
print("COLLECTING 10 PAPER TRADES")
print("=" * 80)
print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n")

# Get Kalshi markets
print("📡 Fetching Kalshi NBA markets...")
kalshi_data = kalshi_request("/markets", {"series_ticker": "KXNBAGAME", "status": "open", "limit": 500})
k_markets = kalshi_data.get('markets', [])

# Organize by game
k_games = {}
for m in k_markets:
    event = m.get('event_ticker', '')
    ticker = m.get('ticker', '')
    title = m.get('title', '')
    
    if 'KXNBAGAME' not in event or 'winner' not in title.lower():
        continue
    
    parts = event.split('-')
    if len(parts) >= 2:
        date_teams = parts[1]
        if len(date_teams) >= 11:
            away_k = date_teams[6:9]
            home_k = date_teams[9:12]
            
            key = f"{away_k}-{home_k}"
            if key not in k_games:
                k_games[key] = {'away_k': away_k, 'home_k': home_k, 'teams': {}}
            
            yes = float(m.get('yes_ask_dollars') or m.get('yes_ask', 0) / 100)
            vol = m.get('volume_24h', 0)
            
            if away_k in ticker:
                k_games[key]['teams'][away_k] = {'yes': yes, 'vol': vol}
            elif home_k in ticker:
                k_games[key]['teams'][home_k] = {'yes': yes, 'vol': vol}

print(f"   ✅ {len(k_games)} Kalshi games")

# Get PM events
print("📡 Fetching Polymarket NBA games...")
pm_response = requests.get(
    "https://gamma-api.polymarket.com/events",
    params={"tag_slug": "nba", "active": "true", "closed": "false", "limit": 200},
    timeout=30
)

pm_events = pm_response.json()

# Collect paper trades
paper_trades = []
timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')

print("🔍 Matching games and collecting prices...")

for e in pm_events:
    if not isinstance(e, dict):
        continue
    
    slug = e.get('slug', '')
    if 'nba-' not in slug:
        continue
    
    parts = slug.split('-')
    if len(parts) < 4:
        continue
    
    away_pm = parts[1].upper()
    home_pm = parts[2].upper()
    
    if away_pm not in PM_TO_K or home_pm not in PM_TO_K:
        continue
    
    away_k = PM_TO_K[away_pm]
    home_k = PM_TO_K[home_pm]
    
    key1 = f"{away_k}-{home_k}"
    key2 = f"{home_k}-{away_k}"
    
    k_game = None
    if key1 in k_games:
        k_game = k_games[key1]
    elif key2 in k_games:
        k_game = k_games[key2]
    
    if not k_game:
        continue
    
    markets = e.get('markets', [])
    for m in markets:
        q = m.get('question', '').lower()
        if 'spread' in q or 'over' in q or 'under' in q:
            continue
        
        try:
            prices_raw = m.get('outcomePrices', '[]')
            outcomes = m.get('outcomes', '[]')
            
            if isinstance(prices_raw, str):
                prices = json.loads(prices_raw)
            else:
                prices = prices_raw
            
            if isinstance(outcomes, str):
                outcomes = json.loads(outcomes)
            
            if len(prices) < 2:
                continue
            
            for i, outcome in enumerate(outcomes):
                outcome_lower = outcome.lower()
                
                if away_pm.lower() in outcome_lower or TEAM_NAMES.get(away_pm, '').lower() in outcome_lower:
                    if away_k in k_game['teams']:
                        pm_price = float(prices[i])
                        k_data = k_game['teams'][away_k]
                        spread = abs(pm_price - k_data['yes'])
                        
                        paper_trades.append({
                            'game': f"{TEAM_NAMES.get(away_pm, away_pm)} @ {TEAM_NAMES.get(home_pm, home_pm)}",
                            'team': away_pm,
                            'team_name': TEAM_NAMES.get(away_pm, away_pm),
                            'pm_price': pm_price,
                            'k_price': k_data['yes'],
                            'spread': spread,
                            'pm_vol': float(e.get('volume24hr', 0)),
                            'k_vol': k_data['vol'],
                            'end_date': e.get('endDate'),
                            'timestamp': timestamp
                        })
                
                if home_pm.lower() in outcome_lower or TEAM_NAMES.get(home_pm, '').lower() in outcome_lower:
                    if home_k in k_game['teams']:
                        pm_price = float(prices[i])
                        k_data = k_game['teams'][home_k]
                        spread = abs(pm_price - k_data['yes'])
                        
                        paper_trades.append({
                            'game': f"{TEAM_NAMES.get(home_pm, home_pm)} vs {TEAM_NAMES.get(away_pm, away_pm)}",
                            'team': home_pm,
                            'team_name': TEAM_NAMES.get(home_pm, home_pm),
                            'pm_price': pm_price,
                            'k_price': k_data['yes'],
                            'spread': spread,
                            'pm_vol': float(e.get('volume24hr', 0)),
                            'k_vol': k_data['vol'],
                            'end_date': e.get('endDate'),
                            'timestamp': timestamp
                        })
        except:
            pass

print(f"   ✅ Found {len(paper_trades)} comparable prices")

# Sort and take top 10
paper_trades.sort(key=lambda x: -x['spread'])
paper_trades = paper_trades[:10]

print(f"\n📝 Logging top {len(paper_trades)} paper trades...")

# Build log content
lines = [
    "# Paper Trade Log - Batch #1",
    f"**Collection Time:** {timestamp}",
    "**Strategy:** NBA Cross-Market Arbitrage",
    "",
    "## Summary",
    f"- **Total opportunities found:** {len(paper_trades)}",
    "- **Data collection target:** 10 trades",
    "- **Status:** ACTIVE (monitoring for resolution)",
    "",
    "---",
    ""
]

for i, trade in enumerate(paper_trades, 1):
    if trade['pm_price'] < trade['k_price']:
        action = f"BUY Polymarket YES @ {trade['pm_price']:.2f}¢ + BUY Kalshi NO @ {1-trade['k_price']:.2f}¢"
        cost = trade['pm_price'] + (1 - trade['k_price'])
    else:
        action = f"BUY Kalshi YES @ {trade['k_price']:.2f}¢ + BUY Polymarket NO @ {1-trade['pm_price']:.2f}¢"
        cost = trade['k_price'] + (1 - trade['pm_price'])
    
    profit = 1 - cost
    profit_after_fees = max(0, profit - 0.037)
    execute = "EXECUTE" if trade['spread'] > 0.04 else "PAPER ONLY"
    
    lines.extend([
        f"## Trade #{i}: {trade['game']} ({trade['team_name']})",
        "",
        f"**Entry Time:** {trade['timestamp']}",
        f"**Resolution Date:** {trade['end_date']}",
        "**Status:** PAPER TRADE ACTIVE",
        "",
        "### Prices",
        "| Platform | Side | Price | Volume |",
        "|----------|------|-------|--------|",
        f"| Polymarket | YES | {trade['pm_price']:.2f}¢ | ${trade['pm_vol']:,.0f} |",
        f"| Kalshi | YES | {trade['k_price']:.2f}¢ | ${trade['k_vol']:,} |",
        "",
        "### Analysis",
        f"- **Spread:** {trade['spread']:.2f} ({trade['spread']*100:.1f}%)",
        f"- **Action:** {action}",
        f"- **Total Cost:** {cost:.2f}¢ per pair",
        "- **Expected Payout:** $1.00 per pair",
        f"- **Gross Profit:** {profit:.2f}¢ ({profit*100:.1f}%)",
        f"- **After Fees (3.7%):** {profit_after_fees:.2f}¢ ({profit_after_fees*100:.1f}%)",
        "",
        "### Paper Trade Execution",
        f"**Action:** {execute}",
        "",
        "**Leg 1 (Execute First - Less Liquid):**",
        "- [ ] Check order book depth",
        "- [ ] Place order",
        "- [ ] Confirm fill price",
        "",
        "**Leg 2 (Execute Second):**",
        "- [ ] Check order book depth",
        "- [ ] Place order",
        "- [ ] Confirm fill price",
        "",
        "**Actual Fill Prices:**",
        "- Leg 1: ___¢",
        "- Leg 2: ___¢",
        "- Total Cost: ___¢",
        "",
        "**Resolution:**",
        "- [ ] Wait for game outcome",
        "- [ ] Record winner",
        "- [ ] Calculate actual P/L",
        "",
        "**Notes:**",
        "_(Add execution notes here)_",
        "",
        "---",
        ""
    ])

arb_count = sum(1 for t in paper_trades if t['spread'] > 0.04)
lines.extend([
    "## Batch Summary",
    "",
    f"- **Total logged:** {len(paper_trades)}",
    f"- **Arbitrage (>{4}%):** {arb_count}",
    f"- **Paper only (<{4}%):** {len(paper_trades) - arb_count}",
    "",
    "Next: Monitor for resolution and update with actual results",
    ""
])

# Write to file
log_file = "/Users/thekhemist/.openclaw/workspace/memory/trading/paper-trades-10-batch.md"
with open(log_file, 'w') as f:
    f.write('\n'.join(lines))

print(f"\n✅ {len(paper_trades)} paper trades logged to:")
print(f"   {log_file}")

print("\n" + "=" * 80)
print("PAPER TRADE SUMMARY")
print("=" * 80)

for i, trade in enumerate(paper_trades, 1):
    status = "🚨 ARB" if trade['spread'] > 0.04 else "📊 PAPER"
    print(f"{i:2}. {status} | {trade['game']}")
    print(f"    Spread: {trade['spread']*100:.1f}% | PM: {trade['pm_price']:.2f}¢ | K: {trade['k_price']:.2f}¢")

print(f"\nTotal: {len(paper_trades)} trades")
print(f"Arbitrage (>4%): {arb_count}")
print(f"Paper only (<4%): {len(paper_trades) - arb_count}")

print("\n" + "=" * 80)
print("DATA COLLECTION COMPLETE")
print("=" * 80)
print("""
Next steps:
1. Monitor these 10 trades until game resolution
2. Track actual outcomes vs expected  
3. Update log with fill prices and results
4. Calculate real P/L vs theoretical
5. Run 10 more trades for 20 total
""")
