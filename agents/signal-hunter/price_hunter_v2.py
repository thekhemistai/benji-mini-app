#!/usr/bin/env python3
"""
Price Hunter v0.2 - Synchronized BTC → Polymarket Arbitrage

Monitors BTC price in sync with Polymarket 5-minute market windows.
Dormant between windows, aggressive monitoring during active periods.
"""

import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Dict, Tuple
import math

import requests

# Paths
DATA_DIR = Path(__file__).resolve().parent / "data"
LOG_DIR = Path(__file__).resolve().parent / "logs"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Config
PRICE_THRESHOLD = 0.005  # 0.5% move triggers signal
ALERT_BEFORE = 30  # seconds before market opens to start monitoring
MONITOR_DURATION = 90  # seconds of aggressive monitoring
CHECK_INTERVAL_DORMANT = 60  # seconds between checks when dormant
CHECK_INTERVAL_ALERT = 1  # seconds between checks during high alert
COINBASE_API = "https://api.coinbase.com/v2/exchange-rates?currency=BTC"
MARKET_DURATION = 300  # 5 minutes = 300 seconds

def log(message: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    log_file = LOG_DIR / "price_hunter.log"
    with log_file.open("a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def get_btc_price() -> Optional[float]:
    try:
        resp = requests.get(COINBASE_API, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        price = float(data["data"]["rates"]["USD"])
        return price
    except Exception as exc:
        log(f"[ERROR] Failed to fetch BTC price: {exc}")
        return None

def get_next_market_window() -> datetime:
    """Get the next 5-minute market open time."""
    now = datetime.now(timezone.utc)
    # Round up to next 5-minute mark
    minutes = now.minute
    seconds = now.second
    microseconds = now.microsecond
    
    # Calculate minutes to add to get to next 5-min boundary
    minutes_to_add = 5 - (minutes % 5)
    if minutes_to_add == 5 and seconds == 0 and microseconds == 0:
        minutes_to_add = 0
    
    next_window = now + timedelta(minutes=minutes_to_add)
    next_window = next_window.replace(second=0, microsecond=0)
    
    return next_window

def calculate_price_change(price_history: list) -> Optional[Dict]:
    """Calculate price change over the monitoring window."""
    if len(price_history) < 2:
        return None
    
    start_price = price_history[0]["price"]
    end_price = price_history[-1]["price"]
    change_pct = (end_price - start_price) / start_price
    
    return {
        "start_price": start_price,
        "end_price": end_price,
        "change_pct": change_pct,
        "direction": "UP" if change_pct > 0 else "DOWN",
    }

def log_opportunity(signal: Dict, window_time: datetime) -> None:
    """Log trading opportunity to file."""
    opp_file = REPORTS_DIR / "price_opportunities.jsonl"
    opportunity = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "window_time": window_time.isoformat(),
        "type": "price_movement",
        **signal,
    }
    with opp_file.open("a") as f:
        f.write(json.dumps(opportunity) + "\n")
    
    log(f"[SIGNAL] BTC {signal['direction']} {abs(signal['change_pct'])*100:.2f}% "
        f"(${signal['start_price']:,.2f} → ${signal['end_price']:,.2f}) "
        f"- CHECK POLYMARKET")

def log_paper_trade(signal: Dict, odds: Dict, window_time: datetime) -> None:
    """Log paper trade opportunity."""
    trade_file = REPORTS_DIR / "paper_trades.jsonl"
    
    # Calculate edge
    if signal["direction"] == "UP":
        fair_odds = 0.5 + signal["change_pct"] * 10  # 1% = 10 point shift
        current_odds = odds.get("up", 0.5)
    else:
        fair_odds = 0.5 - signal["change_pct"] * 10
        current_odds = odds.get("down", 0.5)
    
    fair_odds = max(0.05, min(0.95, fair_odds))
    edge = fair_odds - current_odds if signal["direction"] == "UP" else current_odds - fair_odds
    
    trade = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "window_time": window_time.isoformat(),
        "type": "paper_trade",
        "direction": signal["direction"],
        "btc_change": signal["change_pct"],
        "current_odds": current_odds,
        "fair_odds": fair_odds,
        "edge": edge,
        "status": "open",
        "virtual_stake": 10.0,
    }
    
    with trade_file.open("a") as f:
        f.write(json.dumps(trade) + "\n")
    
    log(f"[PAPER TRADE] {signal['direction']} - Edge: {edge*100:.1f}% - "
        f"Current: {current_odds:.2f}, Fair: {fair_odds:.2f}")

def get_polymarket_odds_simple() -> Dict:
    """Get current Polymarket odds (simplified - would call Bankr in real version)."""
    # Placeholder - in real version this would call Bankr
    # For now, assume 50/50 if we don't have odds
    return {"up": 0.5, "down": 0.5}

def monitor_window(window_start: datetime) -> Optional[Dict]:
    """Monitor BTC price during the active window."""
    log(f"[MONITOR] Starting 90-second monitoring for window at {window_start.strftime('%H:%M:%S')}")
    
    price_history = []
    start_time = datetime.now(timezone.utc)
    end_time = start_time + timedelta(seconds=MONITOR_DURATION)
    
    # Get initial price
    initial_price = get_btc_price()
    if initial_price:
        price_history.append({
            "timestamp": start_time.isoformat(),
            "price": initial_price,
        })
        log(f"[INIT] BTC ${initial_price:,.2f} at window start")
    
    # Monitor aggressively
    while datetime.now(timezone.utc) < end_time:
        price = get_btc_price()
        if price:
            price_history.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "price": price,
            })
        
        time.sleep(CHECK_INTERVAL_ALERT)
    
    # Calculate change
    signal = calculate_price_change(price_history)
    
    if signal and abs(signal["change_pct"]) >= PRICE_THRESHOLD:
        log_opportunity(signal, window_start)
        
        # Check if we should paper trade
        odds = get_polymarket_odds_simple()
        
        if signal["direction"] == "UP":
            fair_odds = 0.5 + signal["change_pct"] * 10
            current_odds = odds.get("up", 0.5)
            edge = fair_odds - current_odds
        else:
            fair_odds = 0.5 - signal["change_pct"] * 10
            current_odds = odds.get("down", 0.5)
            edge = current_odds - fair_odds
        
        fair_odds = max(0.05, min(0.95, fair_odds))
        
        if edge >= 0.05:  # 5% edge threshold
            log_paper_trade(signal, odds, window_start)
            return signal
        else:
            log(f"[NO TRADE] Edge only {edge*100:.1f}% (need 5%)")
    else:
        if signal:
            log(f"[NO SIGNAL] Move was {abs(signal['change_pct'])*100:.2f}% (need {PRICE_THRESHOLD*100}%)")
        else:
            log("[NO DATA] Couldn't calculate price change")
    
    return None

