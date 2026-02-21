# Polymarket Official Agents Framework — Extraction Report

**Source:** https://github.com/polymarket/agents  
**Date:** 2026-02-20  
**Purpose:** Extract useful components for Khem's information arbitrage system

---

## What This Is

Polymarket's official Python framework for building AI trading agents. MIT licensed. Built around prediction-based strategies using RAG + LLMs.

**Critical distinction:** Their edge is *prediction*. Khem's edge is *confirmation speed*. Different games entirely.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    TRADER (trade.py)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Polymarket │  │    Gamma     │  │   Executor   │      │
│  │   (trading)  │  │  (data API)  │  │  (LLM logic) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
         │                   │                  │
         ▼                   ▼                  ▼
   ┌──────────┐      ┌──────────────┐    ┌──────────────┐
   │  CLOB    │      │ Gamma API    │    │   Chroma     │
   │  Client  │      │ /markets     │    │    RAG       │
   │          │      │ /events      │    │              │
   └──────────┘      └──────────────┘    └──────────────┘
```

---

## Components — USE vs AVOID

### ✅ USE — Adapt for Arb System

#### 1. Gamma API Client (`gamma.py`)
**What it does:** Clean HTTP client for Polymarket's Gamma API

**Key methods:**
```python
# Get all active markets
gamma.get_current_markets(limit=100)

# Get all active events  
gamma.get_current_events(limit=100)

# Get specific market by ID
gamma.get_market(market_id)

# Pagination support
gamma.get_all_current_markets(limit=100)  # auto-paginates
```

**Query params available:**
- `active=true` — Active markets only
- `closed=false` — Not closed
- `archived=false` — Not archived
- `tag_slug=bitcoin` — Filter by tag (CRITICAL for BTC up/down markets)
- `limit`, `offset` — Pagination
- `enableOrderBook=true` — CLOB-enabled markets only

**For arb:** Already have working Gamma queries in `scripts/discover-btc-markets.sh`, but their pagination pattern is cleaner.

---

#### 2. Data Models (`objects.py`)
**What it does:** Pydantic models for type-safe API responses

**Key models:**
```python
class SimpleMarket(BaseModel):
    id: int
    question: str
    end: str              # ISO date
    active: bool
    funded: bool
    spread: float         # Bid-ask spread
    outcomes: str         # JSON array as string
    outcome_prices: str   # JSON array as string
    clob_token_ids: str   # For orderbook lookup

class PolymarketEvent(BaseModel):
    id: str
    slug: str             # e.g., "btc-updown-15m-1771552800"
    title: str
    active: bool
    closed: bool
    archived: bool
    endDate: str
    tags: list[Tag]       # Contains slugs for filtering
```

**For arb:** Use `SimpleMarket` pattern. Their `slug` field is perfect for BTC up/down market identification.

---

#### 3. CLOB Client Integration (`polymarket.py`)
**What it does:** Wraps `py_clob_client` for order execution

**Key methods:**
```python
# Initialize with private key
polymarket = Polymarket()  # reads POLYGON_WALLET_PRIVATE_KEY from env

# Get orderbook
orderbook = polymarket.get_orderbook(token_id)

# Get mid price
price = polymarket.get_orderbook_price(token_id)

# Execute order (requires approvals)
order_id = polymarket.execute_order(price, size, side, token_id)

