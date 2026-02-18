#!/usr/bin/env python3
"""
BTC 15m Price Hunter - Tracks 15-minute BTC up/down markets
Simplified version for 15m windows vs 5m windows
"""

import json
import time
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Optional

import requests

# Paths
DATA_DIR = Path(__file__).resolve().parent / "data"
LOG_DIR = Path(__file__).resolve().parent / "logs"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"
for d in [DATA_DIR, LOG_DIR, REPORTS_DIR]:
    d.mkdir(exist_ok=True)

# 15m Config
CONFIG_15M = {
    "WINDOW_MINUTES": 15,
    "PRICE_THRESHOLD": 0.008,      # 0.8% move triggers (larger for 15m)
    "EDGE_THRESHOLD": 0.04,         # 4% edge required
    "ALERT_BEFORE": 60,             # seconds before window
    "MONITOR_DURATION": 120,        # seconds of monitoring
    "MAX_DAILY_TRADES": 15,         # fewer trades for 15m
    "VIRTUAL_STAKE": 15.0,          # larger stake for 15m
}

STATE_FILE_15M = DATA_DIR / "state_15m.json"

def log_15m(message: str, level: str = "INFO"):
    """Log to 15m-specific log file."""
    timestamp = datetime.now(timezone.utc).isoformat()
    log_file = LOG_DIR / f"btc_15m_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.log"
    line = f"[{timestamp}] [{level}] {message}"
    with log_file.open("a") as f:
        f.write(line + "\n")
    print(line)

def load_state_15m() -> Dict:
    """Load 15m daily state."""
    if STATE_FILE_15M.exists():
        with open(STATE_FILE_15M) as f:
            state = json.load(f)
            if state.get("date") != datetime.now(timezone.utc).strftime("%Y-%m-%d"):
                return {
                    "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                    "trades_today": 0,
                    "daily_pnl": 0.0,
                }
            return state
    return {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "trades_today": 0,
        "daily_pnl": 0.0,
    }

def save_state_15m(state: Dict):
    """Save 15m daily state."""
    with open(STATE_FILE_15M, "w") as f:
        json.dump(state, f, indent=2)

def fetch_btc_price() -> Optional[float]:
    """Fetch current BTC price from Coinbase."""
    try:
        resp = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=BTC', timeout=5)
        return float(resp.json()['data']['rates']['USD'])
    except Exception as e:
        log_15m(f"BTC fetch error: {e}", "ERROR")
        return None

def get_minute_window(now: datetime = None) -> int:
    """Get the current 15m window start (0, 15, 30, 45)."""
    if now is None:
        now = datetime.now(timezone.utc)
    return (now.minute // 15) * 15

def seconds_to_next_window(now: datetime = None) -> int:
    """Calculate seconds until next 15m window."""
    if now is None:
        now = datetime.now(timezone.utc)
    current_window = get_minute_window(now)
    next_window = current_window + 15
    if next_window >= 60:
        next_window = 0
    
    current_seconds = now.minute * 60 + now.second
    next_seconds = next_window * 60
    if next_window == 0:
        next_seconds = 3600  # Next hour
    
    diff = next_seconds - current_seconds
    if diff <= 0:
        diff += 3600  # Add hour if we wrapped
    return diff

def log_trade_15m(direction: str, start_price: float, end_price: float, change_pct: float):
    """Log 15m paper trade to both local and PaperTradingLogger."""
    state = load_state_15m()
    
    trade = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "paper_trade_15m",
        "direction": direction,
        "btc_start": start_price,
        "btc_end": end_price,
        "btc_change_pct": change_pct,
        "virtual_stake": CONFIG_15M["VIRTUAL_STAKE"],
        "window": "15m",
    }
    
    # Save to 15m trades file
    trades_file = REPORTS_DIR / f"trades_15m_{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.jsonl"
    with trades_file.open("a") as f:
        f.write(json.dumps(trade) + "\n")
    
    # Log to official PaperTradingLogger
    try:
        sys.path.insert(0, '/Users/thekhemist/.openclaw/workspace/trading/paper-logs')
        from logger import PaperTradingLogger
        pt_logger = PaperTradingLogger()
        pt_logger.log_trade({
            'market': f"BTC-15m-{direction}-{datetime.now(timezone.utc).strftime('%H%M')}",
            'direction': direction,
            'entry_price': 0.5,  # Even odds baseline
            'fair_price': 0.5 + (change_pct / 100),
            'edge_percent': abs(change_pct),
            'position_size': CONFIG_15M["VIRTUAL_STAKE"],
            'confidence': min(abs(change_pct) / 2, 0.95),
            'reasoning': f"15m Window: BTC moved {change_pct:.2f}% | Signal: {direction}",
            'status': 'open'
        })
    except Exception as e:
        log_15m(f"PaperTradingLogger error: {e}", "WARN")
    
    state["trades_today"] += 1
    save_state_15m(state)
    
    log_15m(f"TRADE: {direction} | Change: {change_pct:.2f}% | Stake: ${CONFIG_15M['VIRTUAL_STAKE']}", "TRADE")

