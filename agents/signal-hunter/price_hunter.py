#!/usr/bin/env python3
"""
Price Hunter v0.1 - BTC Price → Polymarket Arbitrage

Monitors BTC price in real-time, detects rapid moves,
checks if Polymarket odds have updated, flags trade opportunities.
"""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict

import requests

DATA_DIR = Path(__file__).resolve().parent / "data"
LOG_DIR = Path(__file__).resolve().parent / "logs"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Config
PRICE_THRESHOLD = 0.005  # 0.5% move triggers signal
TIME_WINDOW = 60  # seconds
CHECK_INTERVAL = 5  # seconds between price checks
COINBASE_API = "https://api.coinbase.com/v2/exchange-rates?currency=BTC"

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
        # Price in USD
        price = float(data["data"]["rates"]["USD"])
        return price
    except Exception as exc:
        log(f"[ERROR] Failed to fetch BTC price: {exc}")
        return None

def load_price_history() -> list:
    history_file = DATA_DIR / "btc_price_history.jsonl"
    if not history_file.exists():
        return []
    with history_file.open() as f:
        return [json.loads(line) for line in f if line.strip()]

def save_price_point(price: float) -> None:
    history_file = DATA_DIR / "btc_price_history.jsonl"
    point = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "price": price,
    }
    with history_file.open("a") as f:
        f.write(json.dumps(point) + "\n")

def detect_movement(current_price: float, history: list) -> Optional[Dict]:
    """Check if price moved > threshold in time window."""
    if not history:
        return None
    
    now = datetime.now(timezone.utc)
    cutoff = now.timestamp() - TIME_WINDOW
    
    # Find price from TIME_WINDOW seconds ago
    recent_prices = [
        h for h in history 
        if datetime.fromisoformat(h["timestamp"]).timestamp() > cutoff
    ]
    
    if not recent_prices:
        return None
    
    old_price = recent_prices[0]["price"]
    change_pct = (current_price - old_price) / old_price
    
    if abs(change_pct) >= PRICE_THRESHOLD:
        direction = "UP" if change_pct > 0 else "DOWN"
        return {
            "direction": direction,
            "change_pct": change_pct,
            "old_price": old_price,
            "new_price": current_price,
            "time_window": TIME_WINDOW,
        }
    
    return None

def log_opportunity(signal: Dict) -> None:
    opp_file = REPORTS_DIR / "price_opportunities.jsonl"
    opportunity = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "price_movement",
        **signal,
    }
    with opp_file.open("a") as f:
        f.write(json.dumps(opportunity) + "\n")
    
    log(f"[SIGNAL] BTC {signal['direction']} {signal['change_pct']*100:.2f}% "
        f"(${signal['old_price']:,.2f} → ${signal['new_price']:,.2f}) "
        f"in {signal['time_window']}s - CHECK POLYMARKET")

def main():
    log("[INIT] Price Hunter v0.1 starting...")
    log(f"[CONFIG] Threshold: {PRICE_THRESHOLD*100}%, Window: {TIME_WINDOW}s")
    
    while True:
        price = get_btc_price()
        if price:
            save_price_point(price)
            history = load_price_history()
            signal = detect_movement(price, history)
            
            if signal:
                log_opportunity(signal)
            else:
                # Only log price periodically to avoid spam
                if len(history) % 12 == 0:  # Every ~60 seconds
                    log(f"[MONITOR] BTC ${price:,.2f} - No signal")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log("[SHUTDOWN] Price Hunter stopped by user")
