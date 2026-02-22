# Polymarket Arbitrage

**Status:** Active — Combinatorial & cross-platform strategies viable  
**Last Updated:** 2026-02-21  
**Priority:** Primary trading strategy

---

## What Changed (2/21/2026)

**Resolution arb is DEAD.** Proven: WebSocket detected BTC outcome instantly, queried orderbook within milliseconds, best ask already $0.99. Market makers with co-located servers and sub-ms connections update prices before any retail agent can act. Average arb window in 2026 is 2.7 seconds, 73% captured by sub-100ms bots.

**We are not a speed bot. We are a reasoning engine.**

Our edge: scanning thousands of markets simultaneously and detecting logical relationships and pricing violations that require *understanding*, not just speed. This is what LLMs do that dumb bots cannot.

---

## Strategy 1: Combinatorial / Cross-Market Arbitrage (PRIMARY)

### What It Is

Different Polymarket markets that are logically related frequently misprice against each other. Each market has its own independent order book. Traders focus on individual markets. Nobody is systematically checking whether prices across related markets make logical sense.

**$40M was extracted from these mispricings between April 2024 and April 2025** (IMDEA Networks Institute / Cornell, arXiv:2508.03474, analyzed 86M bets across thousands of markets).

### Types of Violations

**Type 1: Subset Violation**

Market A is a strict subset of Market B, but A is priced higher.

Example:
- "Chiefs win Super Bowl" = $0.28
- "AFC team wins Super Bowl" = $0.24

Impossible. Chiefs ARE an AFC team. If Chiefs win, AFC wins. AFC must be >= Chiefs. Buy AFC at $0.24 — you profit if Chiefs OR any other AFC team wins.

**Type 2: Exhaustive Sum Violation**

Mutually exclusive outcomes in a multi-outcome market sum to != $1.00.

Example:
- Candidate A: $0.35
- Candidate B: $0.32
- Candidate C: $0.30
- Total: $0.97

Buy one share of EACH outcome for $0.97. One MUST win and pay $1.00. Guaranteed $0.03 profit per set.

**Type 3: Implication Chain Violation**

Logically connected markets across different events with inconsistent pricing.

Example:
- "Trump wins 2028" = 35%
- "Republican wins 2028" = 32%

Impossible. Trump IS a Republican. Republican >= Trump, always.

**Type 4: Near-Duplicate Market Mispricing**

Same event, different wording, different prices.

Example:
- "Will GTA 6 release before 2026?" = $0.42
- "GTA 6 launch date before January 2026" = $0.38

Same question. 4¢ spread. Buy low, sell high.

### Implementation

#### Step 1: Ingest All Active Markets

```bash
GET https://gamma-api.polymarket.com/markets?active=true&limit=100
```

Paginate through all active markets. For each, store:
- condition_id
- question (the full market question text)
- tokens[] (outcome names, prices, token_ids)
- end_date_iso
- tags[]
- description (contains resolution criteria)
- neg_risk (boolean — affects trading mechanics)

Target: build local index of ALL active markets. Update daily.

#### Step 2: Build Market Relationship Graph

This is where the LLM reasoning happens. For each market, analyze the question text and identify:
1. Entity mentions (people, teams, companies, countries)
2. Event type (election, sports, economic, crypto, tech)
3. Time frame (when does this resolve?)
4. Logical dependencies

Group markets into clusters of related markets.

Example cluster: "2028 US Presidential Election"
- "Trump wins 2028 election" — YES: $0.35
- "Republican wins 2028 election" — YES: $0.32 ← VIOLATION
- "DeSantis wins 2028 election" — YES: $0.12
- "Democrat wins 2028 election" — YES: $0.58
- "Third party wins 2028 election" — YES: $0.04
- Sum check: 0.35 + 0.12 + 0.58 + 0.04 = $1.09 ← VIOLATION

Store the graph in `memory/trading/market-graph.md`.

#### Step 3: Scan for Violations

**Check A — Subset Test:**
For every pair (A, B) where A logically implies B:
- If price(A) > price(B): FLAG as subset violation
- Edge = price(A) - price(B)

**Check B — Sum Test:**
For every set of mutually exclusive, exhaustive outcomes:
- If sum < $1.00: FLAG as long arb
- If sum > $1.00: FLAG as short arb
- Edge = |1.00 - sum|

**Check C — Duplicate Test:**
For semantically identical markets with different IDs:
- If |price_A - price_B| > $0.02: FLAG as duplicate mispricing

**Check D — Implication Test:**
For markets where A occurring makes B much more/less likely:
- Check if B's price is consistent with A's probability
- If inconsistent by > 5%: FLAG for manual review

