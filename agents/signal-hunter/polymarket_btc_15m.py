#!/usr/bin/env python3
"""
BTC 15m Polymarket Trader - Tracks Polymarket's "BTC Price Up/Down (15m)" market
Buys YES/NO based on edge vs fair odds calculated from BTC price movement
"""

import json
import time
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests

# Paths
DATA_DIR = Path(__file__).resolve().parent / "data"
LOG_DIR = Path(__file__).resolve().parent / "logs"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"
for d in [DATA_DIR, LOG_DIR, REPORTS_DIR]:
    d.mkdir(exist_ok=True)

# 15m Polymarket Config
CONFIG = {
    "MARKET_NAME": "BTC Price Up/Down (15m)",
    "WINDOW_MINUTES": 15,
    "PRICE_THRESHOLD": 0.005,       # 0.5% move for signal
    "EDGE_THRESHOLD": 0.04,          # 4% edge required to trade
    "MAX_DAILY_TRADES": 15,
    "VIRTUAL_STAKE": 15.0,
    "ODDS_CACHE_TTL": 5,
}

STATE_FILE = DATA_DIR / "state_polymarket_15m.json"

def log(message: str, level: str = "INFO"):
    """Log to 15m Polymarket-specific log file."""
    timestamp = datetime.now(timezone.utc).isoformat()
    log_file = LOG_DIR / f"polymarket_15m_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.log"
    line = f"[{timestamp}] [{level}] {message}"
    with log_file.open("a") as f:
        f.write(line + "\n")
    print(line)

def load_state() -> Dict:
    """Load daily state."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            state = json.load(f)
            if state.get("date") != datetime.now(timezone.utc).strftime("%Y-%m-%d"):
                return {
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "trades_today": 0,
                    "daily_pnl": 0.0,
                    "open_trade": None,
                }
            return state
    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "trades_today": 0,
        "daily_pnl": 0.0,
        "open_trade": None,
    }

def save_state(state: Dict):
    """Save daily state."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def fetch_btc_price() -> Optional[float]:
    """Fetch current BTC price from Coinbase."""
    try:
        resp = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=BTC', timeout=5)
        return float(resp.json()['data']['rates']['USD'])
    except Exception as e:
        log(f"BTC fetch error: {e}", "ERROR")
        return None

def get_polymarket_odds() -> Tuple[Optional[float], Optional[float]]:
    """Get current YES/NO odds from Polymarket via bankr."""
    try:
        result = subprocess.run(
            ["bankr", "market", "info", CONFIG["MARKET_NAME"]],
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode != 0:
            log(f"bankr error: {result.stderr}", "ERROR")
            return None, None
        
        # Parse odds from output
        output = result.stdout
        yes_match = None
        no_match = None
        
        for line in output.split('\n'):
            if 'yes' in line.lower() and '$' in line:
                # Extract price like "YES: $0.52"
                parts = line.split('$')
                if len(parts) > 1:
                    try:
                        yes_match = float(parts[1].split()[0])
                    except:
                        pass
            elif 'no' in line.lower() and '$' in line:
                parts = line.split('$')
                if len(parts) > 1:
                    try:
                        no_match = float(parts[1].split()[0])
                    except:
                        pass
        
        return yes_match, no_match
    except subprocess.TimeoutExpired:
        log("bankr timeout", "WARN")
        return None, None
    except Exception as e:
        log(f"Odds fetch error: {e}", "ERROR")
        return None, None

def calculate_edge(btc_change_pct: float, yes_odds: float, no_odds: float) -> Tuple[str, float, float]:
    """
    Calculate trading edge.
    
    If BTC moved UP by X%, fair odds for UP should be ~X% * multiplier
    If market odds differ significantly, there's edge.
    
    Returns: (direction_to_buy, edge_percent, fair_odds)
    """
    abs_change = abs(btc_change_pct)
    direction = "UP" if btc_change_pct > 0 else "DOWN"
    
    # Simple fair odds model: larger move = higher probability
    # Cap at 80% to account for reversal risk
    fair_prob = min(abs_change * 10, 80) / 100  # 1% move = 10% prob, max 80%
    
    if direction == "UP":
        # If BTC up, buy YES if yes_odds < fair_prob
        market_prob = yes_odds
        edge = fair_prob - yes_odds
        if edge > CONFIG["EDGE_THRESHOLD"]:
            return "YES", edge, fair_prob
    else:
        # If BTC down, buy NO if no_odds < fair_prob  
        market_prob = no_odds
        edge = fair_prob - no_odds
        if edge > CONFIG["EDGE_THRESHOLD"]:
            return "NO", edge, fair_prob
    
    return None, 0.0, fair_prob

def log_trade(direction: str, stake: float, odds: float, edge: float, 
              btc_start: float, btc_end: float, btc_change: float):
    """Log paper trade to both local and PaperTradingLogger."""
    state = load_state()
    
    trade = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "market": CONFIG["MARKET_NAME"],
        "direction_bought": direction,
        "stake": stake,
        "entry_odds": odds,
        "edge": edge,
        "btc_start": btc_start,
        "btc_end": btc_end,
        "btc_change_pct": btc_change,
        "status": "open",
    }
    
    # Save to trades file
    trades_file = REPORTS_DIR / f"polymarket_15m_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
    with trades_file.open("a") as f:
        f.write(json.dumps(trade) + "\n")
    
    # Log to official PaperTradingLogger
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
            'reasoning': f"15m Window Complete: BTC {btc_change:+.2f}% | Bought {direction} at {odds:.2f} with {edge*100:.1f}% edge",
            'status': 'open'
        })
    except Exception as e:
        log(f"PaperTradingLogger error: {e}", "WARN")
    
    state["trades_today"] += 1
    state["open_trade"] = trade
    save_state(state)
    
    log(f"TRADE: Bought {direction} at ${odds:.2f} | Edge: {edge*100:.1f}% | BTC change: {btc_change:+.2f}%", "TRADE")

