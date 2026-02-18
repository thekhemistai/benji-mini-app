#!/usr/bin/env python3
"""Simple paper trading engine for Signal Hunter."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
REPORTS_DIR = Path(__file__).resolve().parents[1] / "reports"
LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
POSITIONS_FILE = DATA_DIR / "paper_positions.json"
REPORTS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
CAPITAL = 10.0  # virtual dollars per trade


def log(message: str) -> None:
    log_file = LOG_DIR / "paper_trade.log"
    with log_file.open("a") as f:
        f.write(f"[{datetime.utcnow().isoformat()}] {message}\n")


def load_positions() -> Dict:
    if POSITIONS_FILE.exists():
        return json.loads(POSITIONS_FILE.read_text())
    return {"trades": [], "pnl": 0.0}


def save_positions(state: Dict) -> None:
    POSITIONS_FILE.write_text(json.dumps(state, indent=2))


def record_trade(signal: Dict, outcome: float) -> None:
    state = load_positions()
    profit = CAPITAL * outcome
    state["trades"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "signal": signal,
        "outcome": outcome,
        "pnl": profit,
    })
    state["pnl"] += profit
    save_positions(state)
    log(f"[TRADE] outcome={outcome:+.4f} pnl={profit:+.2f}")


def generate_report() -> None:
    state = load_positions()
    report_file = REPORTS_DIR / f"daily_signals_{datetime.utcnow().date()}.md"
    lines = [
        "# Signal Hunter Daily Report",
        f"Date: {datetime.utcnow().date()}",
        f"Total PnL: ${state['pnl']:.2f}",
        "",
        "## Trades",
    ]
    for trade in state["trades"][-50:]:
        lines.append(
            f"- {trade['timestamp']}: outcome={trade['outcome']:+.3f}, "
            f"pnl=${trade['pnl']:+.2f}"
        )
    report_file.write_text("\n".join(lines))


def main() -> None:
    # Placeholder example
    dummy_signal = {"type": "x+news", "confidence": 0.7}
    record_trade(dummy_signal, outcome=0.05)
    generate_report()

if __name__ == "__main__":
    main()