#### Step 4: Edge Calculation & Feasibility

For each flagged violation:
1. Gross edge: Calculated per violation type
2. Polymarket fee: 2% on winning positions. Target >= 2.5-3% spread.
3. Liquidity check: Query order books for BOTH sides
4. Execution risk: Multi-leg trades are NOT atomic
5. Net edge: gross_edge - fees - estimated_slippage

If net edge < 1%: PASS  
If net edge 1-3%: PAPER TRADE  
If net edge > 3%: PAPER TRADE with high priority flag

#### Step 5: Paper Trade Logging

Log every detected opportunity to `memory/trading/arb-results.md`:

```markdown
## Combinatorial Arb #[N]
Date: YYYY-MM-DD HH:MM:SS
Type: SUBSET / SUM / DUPLICATE / IMPLICATION
Markets involved:
- Market A: "[question]" | [condition_id] | YES: $X.XX | NO: $X.XX
- Market B: "[question]" | [condition_id] | YES: $X.XX | NO: $X.XX
Violation:
- Description: [what's logically wrong]
- Gross edge: X.X%
- Fee drag: ~2%
- Liquidity (Leg 1): $XXX available at target
- Liquidity (Leg 2): $XXX available at target
- Net edge estimate: X.X%
Paper trade:
- Leg 1: BUY [outcome] at $X.XX on [market]
- Leg 2: BUY/SELL [outcome] at $X.XX on [market]
Status: OPEN / WON / LOST / EXPIRED
```

---

## Strategy 2: News Interpretation Arb (SECONDARY)

### What It Is

When breaking news drops, there's a window (30 seconds to 5 minutes) before Polymarket prices fully adjust. Speed bots catch the obvious repricing. But many news events have SECOND-ORDER effects on markets that aren't directly about the news.

**Direct effect (bots catch fast):**
- News: "Fed holds rates steady"
- Market: "Fed cuts in March?" → price drops immediately
- Window: <5 seconds. Bots own this.

**Second-order effect (reasoning required):**
- News: "Fed holds rates steady"
- Market: "S&P 500 above 6000 by April?" → should drop
- Market: "10Y Treasury yield above 4.5% by Q2?" → should rise
- Window: 30 seconds to 5+ minutes.

### Implementation

1. Monitor news feeds — web search on cron for breaking news
2. For each news event, reason: Which open Polymarket markets are affected?
3. Check current prices on affected markets
4. If market hasn't repriced → paper trade
5. Log with full reasoning chain

### Confirmation Protocol

- [ ] News confirmed by 2+ authoritative sources
- [ ] Reasoning chain is clear and defensible
- [ ] Price divergence > 10%
- [ ] Market has sufficient liquidity
- [ ] No obvious reason market already priced this in

**Signal levels:**
- GREEN: Clear causal chain, 2+ sources, >10% mispricing
- YELLOW: Plausible chain but <10% or uncertain
- RED: Speculative, single source, thin market

---

## Strategy 3: Multi-Outcome Rebalancing (OPPORTUNISTIC)

### What It Is

The simplest form: in multi-outcome markets (3+ outcomes), buy one share of every outcome when they sum to < $1.00. One must win. Guaranteed profit.

### Reality Check

This is mostly bot-dominated. Median spread is 0.3%, windows last 2.7 seconds. BUT:
- New markets sometimes launch with wide mispricings
- Low-liquidity niche markets have wider spreads
- Markets with many outcomes (10+) are harder for simple bots

### When To Play

Only flag if:
- Sum deviation > 3% (to cover 2% fee + slippage)
- Each outcome has > $100 liquidity
- Market resolves within 30 days

---

## Strategy 4: Cross-Platform Sports Arb (RE-OPENED 2/21/2026)

### What Changed

Kalshi launched NBA moneylines April 2025 and now offers moneylines, spreads, totals, player props across NFL, NBA, NHL, MLB, college, MLS, UFC, tennis, golf.

### How It Works

Same game, same question, different platforms:
- Polymarket: "Will Lakers win?" YES = $0.62, NO = $0.38
- Kalshi: "Will Lakers win?" YES = $0.58, NO = $0.42

If Kalshi YES ($0.58) + Polymarket NO ($0.38) = $0.96 < $1.00:
→ Buy both. One MUST pay $1.00. Gross profit = $0.04/pair.

### Fee Math

- Polymarket winner fee: ~2%
- Kalshi fee: <2% per contract
- Need > 4% gross spread to profit after fees

### Implementation

