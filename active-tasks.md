# Active Tasks - Cross-Market Arbitrage Focus

*Last updated: 2026-02-22 00:25 UTC*

---

## 🟢 ACTIVE — NBA Cross-Market Arbitrage (OPERATIONAL)

**Status:** Scanner deployed, 6 live opportunities detected  
**Strategy:** Compare NBA moneylines between Polymarket and Kalshi  
**Real Performance:** 12 games matched, 6 arb opportunities (5.5% to 21.5% spreads)

### Phase 1: Scanner Deployment ✅ COMPLETE
**Goal:** Operational scanner finding price discrepancies
**Results:**
- ✅ Kalshi API integrated (KXNBAGAME series)
- ✅ Polymarket API integrated (tag_slug=nba)
- ✅ Team code mapping complete (1OR→ORL, etc.)
- ✅ 12 NBA games matched across platforms
- ✅ Auto-logs >4% spreads to arb-results.md

**Scanner:** `scripts/nba_cross_market_scanner.py`

### Phase 2: Paper Trading ⏳ IN PROGRESS
**Goal:** Execute paper trades on highest-spread opportunities
**Current Opportunities:**
| Game | Spread | Action |
|------|--------|--------|
| Rockets vs Knicks | 21.5% | Buy PM YES + Kalshi NO |
| Raptors vs Bucks | 18.5% | Buy Kalshi YES + PM NO |
| Mavericks vs Pacers | 10.5% | Buy Kalshi YES + PM NO |
| Cavaliers vs Thunder | 8.5% | Buy Kalshi YES + PM NO |
| Blazers vs Suns | 5.5% | Buy PM YES + Kalshi NO |
| 76ers vs Pelicans | 5.5% | Buy PM YES + Kalshi NO |

**Tasks:**
- [ ] Paper trade Rockets vs Knicks (highest spread)
- [ ] Verify order book depth on both platforms
- [ ] Log fill prices and calculate net P/L
- [ ] Document execution latency

### Phase 3: Live Execution 🔄 PENDING
**Goal:** Execute real trades with creator approval
**Prerequisites:**
- [ ] 3+ successful paper trades documented
- [ ] Order book depth verified
- [ ] Fee structure confirmed
- [ ] Creator approval obtained

**Capital Required:** $200+ USDC on Polymarket, $200+ USD on Kalshi

---

## 🔴 ACTIVE — Speed-Based BTC Arb (PAUSED)

**Status:** Awaiting CLOB API approval  
**Strategy:** Information arbitrage on BTC up/down markets  
**Previous Performance:** 15 paper trades, 100% win rate, $105.30 theoretical

**Blocker:** CLOB API application pending (submitted 2/20)

**Resume when:** CLOB API key received

---

## 📊 CROSS-MARKET ARB STATUS

| Component | Status | Notes |
|-----------|--------|-------|
| Kalshi API | ✅ OPERATIONAL | KXNBAGAME series, 20 games |
| Polymarket API | ✅ OPERATIONAL | 14 NBA games, live prices |
| Team mapping | ✅ COMPLETE | 30+ team codes mapped |
| Scanner | ✅ OPERATIONAL | Auto-logs >4% spreads |
| Paper trading | ⏳ IN PROGRESS | 6 opportunities queued |
| Live execution | 🔄 PENDING | Awaiting creator approval |

---

## 🎯 AUTONOMOUS TASKS (Self-Assigned)

### Task 1: Continuous Monitoring
**Schedule:** Every 30 minutes during NBA season  
**Action:** Run scanner, log new opportunities  
**Tool:** Cron job

### Task 2: Opportunity Alerting
**Trigger:** New >10% spread detected  
**Action:** Notify creator via Telegram  
**Priority:** High

### Task 3: Paper Trade Execution
**Schedule:** Daily during active games  
**Action:** Execute highest-spread opportunity on paper  
**Log:** Fill prices, slippage, theoretical P/L

### Task 4: Order Book Analysis
**Schedule:** Before each paper trade  
**Action:** Query CLOB depth on both platforms  
**Goal:** Verify liquidity for planned trade size

### Task 5: Pattern Learning
**Schedule:** Weekly review  
**Action:** Analyze which games/time slots produce best spreads  
**Output:** Updated targeting for scans

---

## 🔧 SYSTEM COMMANDS

```bash
# Activate environment
source .venv-khem-arb/bin/activate

# Run cross-market scanner
python scripts/nba_cross_market_scanner.py

# Check logs
tail -f memory/trading/arb-results.md

# Manual API check
curl "https://gamma-api.polymarket.com/events?tag_slug=nba&active=true&closed=false&limit=100"
```

---

## ⏰ CRON JOBS ACTIVE

| Job | Schedule | Purpose | Status |
|-----|----------|---------|--------|
| NBA Scanner | Every 30 min | Find cross-market arb opportunities | 🟢 ACTIVE |
| Opportunity Alert | On detection | Notify creator of >10% spreads | 🟢 ACTIVE |
| Paper Trade Log | Daily | Document execution results | ⏳ PENDING |
| Pattern Review | Weekly | Analyze spread patterns | ⏳ PENDING |
| Progress Check | Every 2 hours | Counterweight review | ✅ ACTIVE |

---

## NEXT ACTIONS (Autonomous)

1. **Immediate:** Execute paper trade on Rockets vs Knicks (21.5% spread)
2. **Today:** Query order book depth for all 6 opportunities
3. **This week:** Complete 3 paper trades, document results
4. **Ongoing:** Monitor for new opportunities, alert on >10% spreads

---

*Status: Operational and autonomous. Executing without further approval required for paper trades. Awaiting creator approval for live capital deployment.*
