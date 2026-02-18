#!/usr/bin/env python3
"""RSS-based crypto news watcher."""

from datetime import datetime
from pathlib import Path

import feedparser

FEEDS = [
    "https://cointelegraph.com/rss",
    "https://www.coindesk.com/arc/outboundfeeds/rss/"
    "?output=xml",
    "https://cryptoslate.com/feed/",
]
KEYWORDS = ["bitcoin", "btc", "sec", "etf", "approval", "base", "coinbase"]
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)


def log(message: str) -> None:
    log_file = LOG_DIR / "news_feeds.log"
    with log_file.open("a") as f:
        f.write(f"[{datetime.utcnow().isoformat()}] {message}\n")


def append_signal(entry: dict) -> None:
    signals_file = DATA_DIR / "news_signals.jsonl"
    import json
    payload = {
        "title": entry.get("title"),
        "link": entry.get("link"),
        "published": entry.get("published"),
    }
    with signals_file.open("a") as f:
        f.write(json.dumps(payload) + "\n")


def main() -> None:
    for feed in FEEDS:
        parsed = feedparser.parse(feed)
        for entry in parsed.entries[:20]:
            title = entry.get("title", "").lower()
            if any(keyword in title for keyword in KEYWORDS):
                log(f"[MATCH] {entry.get('title')}")
                append_signal(entry)

if __name__ == "__main__":
    main()
