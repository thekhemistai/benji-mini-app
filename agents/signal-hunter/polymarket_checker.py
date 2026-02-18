#!/usr/bin/env python3
"""
Polymarket odds checker for Price Hunter

When price signal fires, check if Polymarket odds have updated.
If divergence exists, log paper trade opportunity.
"""

import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import re

DATA_DIR = Path(__file__).resolve().parent / "data"
LOG_DIR = Path(__file__).resolve().parent / "logs"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

ODDS_DIVERGENCE_THRESHOLD = 0.05  # 5% difference = tradeable

def log(message: str) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    log_file = LOG_DIR / "polymarket_checker.log"
    with log_file.open("a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def get_polymarket_odds(market: str = "BTC Price Up/Down (5m)") -> dict:
    """Use bankr CLI to get current market odds."""
    try:
        result = subprocess.run(
            ["bankr", "market", "info", market],
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout + result.stderr
        
        # Parse odds from output (looking for "Up: XX¢" and "Down: XX¢")
        up_match = re.search(r'Up:\s*(\d+)¢', output)
        down_match = re.search(r'Down:\s*(\d+)¢', output)
        
        if up_match and down_match:
            return {
                "up": int(up_match.group(1)) / 100,
                "down": int(down_match.group(1)) / 100,
                "raw_output": output,
            }
        else:
            log(f"[ERROR] Could not parse odds from: {output[:200]}")
            return {"up": 0.5, "down": 0.5, "raw_output": output}
    except Exception as exc:
        log(f"[ERROR] Failed to get Polymarket odds: {exc}")
        return {"up": 0.5, "down": 0.5, "error": str(exc)}

def calculate_fair_odds(price_change_pct: float) -> dict:
    """
    Calculate what odds *should* be given price movement.
    Simple model: price up 1% = 60/40 odds for UP
    """
    # Map price change to implied probability
    # 0% change = 50/50
    # 1% up = ~60/40
    # 1% down = ~40/60
    
    base_prob = 0.5 + (price_change_pct * 10)  # 1% = 10 point shift
    base_prob = max(0.05, min(0.95, base_prob))  # Clamp to 5-95%
    
    return {
        "up": base_prob,
        "down": 1 - base_prob,
    }

def check_arbitrage(price_signal: dict) -> dict:
    """
    Check if Polymarket odds lag behind price movement.
    Returns trade opportunity if divergence > threshold.
    """
    direction = price_signal["direction"]
    change_pct = price_signal["change_pct"]
    
    # Get current Polymarket odds
    odds = get_polymarket_odds()
    
    # Calculate fair odds based on price move
    fair = calculate_fair_odds(change_pct)
    
    # Check divergence
    if direction == "UP":
        # Price went up, check if UP odds are still low
        current_up_odds = odds["up"]
        fair_up_odds = fair["up"]
        divergence = fair_up_odds - current_up_odds
        
        if divergence >= ODDS_DIVERGENCE_THRESHOLD:
            return {
                "trade": True,
                "direction": "UP",
                "current_odds": current_up_odds,
                "fair_odds": fair_up_odds,
                "divergence": divergence,
                "edge": f"{divergence*100:.1f}%",
                "action": "BUY YES (UP)",
            }
    else:
        # Price went down
        current_down_odds = odds["down"]
        fair_down_odds = fair["down"]
        divergence = fair_down_odds - current_down_odds
        
        if divergence >= ODDS_DIVERGENCE_THRESHOLD:
            return {
                "trade": True,
                "direction": "DOWN",
                "current_odds": current_down_odds,
                "fair_odds": fair_down_odds,
                "divergence": divergence,
                "edge": f"{divergence*100:.1f}%",
                "action": "BUY YES (DOWN)",
            }
    
    return {
        "trade": False,
        "direction": direction,
        "current_odds": odds["up"] if direction == "UP" else odds["down"],
        "fair_odds": fair["up"] if direction == "UP" else fair["down"],
        "divergence": abs(fair["up"] - odds["up"]) if direction == "UP" else abs(fair["down"] - odds["down"]),
    }

def log_paper_trade(signal: dict, arb: dict) -> None:
    """Log paper trade to file."""
    trade = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "paper_trade",
        "price_signal": signal,
        "arbitrage": arb,
        "stake": 10.0,  # virtual $10
        "status": "open",
    }
    
    trades_file = REPORTS_DIR / "price_trades.jsonl"
    with trades_file.open("a") as f:
        f.write(json.dumps(trade) + "\n")
    
    log(f"[PAPER TRADE] {arb['action']} - Edge: {arb['edge']} - "
        f"Current: {arb['current_odds']:.2f}, Fair: {arb['fair_odds']:.2f}")

def main():
    """Read latest price signal and check for arbitrage."""
    opportunities_file = REPORTS_DIR / "price_opportunities.jsonl"
    
    if not opportunities_file.exists():
        log("[INFO] No price signals yet")
        return
    
    # Read latest signal
    with opportunities_file.open() as f:
        lines = [l for l in f if l.strip()]
        if not lines:
            log("[INFO] No signals in file")
            return
        
        latest = json.loads(lines[-1])
    
    log(f"[CHECK] Processing signal: BTC {latest['direction']} {latest['change_pct']*100:.2f}%")
    
    # Check for arbitrage
    arb = check_arbitrage(latest)
    
    if arb["trade"]:
        log_paper_trade(latest, arb)
    else:
        log(f"[NO TRADE] Divergence only {arb['divergence']*100:.1f}% (need {ODDS_DIVERGENCE_THRESHOLD*100}%)")

if __name__ == "__main__":
    main()
