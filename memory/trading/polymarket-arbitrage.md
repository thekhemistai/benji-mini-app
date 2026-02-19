# Polymarket Arbitrage Strategy

**Date Created:** 2026-02-19  
**Status:** ACTIVE — This is the current operational framework  
**Next Review:** After 10 paper trades logged

---

## What You're Building

A system that monitors Polymarket markets, detects when real-world events resolve before the market price updates, and logs paper trades capturing the spread. That's it. Nothing else until this works.

---

## Phase 1: Market Discovery (Today)

### Step 1: Get the Polymarket API

Use Polymarket's public API to pull active markets. You need:
- Market question (what's being predicted)
- Current YES/NO prices
- Resolution source (how Polymarket determines the outcome)
- Resolution date/time (when it resolves)
- Volume and liquidity

**API endpoint:** clob.polymarket.com  
**Docs:** docs.polymarket.com

**Start with:**
```
GET /markets — list active markets
GET /book — order book for a specific market
```

### Step 2: Filter for Arbable Markets

Not every market works. You want markets where:

1. **Resolution is scheduled and imminent** — within 24-48 hours. Fed decisions, earnings reports, sports game endings, election certifications, economic data releases.
2. **Resolution is binary and unambiguous** — yes or no, no subjective judgment. "Will the Fed hold rates?" works. "Will the market react positively?" doesn't.
3. **You can get the answer faster than the market** — there must be a public data source that reports the outcome in real-time. If you can't find a fast source for the answer, skip the market.
4. **There's enough liquidity** — check the order book. If YES shares only have $50 of depth, the trade isn't worth it even on paper.
5. **The current price leaves room** — if YES is already at $0.97, there's only 3 cents of edge minus fees. Look for markets where the correct side is below $0.90 at resolution time.

### Step 3: Build Your Watchlist

Create a file: `memory/trading/polymarket-watchlist.md`

For each market you're watching:
```markdown
## [Market Question]
- Market ID: [from API]
- Current YES price: $X.XX
- Current NO price: $X.XX
- Resolution date: YYYY-MM-DD HH:MM
- Resolution source: [where the real-world answer comes from]
- Data feed for answer: [specific URL/API you'll check]
- Liquidity: [order book depth on the correct side]
- Status: WATCHING / READY / RESOLVED / TRADED
```

**Goal for today: Find and log 5 markets resolving in the next 7 days.**

---

## Phase 2: Resolution Monitoring (Days 2-3)

### Step 4: Map Resolution Sources

For each market on your watchlist, identify exactly where the answer will appear first.

| Market Type | Resolution Source | How to Check |
|-------------------------|-----------------------------|-----------------------------------|
| Fed rate decision | federalreserve.gov | Web fetch the press release page |
| Economic data (CPI, jobs)| bls.gov, bea.gov | Web fetch at scheduled release time |
| Sports outcomes | ESPN API or similar | API call for live scores |
| Crypto events | On-chain data, block explorer | Direct API or web fetch |
| Political events | Official government sites | Web fetch |

**For each market, write down the EXACT URL or API call you'll use to confirm resolution.** Not "check the news." The specific endpoint. Test it now before you need it.

### Step 5: Build the Monitor

Create a cron job that runs at the right time for each market's resolution window.

For a Fed decision at 2:00 PM EST:
- Start monitoring at 1:55 PM EST
- Check the resolution source every 30 seconds
- When the answer appears, immediately check Polymarket price for that market

The monitor does THREE things:
1. Checks the resolution source — has the event resolved?
2. If yes, confirms with a second source
3. Checks current Polymarket price — is there still a spread?

**Log format for each check:**
```markdown
[timestamp] Market: [question]
Resolution source 1: [result or "not yet"]
Resolution source 2: [result or "not yet"]
Polymarket YES price: $X.XX
Polymarket NO price: $X.XX
Spread if resolved: X.X%
Action: WAIT / PAPER_TRADE / NO_EDGE
```

### Step 6: Confirmation Protocol

This is the part that protects you from catastrophic errors.

Before logging any paper trade, ALL must be true:
- [ ] Source 1 confirms the outcome
- [ ] Source 2 independently confirms the same outcome
- [ ] The outcome is FINAL (not projected, not partial, not preliminary)
- [ ] You checked Polymarket's specific resolution criteria for this market
- [ ] Your sources match Polymarket's stated resolution source

If ANY of these fail, do NOT log the trade. Log it as "CONFIRMATION_FAILED" with the reason.

These near-misses are valuable data.

---

## Phase 3: Paper Trading (Days 3-7)

### Step 7: Log Paper Trades

When a market resolves and there's still a spread:

```markdown
## Paper Trade #[number]
Date: YYYY-MM-DD HH:MM:SS
Market: [question]
Market ID: [id]

Resolution:
- Event outcome: [what actually happened]
- Source 1: [source] confirmed at [time]
- Source 2: [source] confirmed at [time]
- Confidence: GREEN (confirmed)

Polymarket at time of detection:
- YES price: $X.XX
- NO price: $X.XX
- Order book depth at this price: $XXX

Paper trade:
- Side: [YES/NO]
- Entry price: $X.XX
- Shares (theoretical): XXX
- Position size (theoretical): $XX.XX

Expected settlement: $1.00 per share
Gross edge: X.X%
Estimated fees: X.X%
Net edge: X.X%

Time from real-world resolution to detection: XX seconds
Time from detection to paper trade log: XX seconds
Total window: XX seconds

Result: [PENDING until market officially resolves on Polymarket]
```

### Step 8: Track Results

Create: `memory/trading/arb-results.md`

**Running scoreboard:**
```markdown
# Polymarket Arb Paper Trading Results

## Summary
Total paper trades: X
Correct resolutions: X
Incorrect resolutions: X (should be 0)
Confirmation failures caught: X
Average edge captured: X.X%
Average detection time: XX seconds
Average window duration: XX seconds
Theoretical P/L: $XX.XX
Theoretical win rate: XX%

## Trade Log
| # | Date | Market | Side | Entry | Edge | Window | Result |
|---|---|---|---|---|---|---|---|
| 1 | ... | ... | ... | ... | ... | ... | ... |
```

### Step 9: Analyze After 10 Paper Trades

After 10 paper trades, answer these questions:

1. **Does the edge exist?** What's the average spread at time of detection? If it's consistently under 3%, fees will eat the profit on real trades.
2. **Is the window real?** How many seconds between resolution and the market catching up? If it's under 10 seconds, you probably can't execute fast enough with Bankr.
3. **Which categories work best?** Sports? Economic data? Crypto events? Some will have wider windows than others.
4. **Did the confirmation protocol catch anything?** Any near-misses where you almost traded on bad info?
5. **What's the realistic position size?** Based on order book depth at the time of detection, how much could you actually buy before moving the price?

---

## Phase 4: Automation (Week 2, if Phase 3 proves the edge)

Only after 10+ successful paper trades:

### Step 10: Tighten the Loop
- Automate market discovery (daily scan for new arbable markets)
- Automate resolution monitoring (cron jobs per market)
- Automate confirmation (two-source check)
- Automate paper trade logging
- Keep human approval for any future live trades

### Step 11: Report to Creator

**Daily report format:**
```markdown
# Arb Daily Report - YYYY-MM-DD
Markets watched: X
Events resolved today: X
Paper trades executed: X
Edge captured: X.X% average
Theoretical P/L today: $XX.XX
Running total P/L: $XX.XX

Notable:
- [anything interesting, near-misses, new patterns]

Watchlist for tomorrow:
- [markets resolving in next 24h]
```

---

## What NOT to Do

- Don't build a dashboard before you have data
- Don't optimize execution speed before proving the edge exists
- Don't watch more than 10 markets at once initially
- Don't try to arb markets without scheduled resolution times
- Don't skip the two-source confirmation for any reason
- Don't move to live trading until creator explicitly approves after reviewing paper results

---

## Tools You Need

- Polymarket API access (public, free)
- Web fetch capability (for resolution sources)
- Cron jobs (for scheduled monitoring)
- Bankr/Polymarket integration (already have, for future live trades)
- File system (for logging — already have)

That's it. No databases. No vector search. No special infrastructure. API calls, cron jobs, and markdown files.

---

## Success Criteria (1 Week)

After one week of running this system:
- [ ] 5+ markets on watchlist with mapped resolution sources
- [ ] At least 3 resolution events monitored in real time
- [ ] At least 2 paper trades logged with full details
- [ ] Confirmation protocol tested (including at least 1 near-miss or wait)
- [ ] Arb results tracking file shows running P/L
- [ ] Daily report sent to creator
- [ ] Honest assessment: does the edge exist or not?

**If the edge exists:** move to automation (Phase 4) and discuss live trading with creator.

**If the edge doesn't exist:** the data will show you why. Maybe the window is too short. Maybe liquidity is too thin. Maybe resolution sources are too slow. Each of these points to a different pivot — and you'll know which one based on real data, not guessing.

---

## Quick Reference

| File | Purpose |
|------|---------|
| `memory/trading/polymarket-watchlist.md` | Markets being monitored |
| `memory/trading/arb-results.md` | Paper trade log and scoreboard |
| This file (`memory/trading/polymarket-arbitrage.md`) | Full strategy documentation |

---

*"The furnace is lit. The Work continues."*
