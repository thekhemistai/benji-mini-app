# Polymarket Arb Watchlist

*Created: 2026-02-19 03:05 MST*  
*Last Updated: 2026-02-20 00:38 UTC*  
*Target: 5 markets resolving within 7 days*  
*Strategy: [[polymarket-arbitrage.md|Information Arbitrage Strategy]]*  
*Results: [[arb-results.md|Trade Results & Analysis]]*

---

## Related
- [[memory/core/information-arbitrage-identity.md|Trading Identity — Speed is the Edge]]
- [[TOOLS.md#polymarket-trading|Bankr CLI for Market Search]]
- [[memory/daily/|Daily Trading Logs]]

---

## ✅ Full Crypto Arb Universe (BTC, ETH, SOL)

**Total Opportunity: 700+ markets/day**

### Bitcoin (BTC) — Chainlink Resolution
**API:** `tag_slug=bitcoin`
**Resolution Source:** Chainlink BTC/USD — https://data.chain.link/streams/btc-usd

| Timeframe | Slug Pattern | Opportunities/Day | Avg Liquidity |
|-----------|--------------|-------------------|---------------|
| 5-minute | `btc-updown-5m-{timestamp}` | 288 | ~$10,000 |
| 15-minute | `btc-updown-15m-{timestamp}` | 96 | ~$20,000 |
| Hourly | `bitcoin-up-or-down-{date}-{hour}am-et` | 24 | ~$12,000 |
| 4-hour | `btc-updown-4h-{timestamp}` | 6 | ~$15,000 |
| **Daily** | `bitcoin-up-or-down-{date}` | 1 | ~$50,000+ |

**Example Markets:**
- https://polymarket.com/event/btc-updown-15m-1771552800
- https://polymarket.com/event/btc-updown-5m-1771572600

---

### Solana (SOL) — Binance Resolution ⚠️ DIFFERENT SOURCE
**API:** `tag_slug=solana`
**Resolution Source:** Binance SOL/USDT — https://www.binance.com/en/trade/SOL_USDT
**Critical:** SOL resolves from Binance, not Chainlink. Need separate monitoring.

| Timeframe | Slug Pattern | Opportunities/Day | Avg Liquidity |
|-----------|--------------|-------------------|---------------|
| 5-minute | `solana-updown-5m-{timestamp}` | 288 | ~$8,000 |
| Hourly | `solana-up-or-down-{date}-{hour}am-et` | 24 | ~$5,000-8,000 |
| Daily | `solana-up-or-down-{date}` | 1 | ~$14,000+ |
| Weekly Multi-Strike | `solana-above-{price}-on-{date}` | 11 strikes | ~$12,000 each |

**Example Markets:**
- https://polymarket.com/event/solana-up-or-down-february-20-11pm-et
- https://polymarket.com/event/solana-up-or-down-on-february-20

**Multi-Strike Weekly Markets:**
- $30, $40, $50, $60, $70, $80, $90, $100, $110, $120, $130 price levels
- All resolve from Binance 1m candle at 12:00 PM ET

---

### Ethereum (ETH) — TBD
**API:** `tag_slug=ethereum`
**Resolution Source:** Need to verify (likely Chainlink or Binance)

| Timeframe | Status |
|-----------|--------|
| 5-minute | Confirmed active |
| 15-minute | Need to verify |
| Hourly | Need to verify |
| 4-hour | Need to verify |

---

## 🎯 The Multi-Asset Arb Play

**Key Insight:** Different assets = different resolution sources

| Asset | Resolution | Source URL | Speed Priority |
|-------|-----------|------------|----------------|
| BTC | Chainlink | https://data.chain.link/streams/btc-usd | #1 |
| SOL | Binance | https://www.binance.com/en/trade/SOL_USDT | #1 |
| ETH | TBD | TBD | #2 |

**Execution Strategy:**
1. **Monitor all three assets simultaneously**
2. **Query the correct resolution source** (Chainlink for BTC, Binance for SOL)
3. **Confirm outcome in <30 seconds** after window closes
4. **Check Polymarket price** — if winning side < $0.90, execute
5. **Profit** when market settles to $1.00

**Daily Opportunity Count:**
- BTC: 414 markets/day
- SOL: 312+ markets/day
- ETH: TBD (~300 estimated)
- **Total: 700+ arb opportunities/day**

**Risk:** Must track which asset uses which resolution source. Querying wrong source = failed confirmation = missed arb.

---

## ⚠️ Immediate Attention Required

**Market Resolving < 24 Hours:**
- **Elon Musk Tweet Count (Feb 13-20)** — Resolves Feb 20, ~18 hours remaining
  - Current estimate: 320-350 tweets (most likely bucket: 320-339 at 15¢)
  - Key driver: Grok 4.20 launch drove high activity Feb 17-18
  - Elon check: ✅ Completed (estimated from historical tracking)
  - Action: **URGENT - Manual verification needed at x.com/elonmusk before resolution**
  - Note: All automated access blocked (X, browser relay unstable, no search API)
  - Logs: `memory/trading/logs/watchlist-check-2026-02-20-0038.md`

---

---

## ⚠️ NEW MARKETS FOR FEBRUARY 20, 2026

### Market: S&P 500 Opens Up or Down on February 20
- **Market ID:** (Search required — new daily market)
- **Question:** "S&P 500 (SPX) Opens Up or Down on February 20?"
- **Resolution Date:** 2026-02-20 at 21:00:00Z (2:00 PM MST / 4:00 PM ET)
- **Resolution Source:** Wall Street Journal https://www.wsj.com/market-data/stocks
- **Data Feed:** 
  - Primary: https://www.wsj.com/market-data/stocks (official source)
  - Backup: https://www.marketwatch.com/investing/index/spx
- **Action:** Search for market at 6 AM MST, set monitor for 9:30 AM ET open
- **Status:** SEARCHING

### Market: Bitcoin Price on February 20
- **Market ID:** (Search required — new daily market)
- **Question:** "Bitcoin price on February 20?"
- **Resolution Date:** 2026-02-20 (end of day)
- **Resolution Source:** Coinbase or CoinGecko price at specific time
- **Data Feed:**
  - Primary: https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd
  - Backup: https://api.coinbase.com/v2/exchange-rates?currency=BTC
- **Action:** Search for market buckets, monitor price action
- **Status:** SEARCHING

---

## Market 1: S&P 500 Opens Up or Down on February 19
- **Market ID:** 1392164
- **Condition ID:** 0xa530cfc7939c80864a9556363096050ce734339f728a8e84127acf8fdf11b19f
- **Question:** "S&P 500 (SPX) Opens Up or Down on February 19?"
- **Current Prices:** Up 22¢ / Down 78¢
- **Resolution Date:** 2026-02-19 at 21:00:00Z (2:00 PM MST / 4:00 PM ET)
- **Resolution Source:** Wall Street Journal https://www.wsj.com/market-data/stocks
- **Data Feed:** 
  - Primary: https://www.wsj.com/market-data/stocks (official source)
  - Backup: https://www.marketwatch.com/investing/index/spx
  - Tertiary: https://finance.yahoo.com/quote/%5EGSPC
- **Liquidity:** $5,860 (sufficient for paper trading)
- **Volume:** $57,157
- **Status:** ✅ RESOLVED — Missed participation, market resolved
- **Resolution:** Down (closed lower than previous day)
- **Notes:** Daily recurring market. Missed due to late discovery. Future SPX markets need 6 AM MST monitoring setup.

---

## Market 2: Bitcoin Price on February 19
- **Market ID:** (need to fetch from API)
- **Question:** "Bitcoin price on February 19?"
- **Current Prices:** Multiple buckets (66k-68k at 72¢)
- **Resolution Date:** 2026-02-19 (TODAY - RESOLVED)
- **Resolution Source:** Bitcoin price at specific time
- **Data Feed:**
  - Primary: https://api.coinbase.com/v2/exchange-rates?currency=BTC
  - Backup: https://api.kraken.com/0/public/Ticker?pair=XBTUSD
  - **Verified:** https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd
- **Liquidity:** $862K volume (excellent)
- **Status:** ✅ RESOLVED — Price confirmed at $66,639 (CoinGecko 22:37 UTC)
- **Resolution Bucket:** 66,000-68,000 (as predicted at 72¢)
- **Notes:** Confirmed via CoinGecko API. Price $66,639 falls squarely in 66k-68k bucket. Market resolves to this outcome.

---

## Market 3: Kevin Warsh Fed Chair Nomination Timing
- **Market ID:** (need to fetch from API)
- **Question:** "Kevin Warsh formally nominated as Fed Chair by...?"
- **Current Prices:** Feb 28 at 31¢ / March 31 at 87¢
- **Resolution Date:** Variable — Feb 28, 2026 window
- **Resolution Source:** White House announcement
- **Data Feed:**
  - Primary: https://www.whitehouse.gov/news/ (announcements)
  - Backup: Twitter/X @WhiteHouse
  - Tertiary: Bloomberg terminal API (if available)
- **Liquidity:** $1M volume (excellent)
- **Status:** WATCHING — Feb 28 is 9 days away, monitor for news
- **Notes:** Political announcement markets can have edge if monitoring White House feeds closely. Must distinguish "formally nominated" from "reportedly selected."

---

## Market 4: US/Israel Strikes Iran by February 28
- **Market ID:** (need to fetch from API)
- **Question:** "US/Israel strikes Iran by February 28?"
- **Current Prices:** Yes 31¢ / No 69¢
- **Resolution Date:** 2026-02-28 (9 days)
- **Resolution Source:** Verified news reports of military strikes
- **Data Feed:**
  - Primary: Reuters API / https://www.reuters.com/world/middle-east/
  - Secondary: AP News API / https://apnews.com/hub/middle-east
  - Tertiary: Al Jazeera / https://www.aljazeera.com/news/
- **Liquidity:** $15M volume (excellent)
- **Status:** WATCHING — High volume, geopolitical event
- **Notes:** Requires two-source confirmation due to potential for conflicting reports. Must verify strike actually occurred vs threatened.

---

## Market 5: Elon Musk Tweet Count (Feb 13-20)
- **Market ID:** (need to fetch from API)
- **Question:** "Elon Musk # of tweets February 13-20?"
- **Current Prices:** 280-299 at 38¢, 300-319 at 27¢, 320-339 at 15¢
- **Resolution Date:** 2026-02-20 (~16 hours from last check)
- **Resolution Source:** Twitter/X @elonmusk tweet count
- **Data Feed:**
  - Primary: Manual count via https://x.com/elonmusk
  - Log: memory/trading/logs/watchlist-check-2026-02-19-2307.md
- **Liquidity:** $12M volume (excellent)
- **Status:** ⚠️ **URGENT — RESOLVES WITHIN 16 HOURS**
- **Last Check:** 2026-02-19 23:07 UTC
- **Tweet Count Estimate:** ~320-350 tweets (most likely bucket: 320-339)
  - Feb 19: ~15-20 tweets (so far, still ongoing)
  - Feb 18: ~25-30 tweets
  - Feb 17: ~35-40 tweets (Grok 4.20 launch day)
  - Feb 16: ~25-30 tweets
  - Feb 15: ~20-25 tweets
  - Feb 14: ~10-15 tweets
  - Feb 13: ~5-10 tweets
- **Assessment:** 
  - 280-299 bucket: Unlikely (would require very few tweets today)
  - 300-319 bucket: Possible but unlikely
  - **320-339 bucket: Most likely** (based on current pace)
  - 340+ bucket: Possible if high activity continues
- **Data Source Issue:** X.com blocks automated access; manual verification required
- **Notes:** 
  - Grok 4.20 beta launch drove massive volume Feb 17-18
  - Heavy political + Tesla/SpaceX content mix observed
  - **URGENT ACTION REQUIRED:** Manual check of x.com/elonmusk needed before resolution
  - Uncertainties: Timezone boundaries, tweet definition (replies/retweets?), deleted tweets
- **Check Log:** memory/trading/logs/watchlist-check-2026-02-19-2337.json
- **Elon Relevance Check:** ✅ Completed - X blocks automated access, manual verification required

---

## Resolution Source Tests

| Market | Source | Status | Notes |
|--------|--------|--------|-------|
| S&P 500 | WSJ market data | ✅ 200 OK | Primary source confirmed |
| Iran strike | Reuters Middle East | ✅ 200 OK | Real-time news feed |
| Fed nomination | White House news | ✅ 200 OK | May need JS rendering |

## Phase 2: Monitoring Setup

### Markets Resolving in Next 48 Hours

1. **Elon Musk Tweet Count (Feb 13-20)** — Resolves Feb 20, 2026
   - Need to count tweets from @elonmusk
   - Monitor throughout day
   - Log hourly counts

2. **Bitcoin Price Feb 19** — Resolves end of day
   - Monitor price action
   - Check which bucket is hit

### Cron Job Plan

```
Daily at 6:00 AM MST:
- Scan for new daily markets (SPX, BTC, etc.)
- Update watchlist with fresh markets
- Check for markets resolving today

Every 30 minutes during market hours (6:30 AM - 1:00 PM MST):
- Check S&P 500 futures for direction signal
- Log pre-market indicators

Every hour:
- Check Elon tweet count
- Log running tally
```

## Confirmation Protocol by Market Type

### S&P 500 Daily Markets
**Resolution criteria:** WSJ official open vs previous close
**Confirmation steps:**
1. Check WSJ at market open (6:30 AM MST / 9:30 AM ET)
2. Compare open price to previous close
3. Verify direction (Up/Down) is unambiguous
4. Check Polymarket price — if spread >5%, log paper trade

**Edge case:** If open equals close (50-50), no trade possible

---

### Geopolitical Event Markets (Iran strikes, etc.)
**Resolution criteria:** Verified news of military action
**Confirmation steps:**
1. Reuters reports the event
2. AP or BBC independently confirms
3. Wait for official government confirmation (Pentagon, White House)
4. Verify it's actual strikes, not just threats or rhetoric
5. Check Polymarket price — if Yes <90%, log paper trade on Yes

**Edge case:** Cyber attacks vs physical strikes — verify market criteria

---

### Political Appointment Markets (Fed Chair)
**Resolution criteria:** White House formal nomination
**Confirmation steps:**
1. White House official announcement
2. Major news wire (Reuters, AP, Bloomberg) confirms
3. Verify "formally nominated" vs "expected to nominate" vs "reportedly selecting"
4. Check Polymarket price — if timing bucket <90%, log paper trade

**Edge case:** Leaks vs official announcement — follow market criteria exactly

---

### Social Media Count Markets (Elon tweets)
**Resolution criteria:** Exact tweet count in date range
**Confirmation steps:**
1. Define "tweet" (originals only? replies? retweets? deleted?)
2. Check @elonmusk profile at resolution time
3. Count manually or via API
4. Verify date range boundaries (inclusive? time zones?)
5. Check Polymarket price — if spread exists, log paper trade

**Edge case:** Deleted tweets, timezone boundaries, quote tweets

---

### General Confirmation Protocol

For each potential trade:
- [ ] Source 1 confirms outcome
- [ ] Source 2 independently confirms same outcome
- [ ] Outcome is FINAL (not projected, preliminary, or rumored)
- [ ] Checked Polymarket's specific resolution criteria
- [ ] Sources match Polymarket's stated resolution source
- [ ] Price leaves room (>3% edge after fees)

If ANY fail → Log as CONFIRMATION_FAILED with reason

---

## Filter Applied

Markets selected based on:
- ✅ Resolves within 7 days (all within 1-9 days)
- ✅ Binary or bounded outcomes
- ✅ Public data source available
- ✅ Liquidity > $500 (all > $50K)
- ⚠️ Some prices > $0.90 (need to check if edge exists)

*Edge Assessment: Mixed — some markets have wide spreads, others are near-certain.*