def get_minute_window() -> int:
    """Get current 15m window (0, 15, 30, 45)."""
    now = datetime.now(timezone.utc)
    return (now.minute // 15) * 15

def seconds_to_next_window() -> int:
    """Calculate seconds until next 15m window."""
    now = datetime.now(timezone.utc)
    current_window = get_minute_window()
    next_window = (current_window + 15) % 60
    
    current_seconds = now.minute * 60 + now.second
    next_seconds = next_window * 60
    
    diff = next_seconds - current_seconds
    if diff <= 0:
        diff += 3600
    return diff

def monitor_15m_window():
    """Monitor one 15m window and execute if edge found."""
    window_start = get_minute_window()
    log(f"Starting 15m window monitoring (current: :{window_start:02d})")
    
    # Capture start price at window start
    start_price = fetch_btc_price()
    if not start_price:
        log("Could not fetch start price", "ERROR")
        return
    
    log(f"Window start | BTC: ${start_price:,.2f}")
    
    # Monitor for ~14.5 minutes
    start_time = time.time()
    check_count = 0
    
    while time.time() - start_time < (14.5 * 60):
        time.sleep(30)  # Check every 30 seconds
        check_count += 1
        
        # Optional: Log status every 2 minutes
        if check_count % 4 == 0:
            current = fetch_btc_price()
            if current:
                change = ((current - start_price) / start_price) * 100
                log(f"Monitoring... BTC: ${current:,.2f} ({change:+.2f}%)")
    
    # Window ending - capture end price and odds
    end_price = fetch_btc_price()
    yes_odds, no_odds = get_polymarket_odds()
    
    if not end_price:
        log("Could not fetch end price", "ERROR")
        return
    if yes_odds is None or no_odds is None:
        log("Could not fetch Polymarket odds", "ERROR")
        return
    
    # Calculate change and edge
    change_pct = ((end_price - start_price) / start_price) * 100
    direction_to_buy, edge, fair_odds = calculate_edge(change_pct, yes_odds, no_odds)
    
    log(f"Window complete | BTC: ${end_price:,.2f} | Change: {change_pct:+.2f}%")
    log(f"Polymarket odds | YES: ${yes_odds:.2f} | NO: ${no_odds:.2f}")
    log(f"Fair odds: ${fair_odds:.2f} | Calculated edge: {edge*100:.1f}%")
    
    # Execute if edge exists
    if direction_to_buy and edge >= CONFIG["EDGE_THRESHOLD"]:
        buy_odds = yes_odds if direction_to_buy == "YES" else no_odds
        log_trade(direction_to_buy, CONFIG["VIRTUAL_STAKE"], buy_odds, edge,
                  start_price, end_price, change_pct)
    else:
        log(f"No trade - edge {edge*100:.1f}% below threshold {CONFIG['EDGE_THRESHOLD']*100:.1f}%")

def run_polymarket_15m_trader():
    """Main Polymarket 15m trader loop."""
    log("="*60)
    log("Polymarket BTC 15m Trader Started")
    log(f"Market: {CONFIG['MARKET_NAME']}")
    log(f"Edge threshold: {CONFIG['EDGE_THRESHOLD']*100:.1f}%")
    log(f"Stake per trade: ${CONFIG['VIRTUAL_STAKE']}")
    log("="*60)
    
    state = load_state()
    log(f"Daily trades: {state['trades_today']}/{CONFIG['MAX_DAILY_TRADES']}")
    
    while True:
        # Wait for next 15m window
        seconds_to_next = seconds_to_next_window()
        next_window = (get_minute_window() + 15) % 60
        log(f"Next window in {seconds_to_next}s (at :{next_window:02d})")
        
        time.sleep(seconds_to_next + 2)
        
        # Check daily limits
        state = load_state()
        if state["trades_today"] >= CONFIG["MAX_DAILY_TRADES"]:
            log("Daily trade limit reached", "SAFEGUARD")
            time.sleep(3600)
            continue
        
        # Monitor and potentially trade this window
        try:
            monitor_15m_window()
        except Exception as e:
            log(f"Monitor error: {e}", "ERROR")
        
        time.sleep(5)

if __name__ == "__main__":
    try:
        run_polymarket_15m_trader()
    except KeyboardInterrupt:
        log("Shutting down...", "INFO")
        sys.exit(0)
