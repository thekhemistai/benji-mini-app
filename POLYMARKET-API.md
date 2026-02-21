# Polymarket API Reference

**Last Updated:** 2026-02-21  
**Purpose:** Correct API usage for accessing live sports markets

---

## Critical Discovery

The `/markets` endpoint returns **archived historical data** (2020-2023).  
The `/events` endpoint returns **live current markets** (2026, today's games).

**Always use `/events` for live market data.**

---

## API Endpoints

### 1. Events Endpoint (LIVE DATA)

**Base URL:** `https://gamma-api.polymarket.com/events`

**Query Parameters:**
- `slug={event-slug}` - Fetch specific event by slug
- `tag_slug={tag}` - Filter by category (sports, nba, nfl, epl, etc.)
- `active=true` - Active events only
- `limit={n}` - Number of results (max 200)

**Examples:**

```bash
# Get specific live game
curl "https://gamma-api.polymarket.com/events?slug=epl-mac-new-2026-02-21"

# Get all sports events
curl "https://gamma-api.polymarket.com/events?tag_slug=sports&limit=200"

# Get NBA events
curl "https://gamma-api.polymarket.com/events?tag_slug=nba&limit=50"
```

**Response Structure:**
```json
{
  "id": "201874",
  "slug": "epl-mac-new-2026-02-21",
  "title": "Manchester City FC vs. Newcastle United FC",
  "description": "Premier League game scheduled for February 21, 2026",
  "startDate": "2026-02-08T05:07:13.608095Z",
  "endDate": "2026-02-21T20:00:00Z",
  "active": true,
  "closed": false,
  "archived": false,
  "live": false,
  "ended": true,
  "score": "2-1",
  "liquidity": 1792369.55,
  "volume": 7190814.61,
  "volume24hr": 470480.22,
  "enableOrderBook": true,
  "markets": [
    {
      "id": "1354427",
      "question": "Will Manchester City FC win on 2026-02-21?",
      "slug": "epl-mac-new-2026-02-21-mac",
      "outcomes": "[\"Yes\", \"No\"]",
      "outcomePrices": "[\"0.9995\", \"0.0005\"]",
      "volume": "6470385.28",
      "liquidity": "815876.41",
      "active": true,
      "closed": false,
      "clobTokenIds": "[\"...\", \"...\"]"
    }
  ]
}
```

### 2. Markets Endpoint (ARCHIVED DATA)

**Base URL:** `https://gamma-api.polymarket.com/markets`

⚠️ **WARNING:** Returns only historical markets (2020-2023).  
**Do not use for live market discovery.**

---

## Key Fields

### Event Fields
| Field | Type | Description |
|-------|------|-------------|
| `slug` | string | Unique identifier (e.g., "epl-mac-new-2026-02-21") |
| `title` | string | Event name |
| `endDate` | ISO 8601 | When event resolves |
| `active` | boolean | Currently active |
| `closed` | boolean | No longer accepting orders |
| `archived` | boolean | Moved to archive |
| `live` | boolean | Currently in progress |
| `ended` | boolean | Completed |
| `score` | string | Current/live score |
| `liquidity` | float | Total liquidity |
| `volume` | float | Total trading volume |
| `volume24hr` | float | 24-hour volume |
| `markets` | array | Child markets |

### Market Fields
| Field | Type | Description |
|-------|------|-------------|
| `question` | string | Market question |
| `outcomes` | JSON string | Array of outcomes ["Yes", "No"] |
| `outcomePrices` | JSON string | Array of prices ["0.75", "0.25"] |
| `clobTokenIds` | JSON string | Token IDs for CLOB trading |
| `volume` | string | Market volume |
| `liquidity` | string | Market liquidity |

---

## Sports Tags

| Tag | Description |
|-----|-------------|
| `sports` | All sports |
| `nba` | NBA basketball |
| `nfl` | NFL football |
| `nhl` | NHL hockey |
| `epl` | English Premier League |
| `soccer` | Soccer/football |
| `premier-league` | Premier League |

---

## Common Patterns

### Find Live Games Today
```python
import requests
from datetime import datetime, timezone

response = requests.get(
    "https://gamma-api.polymarket.com/events",
    params={"tag_slug": "sports", "limit": 200}
)

events = response.json()
today = datetime.now(timezone.utc)

live_games = []
for e in events:
    if e.get('ended') == False:  # Not finished
        end = datetime.fromisoformat(e['endDate'].replace('Z', '+00:00'))
        days = (end - today).days
        if 0 <= days <= 1:  # Today or tomorrow
            live_games.append(e)
```

### Get Specific Game by Slug
```python
response = requests.get(
    "https://gamma-api.polymarket.com/events",
    params={"slug": "epl-mac-new-2026-02-21"}
)

event = response.json()[0]
print(f"Game: {event['title']}")
print(f"Score: {event.get('score', 'N/A')}")
print(f"Markets: {len(event['markets'])}")
```

---

## CLOB Integration

For order book data and trading:

**Base URL:** `https://clob.polymarket.com`

**Endpoints:**
- `/price?token_id={id}` - Current best price
- `/book?token_id={id}` - Full order book
- `/markets` - CLOB-enabled markets (archived)

**Authentication:** Requires API key from CLOB signup

---

## Cross-Market Arbitrage

### Kalshi Comparison

| Platform | Endpoint | Data Type |
|----------|----------|-----------|
| **Kalshi** | `/trade-api/v2/markets` | Live markets ✅ |
| **Polymarket** | `/events?tag_slug=sports` | Live markets ✅ |

### Strategy
1. Query both APIs for upcoming games
2. Match events by team names
3. Compare implied probabilities
4. Alert on >5% discrepancies

### Example Match
- **Polymarket:** "Will Man City win?" (moneyline)
- **Kalshi:** "Man City win by 2+ goals?" (spread)

Related but different structures - arbitrage possible on correlated outcomes.

---

## Files & References

- **Scanner Script:** `scripts/cross-market-scanner.py`
- **Research:** [[cross-market-research-2026-02-21.md]]
- **Kalshi Integration:** `scripts/kalshi_scanner_final.py`
- **Trading Hub:** [[memory/trading/TRADING-HUB.md]]

---

*Document maintained by Khem. Updated when API behavior changes.*