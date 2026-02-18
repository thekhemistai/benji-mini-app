#!/usr/bin/env python3
"""
SOL 5m Polymarket Trader - Tracks "SOL Price Up/Down (5m)"
"""

import json
import time
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests

DATA_DIR = Path(__file__).resolve().parent / "data"
LOG_DIR = Path(__file__).resolve().parent / "logs"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"
for d in [DATA_DIR, LOG_DIR, REPORTS_DIR]:
    d.mkdir(exist_ok=True)

CONFIG = {
    "ASSET": "SOL",
    "MARKET_NAME": "SOL Price Up/Down (5m)",
    "WINDOW_MINUTES": 5,
    "PRICE_THRESHOLD": 0.009,       # 0.9% for SOL (higher volatility)
    "EDGE_THRESHOLD": 0.05,          # 5% edge
    "MAX_DAILY_TRADES": 15,          # Lower limit due to volatility
    "VIRTUAL_STAKE": 12.0,
}

STATE_FILE = DATA_DIR / "state_sol_5m.json"

def log(message: str, level: str = "INFO"):
    timestamp = datetime.now(timezone.utc).isoformat()
    log_file = LOG_DIR / f"sol_5m_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.log"
    line = f"[{timestamp}] [{level}] {message}"
    with log_file.open("a") as f:
        f.write(line + "\n")
    print(line)

def load_state() -> Dict:
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            state = json.load(f)
            if state.get("date") != datetime.now(timezone.utc).strftime("%Y-%m-%d"):
                return {"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "trades_today": 0, "daily_pnl": 0.0}
            return state
    return {"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "trades_today": 0, "daily_pnl": 0.0}

def save_state(state: Dict):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def fetch_sol_price() -> Optional[float]:
    try:
        resp = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=SOL', timeout=5)
        return float(resp.json()['data']['rates']['USD'])
    except Exception as e:
        log(f"SOL fetch error: {e}", "ERROR")
        return None

def get_polymarket_odds() -> Tuple[Optional[float], Optional[float]]:
    try:
        result = subprocess.run(["bankr", "market", "info", CONFIG["MARKET_NAME"]], 
                              capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            return None, None
        
        output = result.stdout
        yes_odds, no_odds = None, None
        
        for line in output.split('\n'):
            if 'yes' in line.lower() and '$' in line:
                try:
                    yes_odds = float(line.split('$')[1].split()[0])
                except:
                    pass
            elif 'no' in line.lower() and '$' in line:
                try:
                    no_odds = float(line.split('$')[1].split()[0])
                except:
                    pass
        
        return yes_odds, no_odds
    except:
        return None, None

def calculate_edge(sol_change_pct: float, yes_odds: float, no_odds: float) -> Tuple[Optional[str], float, float]:
    abs_change = abs(sol_change_pct)
    direction = "UP" if sol_change_pct > 0 else "DOWN"
    fair_prob = min(abs_change * 6, 80) / 100  # SOL more volatile, wider range
    
    if direction == "UP":
        edge = fair_prob - yes_odds
        if edge > CONFIG["EDGE_THRESHOLD"]:
            return "YES", edge, fair_prob
    else:
        edge = fair_prob - no_odds
        if edge > CONFIG["EDGE_THRESHOLD"]:
            return "NO", edge, fair_prob
    
    return None, 0.0, fair_prob

def log_trade(direction: str, stake: float, odds: float, edge: float, 
              sol_start: float, sol_end: float, sol_change: float):
    state = load_state()
    
    trade = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "market": CONFIG["MARKET_NAME"],
        "direction_bought": direction,
        "stake": stake,
        "entry_odds": odds,
        "edge": edge,
        "sol_start": sol_start,
        "sol_end": sol_end,
        "sol_change_pct": sol_change,
        "status": "open",
    }
    
    trades_file = REPORTS_DIR / f"sol_5m_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
    with trades_file.open("a") as f:
        f.write(json.dumps(trade) + "\n")
    
    try:
        sys.path.insert(0, '/Users/thekhemist/.openclaw/workspace/trading/paper-logs')
        from logger import PaperTradingLogger
        pt_logger = PaperTradingLogger()
        pt_logger.log_trade({
            'market': f"Polymarket-{CONFIG['MARKET_NAME']}-{datetime.now(timezone.utc).strftime('%H%M')}",
            'direction': direction,
            'entry_price': odds,
            'fair_price': odds + edge,
            'edge_percent': edge * 100,
            'position_size': stake,
            'confidence': min(edge * 20, 0.95),
            'reasoning': f"5m Window: SOL {sol_change:+.2f}% | Bought {direction} at {odds:.2f} with {edge*100:.1f}% edge",
            'status': 'open'
        })
    except Exception as e:
        log(f"PaperTradingLogger error: {e}", "WARN")
    
    state["trades_today"] += 1
    save_state(state)
    log(f"TRADE: Bought {direction} at ${odds:.2f} | Edge: {edge*100:.1f}% | SOL: {sol_change:+.2f}%", "TRADE")

def get_5m_window() -> int:
    return (datetime.now(timezone.utc).minute // 5) * 5

def seconds_to_next_5m() -> int:
    now = datetime.now(timezone.utc)
    current = get_5m_window()
    next_w = (current + 5) % 60
    diff = (next_w - now.minute) * 60 - now.second
    return diff if diff > 0 else diff + 300

def monitor_5m_window():
    start_price = fetch_sol_price()
    if not start_price:
        return
    log(f"Window start | SOL: ${start_price:,.2f}")
    
    time.sleep(4.5 * 60)
    
    end_price = fetch_sol_price()
    yes_odds, no_odds = get_polymarket_odds()
    
    if not end_price or yes_odds is None:
        log("Missing data at window end", "ERROR")
        return
    
    change_pct = ((end_price - start_price) / start_price) * 100
    direction, edge, fair = calculate_edge(change_pct, yes_odds, no_odds)
    
    log(f"Window complete | SOL: ${end_price:,.2f} | Change: {change_pct:+.2f}%")
    log(f"Odds | YES: ${yes_odds:.2f} | NO: ${no_odds:.2f} | Edge: {edge*100:.1f}%")
    
    if direction and edge >= CONFIG["EDGE_THRESHOLD"]:
        buy_odds = yes_odds if direction == "YES" else no_odds
        log_trade(direction, CONFIG["VIRTUAL_STAKE"], buy_odds, edge, start_price, end_price, change_pct)
    else:
        log(f"No trade - edge {edge*100:.1f}% < threshold")

def run():
    log("="*60)
    log(f"SOL 5m Polymarket Trader Started")
    log(f"Market: {CONFIG['MARKET_NAME']}")
    log("="*60)
    
    while True:
        seconds = seconds_to_next_5m()
        next_w = (get_5m_window() + 5) % 60
        log(f"Next window in {seconds}s (at :{next_w:02d})")
        
        time.sleep(seconds + 2)
        
        state = load_state()
        if state["trades_today"] >= CONFIG["MAX_DAILY_TRADES"]:
            log("Daily limit reached", "SAFEGUARD")
            time.sleep(3600)
            continue
        
        try:
            monitor_5m_window()
        except Exception as e:
            log(f"Error: {e}", "ERROR")
        
        time.sleep(5)

if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        log("Shutdown", "INFO")
        sys.exit(0)