def monitor_15m_window():
    """Monitor a single 15m window and execute if threshold hit."""
    now = datetime.now(timezone.utc)
    window_start = get_minute_window(now)
    
    # Wait for window to start
    while get_minute_window(datetime.now(timezone.utc)) == window_start:
        time.sleep(1)
    
    # Window started - capture start price
    start_price = fetch_btc_price()
    if not start_price:
        log_15m("Could not fetch start price, skipping window", "WARN")
        return
    
    log_15m(f"Window started | BTC: ${start_price:,.2f}")
    
    # Monitor for 15 minutes
    start_time = time.time()
    while time.time() - start_time < (15 * 60 - 5):  # 14m 55s
        time.sleep(5)
    
    # Window ending - capture end price
    end_price = fetch_btc_price()
    if not end_price:
        log_15m("Could not fetch end price", "WARN")
        return
    
    # Calculate change
    change_pct = ((end_price - start_price) / start_price) * 100
    direction = "UP" if change_pct > 0 else "DOWN"
    abs_change = abs(change_pct)
    
    log_15m(f"Window complete | BTC: ${end_price:,.2f} | Change: {change_pct:+.2f}%")
    
    # Check threshold
    if abs_change >= (CONFIG_15M["PRICE_THRESHOLD"] * 100):
        log_trade_15m(direction, start_price, end_price, change_pct)
    else:
        log_15m(f"No trade - change {abs_change:.2f}% below threshold {CONFIG_15M['PRICE_THRESHOLD']*100:.1f}%")

def run_15m_tracker():
    """Main 15m tracker loop."""
    log_15m("="*50)
    log_15m("BTC 15m Price Hunter Started")
    log_15m("="*50)
    
    state = load_state_15m()
    log_15m(f"Daily trades: {state['trades_today']}/{CONFIG_15M['MAX_DAILY_TRADES']}")
    
    while True:
        now = datetime.now(timezone.utc)
        seconds_to_next = seconds_to_next_window(now)
        
        log_15m(f"Next window in {seconds_to_next}s (at :{get_minute_window(now) + 15 if get_minute_window(now) < 45 else 0:02d})")
        
        # Sleep until window starts
        time.sleep(seconds_to_next + 2)  # +2s buffer
        
        # Check daily limits
        state = load_state_15m()
        if state["trades_today"] >= CONFIG_15M["MAX_DAILY_TRADES"]:
            log_15m("Daily trade limit reached, pausing", "SAFEGUARD")
            time.sleep(3600)  # Sleep 1 hour
            continue
        
        # Monitor this window
        try:
            monitor_15m_window()
        except Exception as e:
            log_15m(f"Monitor error: {e}", "ERROR")
        
        time.sleep(5)  # Brief pause between windows

if __name__ == "__main__":
    try:
        run_15m_tracker()
    except KeyboardInterrupt:
        log_15m("Shutting down...", "INFO")
        sys.exit(0)