1. Pull tonight's games from both platforms
2. Match games by team names and date
3. Compare YES prices
4. If spread > 4% → check order book depth
5. Paper trade both legs

### Critical Risks

- **Non-atomic execution:** Prices move between Leg 1 and Leg 2
- **Different resolution criteria:** Read BOTH platforms' rules
- **Capital split:** Polymarket = USDC, Kalshi = USD fiat
- **Execute less liquid side FIRST**

---

## API Reference

### Polymarket

**Base:** `https://gamma-api.polymarket.com`  
**CLOB:** `https://clob.polymarket.com`  
**Auth:** None for reads

```bash
# All active events
GET /events?active=true&closed=false&limit=100

# By category
tag_id=2 (Politics), 21 (Crypto), 100639 (Sports)

# By sports league
GET /sports  # Get series_ids
GET /events?series_id=SERIES_ID&active=true&closed=false

# Specific market
GET /events?slug=fed-decision-in-march

# CLOB orderbook
GET /book?token_id=TOKEN_ID
```

### Kalshi

**Base:** `https://api.elections.kalshi.com/trade-api/v2`  
**Auth:** None for reads

```bash
# All series
GET /series

# NBA markets
GET /markets?series_ticker=KXNBA&status=open

# NFL markets
GET /markets?series_ticker=KXNFL&status=open

# NHL markets
GET /markets?series_ticker=KXNHL&status=open

# By event
GET /markets?event_ticker=EVENT_TICKER&status=open

# Orderbook
GET /markets/{ticker}/orderbook
```

### Critical Fields

**Polymarket:**
- `outcomePrices` — JSON STRING `["0.72", "0.28"]` — MUST parse
- `clobTokenIds` — JSON STRING — MUST parse
- `volume24hr` — 24h volume

**Kalshi:**
- `yes_ask_dollars` / `yes_bid_dollars` — USE THESE (not deprecated cents)
- `series_ticker` — e.g., `KXNBA`, `KXNFL`
- Orderbook only has BIDS (YES bid at 60¢ = NO ask at 40¢)

---

## Daily Workflow

### Morning Scan

1. Pull all active markets from Gamma API
2. Update market relationship graph
3. Run violation checks
4. Query order books for flagged violations
5. Calculate net edge
6. Check news feeds
7. Log all opportunities

### Evening Report

```markdown
# Daily Arb Report — YYYY-MM-DD
## Combinatorial Scan
Markets scanned: XXX
Violations found: X
- Subset: X | Sum: X | Duplicate: X
## Paper Trades
New: X | Resolved: X
Running total P/L: $XX.XX
## Watchlist
High-priority clusters for tomorrow
```

---

## Risk Framework

### What Can Go Wrong

1. **Non-atomic execution** — Leg 1 fills, Leg 2 moves. Biggest risk.
2. **Resolution criteria mismatch** — Markets SEEM linked but resolve differently
3. **Liquidity illusion** — Displayed price has thin depth
4. **Fee erosion** — 2% winner fee means sub-3% edges are marginal
5. **Long capital lock** — Markets resolve in months, capital tied up

### Mitigations

- Always check order book depth
- Always read BOTH markets' resolution criteria
- Execute smallest leg first
- Track capital efficiency (edge % / days held)
- Max 20% capital per arb

---

## What's Dead

| Strategy | Why Dead | Evidence |
|----------|----------|----------|
| Resolution arb | Market makers faster | Tested 2/21 — 0.99 by arrival |
| Simple YES+NO rebalancing | Bots, 0.3% spread | 2.7s windows |
| Manual market making | Requires 24/7 + capital | Not feasible |

---

## Boundaries

- **Paper trading ONLY** until creator approves live execution
- **No single trade >20%** of available capital
- **Multi-leg:** Always verify Leg 1 fills before Leg 2
- **Always read** full resolution criteria before flagging
- **Log EVERYTHING** — pattern data matters
- **Daily report** to creator
- **Never modify** openclaw.json or gateway config
- **Never run** gateway commands

---

## Reference

- arXiv:2508.03474 — "Unravelling the Probabilistic Forest: Arbitrage in Prediction Markets"
- Polymarket docs: https://docs.polymarket.com
- Kalshi docs: https://docs.kalshi.com
- API Cheatsheet: `POLYMARKET-KALSHI-API-CHEATSHEET.md`

---

## Files

- `memory/trading/market-graph.md` — Market relationship clusters
- `memory/trading/polymarket-watchlist.md` — Active opportunities
- `memory/trading/arb-results.md` — Paper trade log
- `memory/trading/daily/YYYY-MM-DD.md` — Daily logs
