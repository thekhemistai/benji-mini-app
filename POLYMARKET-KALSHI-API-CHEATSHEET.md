# API Cheat Sheet: Polymarket & Kalshi

**Purpose:** Complete reference for finding and trading on both platforms  
**Last Updated:** 2026-02-21  
**Status:** Cross-market arbitrage viable

---

## POLYMARKET

**Base URL:** `https://gamma-api.polymarket.com`  
**CLOB URL:** `https://clob.polymarket.com`  
**Docs:** https://docs.polymarket.com  
**Auth:** NONE needed for reads

### Site Categories (Tag IDs)

| Category | Tag ID | Notes |
|----------|--------|-------|
| Politics | 2 | Elections, legislation |
| Crypto | 21 | BTC, ETH, prices |
| Sports | 100639 | Game bets (not futures) |
| Finance | 120 | Fed, equities, earnings |
| Tech | 1401 | AI, semiconductors |
| Culture | 596 | Pop culture, awards |
| Geopolitics | 100265 | International affairs |

### Sports Leagues (URL Slugs)

**Major US:** `nba`, `nhl`, `nfl`, `cbb` (NCAAB), `cfb`  
**Soccer:** `epl`, `laliga`, `bundesliga`, `sea` (Serie A), `ucl`, `uel`, `mls`  
**Other:** `ufc`, `atp`, `wta`, `league-of-legends`, `counter-strike`

URL pattern: `/sports/{slug}/games` or `/sports/{slug}/props`

### Key API Patterns

**Get All Active Events (START HERE):**
```bash
# Page 1
curl "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=50&offset=0"

# Page 2
curl "https://gamma-api.polymarket.com/events?active=true&closed=false&limit=50&offset=50"
```

**Filter by Category:**
```bash
# Sports events
curl "https://gamma-api.polymarket.com/events?tag_id=100639&active=true&closed=false&limit=100"

# Crypto events
curl "https://gamma-api.polymarket.com/events?tag_id=21&closed=false&limit=100"
```

**Filter by Sports League:**
```bash
# Step 1: Get series_id for league
curl "https://gamma-api.polymarket.com/sports"

# Step 2: Query by series_id
curl "https://gamma-api.polymarket.com/events?series_id=SERIES_ID&active=true&closed=false"
```

**Get Specific Market:**
```bash
# By slug (from URL)
curl "https://gamma-api.polymarket.com/events?slug=fed-decision-in-march"

# By market slug
curl "https://gamma-api.polymarket.com/markets?slug=will-bitcoin-reach-100k"
```

**Get CLOB Prices:**
```bash
# Midpoint price
curl "https://clob.polymarket.com/midpoint?token_id=TOKEN_ID"

# Full orderbook
curl "https://clob.polymarket.com/book?token_id=TOKEN_ID"

# Spread
curl "https://clob.polymarket.com/spread?token_id=TOKEN_ID"
```

### Critical Fields

| Field | Type | Notes |
|-------|------|-------|
| `outcomePrices` | JSON STRING | `["0.72", "0.28"]` — MUST parse with `json.loads()` |
| `clobTokenIds` | JSON STRING | `["YES_TOKEN", "NO_TOKEN"]` — MUST parse |
| `outcomes` | JSON STRING | `["Yes", "No"]` |
| `volume24hr` | float | 24-hour trading volume |
| `bestBid` / `bestAsk` | float | Current orderbook prices |
| `negRisk` | boolean | Affects trading mechanics |

---

## KALSHI

**Base URL:** `https://api.elections.kalshi.com/trade-api/v2`  
**Docs:** https://docs.kalshi.com  
**Auth:** NONE needed for reads

### Site Categories

- Sports — `KXNBA`, `KXNFL`, `KXNHL`, `KXMLB`
- Crypto — `KXBTC`, `KXETH`, `KXSOL`
- Economics — `KXFED` (rates, jobs, GDP)
- Politics — Various election series
- Weather — `KXHIGHNY` (NYC temp)

### API Structure: Series → Events → Markets

- **Series** = Template (e.g., "NBA Championship")
- **Event** = Specific instance (e.g., "NBA 2025-26 Championship")
- **Market** = Tradable outcome (e.g., "Will Celtics win?")

### Key API Patterns

**Get All Series:**
```bash
curl "https://api.elections.kalshi.com/trade-api/v2/series"
```

**Get All Open Events:**
```bash
# Without nested markets (lighter)
curl "https://api.elections.kalshi.com/trade-api/v2/events?status=open&limit=100"

# With nested markets (complete)
curl "https://api.elections.kalshi.com/trade-api/v2/events?status=open&limit=200&with_nested_markets=true"
```

**Get Markets by Series:**
```bash
# NBA markets
curl "https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXNBA&status=open"

# NFL markets
curl "https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXNFL&status=open"

# NHL markets
curl "https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXNHL&status=open"
```

