#!/usr/bin/env python3
"""
Cross Reference Engine - Signal Hunter v0.1
Reads watcher logs, surfaces correlations, and flags high-confidence signals.
Designed for lightweight local execution (Qwen/Ollama friendly) and
relies solely on locally stored JSONL logs produced by the watcher scripts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent
LOG_DIR = BASE_DIR / "logs"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

POLYMARKET_LOG = LOG_DIR / "polymarket_odds.jsonl"
X_SCRAPER_LOG = LOG_DIR / "x_scraper.jsonl"
NEWS_FEEDS_LOG = LOG_DIR / "news_feeds.jsonl"
CROSS_REF_LOG = LOG_DIR / "cross_reference.jsonl"

REPORT_FILE = REPORTS_DIR / "daily_signals.md"

CORRELATION_WINDOW_MINUTES = 30
RECENT_WINDOW_HOURS = 36

CONFIDENCE_THRESHOLDS = {
    "low": 30,
    "medium": 50,
    "high": 70,
}

BASE_CONFIDENCE = {
    frozenset({"news", "polymarket"}): 55,
    frozenset({"news", "x"}): 45,
    frozenset({"polymarket", "x"}): 45,
    frozenset({"news", "polymarket", "x"}): 75,
}

# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

@dataclass
class SignalEvent:
    source: str
    timestamp: datetime
    message: str
    data: Dict

    @property
    def text(self) -> str:
        return f"{self.message} {json.dumps(self.data, ensure_ascii=False)}"


@dataclass
class Correlation:
    correlation_id: str
    sources: List[str]
    created_at: datetime
    confidence_score: float
    confidence_level: str
    direction: str
    keywords: List[str]
    summary: str
    signals: Dict[str, Dict]
    keyword_overlap: float = 0.0


# ---------------------------------------------------------------------------
# Utility Functions
# ---------------------------------------------------------------------------

def parse_timestamp(value: str) -> Optional[datetime]:
    try:
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value)
    except Exception:
        return None


def read_jsonl(path: Path, hours: int) -> List[Dict]:
    events: List[Dict] = []
    if not path.exists():
        return events

    cutoff = datetime.utcnow() - timedelta(hours=hours)

    with path.open("r") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                timestamp = parse_timestamp(event.get("timestamp", ""))
                if not timestamp or timestamp < cutoff:
                    continue
                event["_dt"] = timestamp
                events.append(event)
            except json.JSONDecodeError:
                continue

    return events


def load_signals() -> Dict[str, List[SignalEvent]]:
    signals: Dict[str, List[SignalEvent]] = {"polymarket": [], "x": [], "news": []}

    # Polymarket significant moves
    for event in read_jsonl(POLYMARKET_LOG, RECENT_WINDOW_HOURS):
        if event.get("type") != "significant_move":
            continue
        signals["polymarket"].append(
            SignalEvent(
                source="polymarket",
                timestamp=event["_dt"],
                message=event.get("message", ""),
                data=event.get("data", {}),
            )
        )

    # X high-signal tweets
    for event in read_jsonl(X_SCRAPER_LOG, RECENT_WINDOW_HOURS):
        if event.get("type") != "high_signal_tweet":
            continue
        signals["x"].append(
            SignalEvent(
                source="x",
                timestamp=event["_dt"],
                message=event.get("message", ""),
                data=event.get("data", {}),
            )
        )

    # News high-priority articles
    for event in read_jsonl(NEWS_FEEDS_LOG, RECENT_WINDOW_HOURS):
        if event.get("type") != "high_priority_news":
            continue
        signals["news"].append(
            SignalEvent(
                source="news",
                timestamp=event["_dt"],
                message=event.get("message", ""),
                data=event.get("data", {}),
            )
        )

    return signals


def normalize_words(text: str) -> List[str]:
    cleaned = ''.join(ch.lower() if ch.isalnum() else ' ' for ch in text)
    words = [w for w in cleaned.split() if len(w) > 3]
    return words


def keyword_overlap(a: str, b: str) -> float:
    words_a = set(normalize_words(a))
    words_b = set(normalize_words(b))
    if not words_a or not words_b:
        return 0.0
    overlap = words_a & words_b
    return len(overlap) / max(len(words_a), len(words_b))


def infer_direction(signal: SignalEvent) -> str:
    if signal.source == "news":
        classification = signal.data.get("scoring", {}).get("classification")
        return classification or "neutral"
    if signal.source == "polymarket":
        direction = signal.data.get("direction")
        if direction == "up":
            return "bullish"
        if direction == "down":
            return "bearish"
        return "neutral"
    if signal.source == "x":
        keywords = [kw.lower() for kw in signal.data.get("keywords_matched", [])]
        bullish_terms = {"etf", "approval", "blackrock", "pump", "listing", "moon", "rally"}
        bearish_terms = {"dump", "crash", "sec halt", "rug", "liquidation", "ban"}
        if any(kw in bullish_terms for kw in keywords):
            return "bullish"
        if any(kw in bearish_terms for kw in keywords):
            return "bearish"
        return "neutral"
    return "neutral"


def aggregate_direction(sources: Dict[str, SignalEvent]) -> str:
    votes = {"bullish": 0, "bearish": 0, "neutral": 0}
    for signal in sources.values():
        direction = infer_direction(signal)
        votes[direction] = votes.get(direction, 0) + 1
    
    bull, bear = votes.get("bullish", 0), votes.get("bearish", 0)
    if bull and bear:
        return "mixed"
    if bull > 0:
        return "bullish"
    if bear > 0:
        return "bearish"
    return "neutral"


def collect_keywords(sources: Dict[str, SignalEvent]) -> List[str]:
    keywords: List[str] = []
    for signal in sources.values():
        if signal.source == "news":
            matches = signal.data.get("scoring", {}).get("matched_keywords", [])
            keywords.extend([kw for _, kw in matches])
        elif signal.source == "x":
            keywords.extend(signal.data.get("keywords_matched", []))
        elif signal.source == "polymarket":
            outcome = signal.data.get("outcome")
            if outcome:
                keywords.append(outcome)
    deduped = []
    seen = set()
    for kw in keywords:
        if kw and kw.lower() not in seen:
            deduped.append(kw)
            seen.add(kw.lower())
    return deduped


def compute_confidence(sources: Dict[str, SignalEvent], overlap: float) -> float:
    key = frozenset(sources.keys())
    base = BASE_CONFIDENCE.get(key, 35)

    strength = 0.0
    if "polymarket" in sources:
        change_pct = float(sources["polymarket"].data.get("change_pct", 0))
        strength += min(change_pct * 0.4, 20)
    if "news" in sources:
        news_score = float(sources["news"].data.get("scoring", {}).get("score", 0))
        strength += min(news_score * 0.3, 20)
    if "x" in sources:
        tweet_score = float(sources["x"].data.get("signal_score", 0))
        strength += min(tweet_score * 0.2, 15)

    overlap_bonus = min(overlap * 40, 20)

    recency_penalty = 0.0
    timestamps = [signal.timestamp for signal in sources.values()]
    age_minutes = (datetime.utcnow() - max(timestamps)).total_seconds() / 60
    recency_penalty = min(age_minutes / 10, 15)

    final_score = max(0.0, min(100.0, base + strength + overlap_bonus - recency_penalty))
    return round(final_score, 2)


def classify_confidence(score: float) -> str:
    if score >= CONFIDENCE_THRESHOLDS["high"]:
        return "high"
    if score >= CONFIDENCE_THRESHOLDS["medium"]:
        return "medium"
    if score >= CONFIDENCE_THRESHOLDS["low"]:
        return "low"
    return "low"


def within_window(a: datetime, b: datetime) -> bool:
    delta = abs(a - b)
    return delta <= timedelta(minutes=CORRELATION_WINDOW_MINUTES)


def build_correlation(sources: Dict[str, SignalEvent]) -> Correlation:
    sorted_times = sorted(signal.timestamp for signal in sources.values())
    created_at = sorted_times[-1]

    texts = [signal.text for signal in sources.values()]
    overlap = 0.0
    if len(texts) >= 2:
        overlap = sum(
            keyword_overlap(texts[i], texts[j])
            for i in range(len(texts))
            for j in range(i + 1, len(texts))
        )
        overlap /= max(1, (len(texts) * (len(texts) - 1)) / 2)

    score = compute_confidence(sources, overlap)
    level = classify_confidence(score)
    direction = aggregate_direction(sources)
    keywords = collect_keywords(sources)

    summary_parts = []
    if "news" in sources:
        summary_parts.append(f"News: {sources['news'].data.get('data', {}).get('title', '')[:80]}")
    if "polymarket" in sources:
        pm = sources['polymarket'].data
        summary_parts.append(
            f"Polymarket {pm.get('outcome')} moved {pm.get('direction')} by {pm.get('change_pct')}%"
        )
    if "x" in sources:
        summary_parts.append(
            f"Tweet @{sources['x'].data.get('author')} matched {len(sources['x'].data.get('keywords_matched', []))} keywords"
        )
    summary = " | ".join(part for part in summary_parts if part)

    correlation_id = f"SIG-{int(created_at.timestamp())}-{len(sources)}"

    serialized_signals = {
        name: {
            "timestamp": signal.timestamp.isoformat(),
            "message": signal.message,
            "data": signal.data,
        }
        for name, signal in sources.items()
    }

    return Correlation(
        correlation_id=correlation_id,
        sources=list(sources.keys()),
        created_at=created_at,
        confidence_score=score,
        confidence_level=level,
        direction=direction,
        keywords=keywords,
        summary=summary,
        signals=serialized_signals,
        keyword_overlap=round(overlap, 3),
    )


def find_correlations(signals: Dict[str, List[SignalEvent]]) -> List[Correlation]:
    correlations: List[Correlation] = []

    news_signals = signals.get("news", [])
    poly_signals = signals.get("polymarket", [])
    x_signals = signals.get("x", [])

    # Triple correlations (news + polymarket + x)
    for news in news_signals:
        related_poly = [pm for pm in poly_signals if within_window(pm.timestamp, news.timestamp)]
        related_x = [tw for tw in x_signals if within_window(tw.timestamp, news.timestamp)]
        for pm in related_poly:
            for tw in related_x:
                sources = {"news": news, "polymarket": pm, "x": tw}
                correlations.append(build_correlation(sources))

    # Pair: news + polymarket
    for news in news_signals:
        for pm in poly_signals:
            if within_window(news.timestamp, pm.timestamp):
                sources = {"news": news, "polymarket": pm}
                correlations.append(build_correlation(sources))

    # Pair: news + x
    for news in news_signals:
        for tw in x_signals:
            if within_window(news.timestamp, tw.timestamp):
                sources = {"news": news, "x": tw}
                correlations.append(build_correlation(sources))

    # Pair: polymarket + x (without news)
    for pm in poly_signals:
        for tw in x_signals:
            if within_window(pm.timestamp, tw.timestamp):
                sources = {"polymarket": pm, "x": tw}
                correlations.append(build_correlation(sources))

    # Deduplicate correlations by correlation_id (keep highest score per id)
    deduped: Dict[str, Correlation] = {}
    for corr in correlations:
        existing = deduped.get(corr.correlation_id)
        if not existing or corr.confidence_score > existing.confidence_score:
            deduped[corr.correlation_id] = corr

    return sorted(deduped.values(), key=lambda c: c.confidence_score, reverse=True)


def log_event(event_type: str, message: str, data: Dict):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type,
        "message": message,
        "data": data,
    }
    with CROSS_REF_LOG.open("a") as handle:
        handle.write(json.dumps(entry) + "\n")


def append_report(correlations: List[Correlation]):
    if not correlations:
        return

    header = f"\n## Cross-Reference Insights ({datetime.utcnow().date()})\n"
    lines = [header]

    for corr in correlations:
        indicator = "🔥" if corr.confidence_level == "high" else ("⚠️" if corr.confidence_level == "medium" else "•")
        lines.append(
            f"{indicator} **{corr.direction.upper()}** | Confidence: {corr.confidence_score}% | Sources: {', '.join(corr.sources)}"
        )
        if corr.summary:
            lines.append(f"   - {corr.summary}")
        if corr.keywords:
            lines.append(f"   - Keywords: {', '.join(corr.keywords[:6])}")

    with REPORT_FILE.open("a") as handle:
        handle.write("\n".join(lines) + "\n")


def run():
    print(f"[{datetime.utcnow().isoformat()}] Cross-reference scan starting...")
    signals = load_signals()

    correlations = find_correlations(signals)
    print(f"Found {len(correlations)} correlation candidates")

    flagged: List[Correlation] = []
    for corr in correlations:
        event_type = "high_confidence_signal" if corr.confidence_level == "high" else "correlation"
        message = (
            f"{corr.confidence_level.upper()} confidence {corr.direction} signal "
            f"({', '.join(corr.sources)})"
        )
        log_event(event_type, message, {
            "correlation_id": corr.correlation_id,
            "confidence_score": corr.confidence_score,
            "confidence_level": corr.confidence_level,
            "direction": corr.direction,
            "keywords": corr.keywords,
            "sources": corr.sources,
            "summary": corr.summary,
            "signals": corr.signals,
            "keyword_overlap": corr.keyword_overlap,
        })

        if corr.confidence_level in {"high", "medium"}:
            flagged.append(corr)

    append_report(flagged)

    print(f"Flagged {len(flagged)} correlations (medium/high confidence)")
    print(f"[{datetime.utcnow().isoformat()}] Cross-reference scan completed")


if __name__ == "__main__":
    run()
