# Polymarket Arb Watchlist

*Created: 2026-02-19 03:05 MST*  
*Target: 5 markets resolving within 7 days*

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
- **Status:** CLOSED — Market closed at 2 PM MST, missed the window
- **Notes:** Daily recurring market. Resolves based on WSJ open/close data. Market closes before resolution — need to monitor future daily markets earlier in the cycle.

---

## Market 2: Bitcoin Price on February 19
- **Market ID:** (need to fetch from API)
- **Question:** "Bitcoin price on February 19?"
- **Current Prices:** Multiple buckets (66k-68k at 72¢)
- **Resolution Date:** 2026-02-19 (TODAY)
- **Resolution Source:** Bitcoin price at specific time
- **Data Feed:**
  - Primary: https://api.coinbase.com/v2/exchange-rates?currency=BTC
  - Backup: https://api.kraken.com/0/public/Ticker?pair=XBTUSD
- **Liquidity:** $862K volume (excellent)
- **Status:** WATCHING — End-of-day resolution, monitor price action
- **Notes:** Price buckets in $2k increments. Need exact resolution criteria from market details.

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
- **Current Prices:** 280-299 at 38¢, 300-319 at 27¢
- **Resolution Date:** 2026-02-20 (1 day)
- **Resolution Source:** Twitter/X @elonmusk tweet count
- **Data Feed:**
  - Primary: Twitter API (if available) or web scrape
  - Manual: https://twitter.com/elonmusk (count tweets in date range)
- **Liquidity:** $12M volume (excellent)
- **Status:** WATCHING — Resolves tomorrow, need exact methodology
- **Notes:** Counting tweets manually is error-prone. Need to verify if retweets count, if deleted tweets count, etc.

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
