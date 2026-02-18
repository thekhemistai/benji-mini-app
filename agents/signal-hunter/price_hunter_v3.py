#!/usr/bin/env python3
"""
Price Hunter v3 - Production BTC → Polymarket Arbitrage
Pure automation with safeguards. No agent calls for speed.
"""

import json
import time
import subprocess
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Tuple
from dataclasses import dataclass, asdict

import requests

# Paths
DATA_DIR = Path(__file__).resolve().parent / "data"
LOG_DIR = Path(__file__).resolve().parent / "logs"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"
for d in [DATA_DIR, LOG_DIR, REPORTS_DIR]:
    d.mkdir(exist_ok=True)

# Config - Adjustable via config file
CONFIG = {
    "PRICE_THRESHOLD": 0.005,      # 0.5% move triggers signal
    "EDGE_THRESHOLD": 0.05,         # 5% edge required to trade
    "ALERT_BEFORE": 30,             # seconds before window to start
    "MONITOR_DURATION": 90,         # seconds of aggressive monitoring
    "CHECK_INTERVAL_DORMANT": 60,   # seconds between dormant checks
    "CHECK_INTERVAL_ALERT": 1,      # seconds between alert checks
    "MAX_DAILY_TRADES": 20,         # safety: max trades per day
    "MAX_DAILY_LOSS": 20.0,         # safety: pause if down $20
    "VIRTUAL_STAKE": 10.0,          # paper trade size
    "ODDS_CACHE_TTL": 10,           # seconds to cache odds
}

# Load overrides from config file if exists
CONFIG_FILE = DATA_DIR / "config.json"
if CONFIG_FILE.exists():
    with open(CONFIG_FILE) as f:
        CONFIG.update(json.load(f))

# State tracking
STATE_FILE = DATA_DIR / "state.json"

def load_state() -> Dict:
    """Load daily tracking state."""
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            state = json.load(f)
            # Reset if new day
            if state.get("date") != datetime.now(timezone.utc).strftime("%Y-%m-%d"):
                return {
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "trades_today": 0,
                    "daily_pnl": 0.0,
                    "paused": False,
                }
            return state
    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "trades_today": 0,
        "daily_pnl": 0.0,
        "paused": False,
    }

def save_state(state: Dict):
    """Save daily tracking state."""
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

def log(message: str, level: str = "INFO"):
    """Structured logging."""
    timestamp = datetime.now(timezone.utc).isoformat()
    log_file = LOG_DIR / f"price_hunter_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.log"
    line = f"[{timestamp}] [{level}] {message}"
    with log_file.open("a") as f:
        f.write(line + "\n")
    print(line)

def get_btc_price(retries: int = 3, backoff: float = 1.0) -> Optional[float]:
    """Fetch BTC price with retry logic."""
    for attempt in range(retries):
        try:
            resp = requests.get(
                "https://api.coinbase.com/v2/exchange-rates?currency=BTC",
                timeout=5
            )
            resp.raise_for_status()
            return float(resp.json()["data"]["rates"]["USD"])
        except Exception as exc:
            log(f"BTC price fetch failed (attempt {attempt+1}/{retries}): {exc}", "WARN")
            if attempt < retries - 1:
                time.sleep(backoff * (2 ** attempt))
    return None

def get_next_market_window() -> datetime:
    """Get next 5-minute market open time."""
    now = datetime.now(timezone.utc)
    minutes_to_add = 5 - (now.minute % 5)
    if minutes_to_add == 5 and now.second == 0:
        minutes_to_add = 0
    next_window = now + timedelta(minutes=minutes_to_add)
    return next_window.replace(second=0, microsecond=0)