# Market order
result = polymarket.execute_market_order(market, amount)
```

**Critical for arb:** 
- They handle CLOB API key derivation automatically
- Order building/signed order pattern is correct
- **BUT:** Their focus is market orders; arb needs limit orders at specific prices

---

#### 4. CLI Pattern (`cli.py`)
**What it does:** Typer-based CLI with clean command structure

**Commands:**
```bash
python cli.py get-all-markets --limit 10 --sort-by spread
python cli.py get-all-events --limit 5
python cli.py run-autonomous-trader
```

**For arb:** Clean pattern for building arb CLI tools. Can adapt for:
```bash
khem-arb scan          # Find arb opportunities
khem-arb monitor       # Watch specific market
khem-arb execute       # Execute trade (manual approval)
```

---

### ❌ AVOID — Wrong Strategy

#### 1. RAG-Based Market Filtering (`chroma.py`)
**What it does:** Vectorizes market data into Chroma DB, queries with LLM

**Why avoid:**
- **Too slow for arb.** RAG + LLM = seconds. Arb window = seconds.
- **Wrong edge.** They filter by "what am I good at predicting." Arb doesn't predict — it confirms.
- **Unnecessary complexity.** Arb needs: Is outcome confirmed? Is price stale? Trade. No semantic search needed.

---

#### 2. LLM Prediction Engine (`executor.py`, `prompts.py`)
**What it does:** Uses GPT-4 to predict market outcomes

**Their flow:**
1. Get all events
2. Filter with RAG + LLM ("which events am I good at?")
3. Map to markets
4. Filter markets with LLM
5. Superforecast with LLM ("what's the probability?")
6. Format trade from LLM output
7. Execute

**Why avoid:**
- **Gambling, not arbitrage.** They're predicting future events.
- **Arb is mechanical:** Event resolved → Confirm → Trade → Profit.
- **LLM adds latency.** Every millisecond counts in arb.
- **Different game entirely.** They're playing poker; arb is counting cards.

---

#### 3. News API Integration (`news.py`)
**What it does:** Fetches news articles for sentiment analysis

**Why avoid:**
- **News is slow.** By the time news reports an event, arb window is closed.
- **Sentiment is irrelevant.** Arb doesn't care about sentiment. It cares about resolution.

---

## Code Patterns to Adopt

### 1. Environment Configuration
```python
from dotenv import load_dotenv
import os

load_dotenv()
private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY")
```

**Better than hardcoded configs. Use for:**
- Chainlink API keys
- Gamma API endpoints
- Notification webhooks

---

### 2. Pagination Pattern
```python
def get_all_current_markets(self, limit=100):
    offset = 0
    all_markets = []
    while True:
        params = {
            "active": True,
            "closed": False,
            "archived": False,
            "limit": limit,
            "offset": offset,
        }
        market_batch = self.get_markets(querystring_params=params)
        all_markets.extend(market_batch)
        
        if len(market_batch) < limit:
            break
        offset += limit
    return all_markets
```

**Use for:** Scanning all BTC up/down markets across multiple timeframes.

---

### 3. Pydantic Parsing
```python
def parse_pydantic_market(self, market_object: dict) -> Market:
    # Handle stringified JSON arrays
    if "outcomePrices" in market_object:
        market_object["outcomePrices"] = json.loads(market_object["outcomePrices"])
    if "clobTokenIds" in market_object:
        market_object["clobTokenIds"] = json.loads(market_object["clobTokenIds"])
    return Market(**market_object)
```

**Use for:** Type-safe handling of Gamma API responses.

---

### 4. Token Limit Chunking
```python
def divide_list(self, original_list, i):
    sublist_size = math.ceil(len(original_list) / i)
    return [original_list[j:j+sublist_size] for j in range(0, len(original_list), sublist_size)]
```

**Not needed for arb** (we don't process that much data), but useful pattern for other tools.

---

## Key Files for Reference

| File | Purpose | Arb Relevance |
|------|---------|---------------|
| `gamma.py` | Gamma API client | HIGH — adapt query patterns |
| `polymarket.py` | CLOB trading | MEDIUM — see order structure |
| `objects.py` | Data models | HIGH — use type definitions |
| `cli.py` | CLI interface | MEDIUM — command patterns |
| `trade.py` | Trading logic | LOW — wrong strategy |
| `executor.py` | LLM orchestration | AVOID — too slow |
| `prompts.py` | LLM prompts | AVOID — wrong approach |
| `chroma.py` | RAG system | AVOID — unnecessary |
| `news.py` | News API | AVOID — too slow |

---

## Action Items

1. **Immediate:** Review `gamma.py` query patterns — cleaner than current shell scripts
2. **Short-term:** Adopt Pydantic models for type safety in arb system
3. **Medium-term:** Build `khem-arb` CLI using Typer pattern
4. **Never:** Implement RAG/LLM prediction layers — wrong game

---

## The Bottom Line

This framework is well-built for **prediction agents.** Clean code, good patterns, solid architecture.

But **arbitrage is a different beast.** Their RAG + LLM stack adds seconds of latency. Arb requires milliseconds.

**Take the good parts:** API clients, data models, CLI patterns.  
**Leave the rest:** LLM prediction, RAG filtering, sentiment analysis.

Khem's edge is speed and certainty, not forecasting.

---

**Related:** [[memory/trading/polymarket-arbitrage.md|Arbitrage Strategy]] · [[memory/trading/polymarket-watchlist.md|Watchlist]] · [[TOOLS.md|Tool Notes]]