def main():
    log("[INIT] Price Hunter v0.2 starting - Synchronized with Polymarket windows")
    log(f"[CONFIG] Alert threshold: {ALERT_BEFORE}s before window, Monitor for: {MONITOR_DURATION}s")
    
    while True:
        next_window = get_next_market_window()
        now = datetime.now(timezone.utc)
        
        # Calculate time until we need to start monitoring
        alert_time = next_window - timedelta(seconds=ALERT_BEFORE)
        time_until_alert = (alert_time - now).total_seconds()
        
        if time_until_alert > 0:
            # Dormant phase - wait until 30s before next window
            log(f"[DORMANT] Next window at {next_window.strftime('%H:%M:%S')} "
                f"- Sleeping for {int(time_until_alert)}s")
            time.sleep(min(time_until_alert, CHECK_INTERVAL_DORMANT))
            continue
        
        # High alert phase - monitor for 90 seconds
        log(f"[ALERT] Window opening at {next_window.strftime('%H:%M:%S')} - Monitoring now!")
        monitor_window(next_window)
        
        # Wait for window to close, then repeat
        window_end = next_window + timedelta(seconds=MARKET_DURATION)
        now = datetime.now(timezone.utc)
        time_to_next = (window_end - now).total_seconds()
        
        if time_to_next > 0:
            log(f"[WAIT] Window closed - Waiting {int(time_to_next)}s for next window")
            time.sleep(time_to_next)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("[SHUTDOWN] Price Hunter stopped by user")