def get_polymarket_odds() -> Optional[Dict]:
    """Fetch Polymarket odds via Bankr CLI natural language interface."""
    try:
        result = subprocess.run(
            ["bankr", "what are the odds for bitcoin up or down today"],
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout for LLM processing
        )
        
        if result.returncode != 0:
            log(f"Bankr error: {result.stderr}", "ERROR")
            return None
        
        # Parse Bankr output
        output = result.stdout
        
        # Look for "Up: $X.XXX, Down: $X.XXX" format
        up_match = re.search(r'Up[:\s]+\$([\d.]+)', output)
        down_match = re.search(r'Down[:\s]+\$([\d.]+)', output)
        
        if up_match and down_match:
            up_price = float(up_match.group(1))
            down_price = float(down_match.group(1))
            total = up_price + down_price
            if total > 0:
                return {
                    "up": up_price / total,
                    "down": down_price / total,
                    "source": "bankr",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
        
        # Fallback: assume 50/50 if parsing fails
        log("Could not parse Bankr output, using 50/50", "WARN")
        return {"up": 0.5, "down": 0.5, "source": "fallback", "timestamp": datetime.now(timezone.utc).isoformat()}
        
    except subprocess.TimeoutExpired:
        log("Bankr timeout (>60s), using fallback odds", "WARN")
        return {"up": 0.5, "down": 0.5, "source": "timeout_fallback", "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as exc:
        log(f"Failed to fetch Polymarket odds: {exc}", "ERROR")
        return None

def calculate_edge(btc_change: float, direction: str, odds: Dict) -> Tuple[float, float]:
    """Calculate trading edge."""
    # Simple linear model: 1% price move = 10pt odds shift
    fair_odds = 0.5 + (btc_change * 10) if direction == "UP" else 0.5 - (btc_change * 10)
    fair_odds = max(0.05, min(0.95, fair_odds))
    
    current_odds = odds.get("up" if direction == "UP" else "down", 0.5)
    edge = fair_odds - current_odds if direction == "UP" else current_odds - fair_odds
    
    return edge, fair_odds

def log_trade(signal: Dict, odds: Dict, edge: float, fair_odds: float, state: Dict):
    """Log paper trade to both local storage and official PaperTradingLogger."""
    trade = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "paper_trade",
        "direction": signal["direction"],
        "btc_start": signal["start_price"],
        "btc_end": signal["end_price"],
        "btc_change_pct": signal["change_pct"],
        "current_odds": odds.get("up" if signal["direction"] == "UP" else "down", 0.5),
        "fair_odds": fair_odds,
        "edge": edge,
        "virtual_stake": CONFIG["VIRTUAL_STAKE"],
        "potential_pnl": edge * CONFIG["VIRTUAL_STAKE"],
        "status": "open",
        "resolved": False,
        "actual_pnl": None,
    }
    
    # Log to local file
    trades_file = REPORTS_DIR / f"trades_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
    with trades_file.open("a") as f:
        f.write(json.dumps(trade) + "\n")
    
    # Log to official PaperTradingLogger
    try:
        sys.path.insert(0, '/Users/thekhemist/.openclaw/workspace/trading/paper-logs')
        from logger import PaperTradingLogger
        pt_logger = PaperTradingLogger()
        pt_logger.log_trade({
            'market': f"BTC-Price-{signal['direction']}-{(datetime.now(timezone.utc) - timedelta(minutes=4)).strftime('%H%M')}",
            'direction': signal['direction'],
            'entry_price': odds.get("up" if signal["direction"] == "UP" else "down", 0.5),
            'fair_price': fair_odds,
            'edge_percent': edge * 100,
            'position_size': CONFIG['VIRTUAL_STAKE'],
            'confidence': min(abs(edge) * 10, 0.95),  # Scale edge to confidence
            'reasoning': f"Signal Hunter: BTC moved {signal['change_pct']:.2f}% with {edge*100:.1f}% edge on {signal['direction']}",
            'status': 'open'
        })
    except Exception as e:
        log(f"Failed to log to PaperTradingLogger: {e}", "WARN")
    
    # Update state
    state["trades_today"] += 1
    save_state(state)
    
    log(f"PAPER TRADE: {signal['direction']} | Edge: {edge*100:.1f}% | Stake: ${CONFIG['VIRTUAL_STAKE']}", "TRADE")
    return trade

def check_safeguards(state: Dict) -> bool:
    """Check if trading should proceed. Returns True if safe to trade."""
    if state.get("paused"):
        log("Trading paused due to safeguard trigger", "SAFEGUARD")
        return False
    
    if state["trades_today"] >= CONFIG["MAX_DAILY_TRADES"]:
        log(f"Max daily trades reached ({CONFIG['MAX_DAILY_TRADES']})", "SAFEGUARD")
        state["paused"] = True
        save_state(state)
        return False
    
    if state["daily_pnl"] <= -CONFIG["MAX_DAILY_LOSS"]:
        log(f"Max daily loss reached (${state['daily_pnl']:.2f})", "SAFEGUARD")
        state["paused"] = True
        save_state(state)
        return False
    
    return True

def monitor_window(window_time: datetime, state: Dict) -> Optional[Dict]:
    """Monitor BTC price during active window."""
    log(f"Monitoring window at {window_time.strftime('%H:%M:%S')}")
    
    prices = []
    start = datetime.now(timezone.utc)
    end = start + timedelta(seconds=CONFIG["MONITOR_DURATION"])
    
    # Get initial price
    initial = get_btc_price()
    if initial:
        prices.append({"t": start.isoformat(), "p": initial})
        log(f"Initial BTC: ${initial:,.2f}")
    
    # Monitor loop
    while datetime.now(timezone.utc) < end:
        price = get_btc_price()
        if price:
            prices.append({"t": datetime.now(timezone.utc).isoformat(), "p": price})
        time.sleep(CONFIG["CHECK_INTERVAL_ALERT"])
    
    # Calculate move
    if len(prices) < 2:
        log("Insufficient price data", "WARN")
        return None
    
    start_price = prices[0]["p"]
    end_price = prices[-1]["p"]
    change_pct = (end_price - start_price) / start_price
    
    log(f"BTC move: {change_pct*100:.2f}% (${start_price:,.2f} → ${end_price:,.2f})")
    
    if abs(change_pct) < CONFIG["PRICE_THRESHOLD"]:
        log(f"Move below threshold ({CONFIG['PRICE_THRESHOLD']*100}%)")
        return None
    
    # Signal detected
    direction = "UP" if change_pct > 0 else "DOWN"
    signal = {
        "direction": direction,
        "start_price": start_price,
        "end_price": end_price,
        "change_pct": change_pct,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    
    # Check safeguards before fetching odds
    if not check_safeguards(state):
        log("Safeguards blocked trade", "SAFEGUARD")
        return None
    
    # Get odds and calculate edge
    odds = get_polymarket_odds()
    if not odds:
        log("Failed to get odds, skipping", "ERROR")
        return None
    
    edge, fair_odds = calculate_edge(change_pct, direction, odds)
    log(f"Current odds: {odds.get('up' if direction == 'UP' else 'down', 0.5):.2f}, Fair: {fair_odds:.2f}, Edge: {edge*100:.1f}%")
    
    if edge >= CONFIG["EDGE_THRESHOLD"]:
        trade = log_trade(signal, odds, edge, fair_odds, state)
        return trade
    else:
        log(f"Edge {edge*100:.1f}% below threshold ({CONFIG['EDGE_THRESHOLD']*100}%)")
        return None

def generate_daily_report():
    """Generate end-of-day report."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    trades_file = REPORTS_DIR / f"trades_{today}.jsonl"
    
    if not trades_file.exists():
        log("No trades today", "REPORT")
        return
    
    trades = []
    with open(trades_file) as f:
        for line in f:
            trades.append(json.loads(line))
    
    # Calculate stats
    total = len(trades)
    wins = len([t for t in trades if t.get("actual_pnl", 0) > 0])
    losses = len([t for t in trades if t.get("actual_pnl", 0) < 0])
    pnl = sum(t.get("actual_pnl", 0) for t in trades)
    
    log(f"DAILY REPORT: {total} trades | {wins}W/{losses}L | PnL: ${pnl:.2f}", "REPORT")

def main():
    log("="*60)
    log("Price Hunter v3 - Production Arbitrage System")
    log("="*60)
    log(f"Config: threshold={CONFIG['PRICE_THRESHOLD']*100}%, edge={CONFIG['EDGE_THRESHOLD']*100}%, max_trades={CONFIG['MAX_DAILY_TRADES']}")
    
    state = load_state()
    log(f"State: trades_today={state['trades_today']}, pnl=${state['daily_pnl']:.2f}, paused={state['paused']}")
    
    try:
        while True:
            if state.get("paused"):
                log("Trading paused. Exiting.")
                break
            
            next_window = get_next_market_window()
            now = datetime.now(timezone.utc)
            alert_time = next_window - timedelta(seconds=CONFIG["ALERT_BEFORE"])
            time_until_alert = (alert_time - now).total_seconds()
            
            if time_until_alert > 0:
                log(f"Next window: {next_window.strftime('%H:%M:%S')} ({int(time_until_alert)}s)")
                time.sleep(min(time_until_alert, CONFIG["CHECK_INTERVAL_DORMANT"]))
                continue
            
            # High alert phase
            monitor_window(next_window, state)
            
            # Wait for window to close
            window_end = next_window + timedelta(seconds=300)
            sleep_time = (window_end - datetime.now(timezone.utc)).total_seconds()
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        log("Shutdown requested", "INFO")
        generate_daily_report()
    except Exception as exc:
        log(f"Fatal error: {exc}", "FATAL")
        raise

if __name__ == "__main__":
    main()