**Get Markets by Event:**
```bash
curl "https://api.elections.kalshi.com/trade-api/v2/markets?event_ticker=EVENT_TICKER&status=open"
```

**Get Orderbook:**
```bash
# Default depth (10 levels)
curl "https://api.elections.kalshi.com/trade-api/v2/markets/MARKET_TICKER/orderbook"

# Custom depth
curl "https://api.elections.kalshi.com/trade-api/v2/markets/MARKET_TICKER/orderbook?depth=20"
```

### Critical Fields

| Field | Type | Notes |
|-------|------|-------|
| `yes_ask_dollars` / `yes_bid_dollars` | string | "0.72" — USE THESE (not deprecated cent fields) |
| `no_ask_dollars` / `no_bid_dollars` | string | "0.28" — USE THESE |
| `volume` / `volume_24h` | int | Contract volume |
| `event_ticker` | string | Parent event |
| `series_ticker` | string | Parent series (e.g., `KXNBA`) |
| `status` | string | "active", "closed", "settled" |

**Note:** Kalshi orderbook only returns BIDS. YES bid at 60¢ = NO ask at 40¢.

---

## CROSS-MARKET ARBITRAGE

### Step 1: Get Tonight's Games

**Polymarket:**
```bash
# Get sports leagues
curl "https://gamma-api.polymarket.com/sports"

# Get NBA events
curl "https://gamma-api.polymarket.com/events?series_id=SERIES_ID&active=true&closed=false"
```

**Kalshi:**
```bash
# Get NBA markets
curl "https://api.elections.kalshi.com/trade-api/v2/markets?series_ticker=KXNBA&status=open"
```

### Step 2: Match Games

Match by team names and date:
- Polymarket: "nba-lal-gsw-2026-02-22" → Lakers vs Warriors, Feb 22
- Kalshi: "KXNBAGAME-26FEB22LALGSW" → Lakers vs Warriors, Feb 22

### Step 3: Compare Prices

**Example:**
- Polymarket: Lakers YES = $0.62 (62¢)
- Kalshi: Lakers YES = 58¢ ($0.58)
- Spread: 4¢ (4%)

### Step 4: Check for Arb

**Arb exists when:**
```
Buy YES on cheaper platform + Buy NO on expensive platform < $1.00
```

**Example:**
- Buy YES Kalshi @ $0.58
- Buy NO Polymarket @ $0.38 (implied from YES $0.62)
- Total cost: $0.96
- Guaranteed payout: $1.00
- Gross profit: $0.04 (4%)

### Step 5: Fee Math

| Platform | Fee Structure |
|----------|---------------|
| Polymarket | 0.10% taker + 2% on winners |
| Kalshi | ~1.7% max per contract |
| **Combined** | ~3.7% worst case |

**Minimum spread for profit:** >4%

### Step 6: Execution

1. Check orderbook depth on BOTH platforms
2. Execute less liquid side FIRST
3. Execute more liquid side SECOND
4. **Risk:** Non-atomic (prices can move between legs)

---

## CRITICAL NOTES

1. **Polymarket:** `outcomePrices` and `clobTokenIds` are JSON STRINGS — must `json.loads()` before use
2. **Kalshi:** Use `_dollars` fields (e.g., `yes_ask_dollars`), not deprecated cent fields
3. **Kalshi:** Orderbook only has BIDS. YES bid at 60¢ = NO ask at 40¢
4. **Polymarket pagination:** Offset-based (`offset=0, 50, 100...`)
5. **Kalshi pagination:** Cursor-based (`cursor=FROM_PREVIOUS_RESPONSE`)
6. **Filters:** Always use `active=true&closed=false` (Polymarket) or `status=open` (Kalshi)
7. **Kalshi multivariate:** Use `/events/multivariate` for combos — SEPARATE from single-game markets
8. **Rate limits:** Don't hammer endpoints. Scan every 5-15 min for discovery
9. **Settlement:** Polymarket = USDC on Polygon. Kalshi = USD (bank/crypto deposit)
10. **State restrictions:** Kalshi unavailable in IL, MD, MT, NJ, NV, OH

---

## REFERENCE LINKS

**Polymarket:**
- Docs: https://docs.polymarket.com
- Gamma API: https://docs.polymarket.com/developers/gamma-markets-api/overview
- CLOB: https://docs.polymarket.com/developers/CLOB/introduction
- Sports: https://polymarket.com/sports/live

**Kalshi:**
- Docs: https://docs.kalshi.com
- Markets API: https://docs.kalshi.com/api-reference/market/get-markets
- Events API: https://docs.kalshi.com/api-reference/events/get-events
- Sports: https://kalshi.com/category/sports/all-sports

---

*Created from comprehensive API investigation. Cross-market arbitrage confirmed viable for NBA, NFL, NHL, MLB.*
