#!/usr/bin/env python3
"""
Polymarket watcher for Signal Hunter v0.1

- Fetches BTC up/down markets from Polymarket public API
- Tracks price movements over time
- Logs significant (>5%) shifts to disk for downstream processing
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import requests

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

def fetch_markets() -> List[Dict]:
    url = "https://clob.polymarket.com/markets"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", [])
    except Exception as exc:
        log(f"[ERROR] Failed to fetch Polymarket markets: {exc}")
        return []

def filter_btc_markets(markets: List[Dict]) -> List[Dict]:
    btc_markets = []
    for market in markets:
        question = market.get("question", "").lower()
        if "btc" in question and any(term in question for term in ["up", "down", "price"]):
            btc_markets.append(market)
    return btc_markets

def load_state() -> Dict:
    state_file = DATA_DIR / "polymarket_state.json"
    if state_file.exists():
        return json.loads(state_file.read_text())
    return {}

def save_state(state: Dict) -> None:
    state_file = DATA_DIR / "polymarket_state.json"
    state_file.write_text(json.dumps(state, indent=2))

def log(message: str) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    log_file = LOG_DIR / "polymarket.log"
    timestamp = datetime.utcnow().isoformat()
    with log_file.open("a") as f:
        f.write(f"[{timestamp}] {message}\n")


def main() -> None:
    markets = fetch_markets()
    btc_markets = filter_btc_markets(markets)
    state = load_state()
    for market in btc_markets:
        market_id = market.get("id")
        prices = market.get("outcomes", [])
        if not prices:
            continue
        yes_price = prices[0].get("price") if prices else None
        if yes_price is None:
            continue
        previous = state.get(market_id, {}).get("price")
        state[market_id] = {
            "price": yes_price,
            "question": market.get("question"),
            "timestamp": datetime.utcnow().isoformat(),
        }
        if previous is None:
            log(f"[INIT] {market.get('question')} @ {yes_price:.4f}")
        else:
            delta = (yes_price - previous) / previous if previous else 0
            if abs(delta) >= 0.05:
                direction = "UP" if delta > 0 else "DOWN"
                log(
                    f"[MOVE] {market.get('question')} {direction} {delta*100:.2f}% -> {yes_price:.4f}"
                )
    save_state(state)

if __name__ == "__main__":
    main()
