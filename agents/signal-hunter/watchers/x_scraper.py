#!/usr/bin/env python3
"""
Lightweight X (Twitter) scraper using the Nitter frontend.
- Monitors specific accounts for keywords
- Logs matching tweets for downstream processing
- Uses conservative timing to avoid blocks
"""

import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict

import requests
from bs4 import BeautifulSoup

WATCH_ACCOUNTS = [
    "zackvoell",
    "HsakaTrades",
    "lookonchain",
    "DegenSpartan",
    "WuBlockchain",
]
KEYWORDS = ["etf", "sec", "blackrock", "approval", "listing", "pump", "dump"]
NITTER_HOST = "https://nitter.net"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"
LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
DATA_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
}


def fetch_tweets(handle: str) -> List[Dict]:
    url = f"{NITTER_HOST}/{handle}"
    tweets = []
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for item in soup.select("div.timeline-item"):
            text = item.select_one("div.tweet-content")
            if not text:
                continue
            content = text.get_text(" ", strip=True)
            timestamp_tag = item.select_one("span.tweet-date a")
            ts = timestamp_tag.get("title") if timestamp_tag else datetime.utcnow().isoformat()
            tweets.append({
                "handle": handle,
                "content": content,
                "timestamp": ts,
            })
    except Exception as exc:
        log(f"[ERROR] Failed to scrape @{handle}: {exc}")
    return tweets


def match_keywords(tweet: Dict) -> bool:
    content = tweet.get("content", "").lower()
    return any(keyword in content for keyword in KEYWORDS)


def log(message: str) -> None:
    log_file = LOG_DIR / "x_scraper.log"
    with log_file.open("a") as f:
        f.write(f"[{datetime.utcnow().isoformat()}] {message}\n")


def append_signal(tweet: Dict) -> None:
    signals_file = DATA_DIR / "x_signals.jsonl"
    import json
    with signals_file.open("a") as f:
        f.write(json.dumps(tweet) + "\n")


def main() -> None:
    for handle in WATCH_ACCOUNTS:
        tweets = fetch_tweets(handle)
        for tweet in tweets:
            if match_keywords(tweet):
                log(f"[MATCH] @{handle}: {tweet['content'][:100]}")
                append_signal(tweet)
        time.sleep(5)  # Respectful delay

if __name__ == "__main__":
    main()
