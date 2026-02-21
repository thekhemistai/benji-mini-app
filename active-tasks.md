# Active Tasks - Cross-Market Arbitrage Focus

*Last updated: 2026-02-21 00:41 MST*

---

## 🔴 ACTIVE — Cross-Market Arbitrage System

**Status:** Pivoting from speed-based to cross-market research-based arb  
**Strategy:** Find price discrepancies between Polymarket and other markets  
**Advantage:** Research-based (minutes/hours), not speed-based (milliseconds)

### Phase 1: Market Discovery ⏳ IN PROGRESS
**Goal:** Identify overlapping markets across platforms
**Markets to check:**
- [ ] Polymarket vs Kalshi (Trump, politics, sports)
- [ ] Polymarket vs Betfair (sports, global events)
- [ ] Polymarket vs Crypto exchanges (BTC predictions)
- [ ] Document price discrepancies

**Assigned to:** Research-Agent (Kimi)

### Phase 2: Price Scanner 🔄 PENDING
**Goal:** Automated cross-market price comparison
**Deliverables:**
- [ ] Scanner script for Polymarket API
- [ ] Kalshi API integration (if accessible)
- [ ] Betfair API integration
- [ ] Alert system for >5% price discrepancies

**Assigned to:** Tech-Architect (Kimi)

### Phase 3: Execution Playbook 🔄 PENDING
**Goal:** Document viable trades
**Deliverables:**
- [ ] Entry/exit criteria
- [ ] Position sizing framework
- [ ] Settlement timeline tracking
- [ ] Risk management rules

**Assigned to:** Counterweight (Kimi) - review before execution

---

## 🎯 CURRENT OPPORTUNITIES (From Manual Scan)

| Market Type | Polymarket Count | Potential Counterpart | Priority |
|-------------|-----------------|----------------------|----------|
| Trump/Politics | 12 markets | Kalshi | HIGH |
| Sports (NBA/NHL/World Cup) | 47 markets | Betfair, Sportsbooks | MEDIUM |
| BTC/Crypto | 4 markets | Crypto options | LOW |

**Top Pick:** Trump deportation markets — crypto-native vs retail US audience = max price divergence potential

---

## 📊 LEGACY STATUS (Speed-Based Arb)

| Component | Status | Notes |
|-----------|--------|-------|
| 5m/15m Auto-arb | ❌ ABANDONED | Markets too efficient |
| WebSocket bot | ✅ WORKING | But no spread found |
| CLOB Wallet | ✅ READY | $5 USDC + 100 POL |

**Lessons Learned:**
- Speed-based arb requires sub-millisecond latency
- Competing with MMs and co-located bots
- Cross-market is the viable edge

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
