# Active Tasks - Speed-Based Arbitrage Focus

*Last updated: 2026-02-21 06:00 MST*

---

## 🔴 ACTIVE — Speed-Based BTC Arbitrage (Infrastructure Fix)

**Status:** Strategy proven on paper; execution tooling broken  
**Strategy:** Information arbitrage — confirm Chainlink feed, buy mispriced winning side  
**Real Performance:** 15 paper trades, 100% win rate, $105.30 theoretical profit

### Phase 1: Execution Infrastructure ⏳ IN PROGRESS
**Goal:** Fix live execution (currently 0% success rate)
**Root Cause:** Bankr CLI latency 60-120s (misses arb window)
**Options:**
- [ ] CLOB API application (submitted, awaiting response)
- [ ] Browser automation fix (Playwright timing issues)
- [ ] Direct Gamma API integration

**Assigned to:** Tech-Architect (Kimi)

### Phase 2: Live Trading Test 🔄 PENDING
**Goal:** Execute 5 live trades with fixed infrastructure
**Success Criteria:**
- [ ] Entry within 30s of resolution confirmation
- [ ] Position settles at $1.00
- [ ] Net profit > $0 after fees

**Assigned to:** Market-Maker (Kimi)

### Phase 3: Scale or Pivot Decision 🔄 PENDING
**Goal:** Prove edge with real money or document failure
**Decision Criteria:**
- If 3+ of 5 live trades profitable → Scale to 20+ trades/day
- If <3 profitable → Document lessons, kill approach

**Assigned to:** Counterweight (Kimi) - final review

---

## 🎯 VALIDATED DATA (From arb-results.md)

| Metric | Value |
|--------|-------|
| Paper trades | 15 |
| Paper win rate | 100% |
| Theoretical P/L | $105.30 |
| Live trades attempted | 3 |
| Live trades successful | 0 |
| Avg detection time | <10s post-resolution |
| Avg window duration | 5-15 min |

**Problem:** Detection works, execution fails

---

## ❌ CROSS-MARKET ARBITRAGE — KILLED (DEFINITIVE)

**Status:** ABANDONED after comprehensive investigation (2026-02-21)
**Finding:** Impossible due to Polymarket API restrictions

**Evidence:**
- Kalshi API: ✅ Returns live sports markets (authenticated, $10 funded)
- Polymarket API: ❌ Returns ONLY archived markets (latest: Nov 2024)
- Web UI shows live markets (Man City vs Newcastle, $6.7M) but NO API access
- Comprehensive scan: 2000+ markets analyzed, zero API-accessible overlaps

**Root Cause:**
Polymarket intentionally restricts live market data to web UI. Public Gamma/CLOB APIs serve historical data only. Cross-platform arbitrage requires identical data access on both platforms.

**Investigation Methods Used:**
1. Gamma API `/markets` with all parameter combinations
2. CLOB API `/markets` with active filters
3. Events endpoint with sports/EPL tags
4. Browser automation (blocked/unavailable)
5. Shadow Council review (Research-Analyst, Archivist, Counterweight)

**All approaches failed to access live Polymarket data.**

**Lesson:** Verify API capabilities BEFORE building cross-platform strategies. Web UI ≠ API access.

---

## 📊 SPEED-BASED ARB STATUS

| Component | Status | Notes |
|-----------|--------|-------|
| Detection system | ✅ WORKING | <10s confirmation via Chainlink |
| Paper logging | ✅ WORKING | 15 trades, 100% accuracy |
| Execution (Bankr) | ❌ BROKEN | 60-120s latency kills edge |
| CLOB API | ⏳ PENDING | Application submitted |
| Browser automation | ⚠️ FLAKY | Playwright timing issues |

**Lessons Learned:**
- Speed-based arb works on paper
- Execution infrastructure is the bottleneck
- Don't pivot away from proven strategies due to tooling issues

---

## 🔧 SYSTEM COMMANDS

```bash
# Activate environment
source .venv-khem-arb/bin/activate

# Run cross-market scanner (when built)
python scripts/cross-market-scanner.py

# Check specific market
python -c "from khem_arb.polymarket import GammaArbClient; g=GammaArbClient(); print(g.get_market_by_slug('MARKET_SLUG'))"
```

---

## ⏰ CRON JOBS ACTIVE

| Job | Schedule | Purpose | Status |
|-----|----------|---------|--------|
| Market Discovery | Every 4 hours | Find new cross-market opportunities | ✅ ACTIVE |
| Price Check | Every 30 min | Monitor known overlaps for discrepancies | ✅ ACTIVE |
| Progress Check | Every 2 hours | Counterweight review | ✅ ACTIVE |

---

*Next: Sub-agents scanning for opportunities*
