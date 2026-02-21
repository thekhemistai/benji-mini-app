# Market Relationship Graph

**Purpose:** Track logical connections between Polymarket markets for combinatorial arbitrage opportunities.

**Last Updated:** 2026-02-21

---

## Active Clusters

### Trump Deportation Cluster (Polymarket Only)

**Markets:**
1. [[cross-market-research-2026-02-21.md|< 250,000]] — 2.15¢ | $1.2M vol
2. [[cross-market-research-2026-02-21.md|250,000-500,000]] — 95.2¢ | $7.5M vol ⭐ **Consensus**
3. [[cross-market-research-2026-02-21.md|500,000-750,000]] — 2.05¢ | $530K vol
4. [[cross-market-research-2026-02-21.md|750,000-1M]] — 0.5¢ | $518K vol
5. [[cross-market-research-2026-02-21.md|1M-1.25M]] — 0.25¢ | $515K vol
6. [[cross-market-research-2026-02-21.md|1.25M-1.5M]] — 0.45¢ | $474K vol
7. [[cross-market-research-2026-02-21.md|1.5M-1.75M]] — 0.15¢ | $450K vol
8. [[cross-market-research-2026-02-21.md|1.75M-2M]] — 0.7¢ | $396K vol
9. [[cross-market-research-2026-02-21.md|2M+]] — 0.25¢ | $398K vol
10. [[cross-market-research-2026-02-21.md|750,000+ (binary)]] — 1.95¢ | $757K vol

**Logical Structure:**
- **Mutually exclusive** — Only ONE bucket can be correct
- **Exhaustive** — All possibilities covered (0 to ∞)
- **Sum Check:** Prices should roughly partition 100% probability

**Current Status:** ✅ Valid pricing (95% on 250k-500k bucket)

**Kalshi Comparison:** ❌ No comparable markets

---

## Cross-Platform Clusters (Future)

### 2028 Presidential Election (Potential)

**Expected on Both Platforms:**
- "Will [Candidate] win 2028?" — Polymarket
- "Will [Candidate] win 2028?" — Kalshi

**Arbitrage Trigger:** >5% price difference on same candidate

**Monitoring:** [[cross-market-research-2026-02-21.md|Daily Scan]]

---

## High-Volume Watchlist

| Market | Platform | Volume | Category |
|--------|----------|--------|----------|
| Chelsea Clinton 2028 | Polymarket | $38M | Politics |
| Leeds EPL 2025-26 | Polymarket | $38M | Sports |
| Oprah 2028 | Polymarket | $35M | Politics |
| Pacers NBA 2026 | Polymarket | $33M | Sports |
| Andrew Yang 2028 | Polymarket | $32M | Politics |

**Note:** High volume ≠ arbitrage opportunity. Need cross-platform overlap.

---

## Violation Log

**Combinatorial violations detected:** 0

**Last Check:** 2026-02-21 14:00 MST

**Types Monitored:**
- Subset violations (A implies B but price(A) > price(B))
- Exhaustive sum errors (mutually exclusive outcomes sum ≠ 100%)
- Duplicate mispricings (same event, different prices)
- Cross-platform divergences (same event, different platforms)

---

## Research Pipeline

1. **Daily Morning Scan** — 8 AM MST
   - Pull all active markets from both platforms
   - Update cluster relationships
   - Flag new violations

2. **Continuous Monitoring** — Every 4 hours
   - Watch for new market launches
   - Detect cross-platform overlaps
   - Alert on price divergences >5%

3. **Weekly Review** — Sunday evenings
   - Analyze violation patterns
   - Identify best-performing clusters
   - Update trading strategy

---

## Files & Cross-Links

- **Research:** [[cross-market-research-2026-02-21.md|Cross-Market Research]]
- **Results:** [[arb-results.md|Arbitrage Results]]
- **Watchlist:** [[polymarket-watchlist.md|Active Watchlist]]
- **Strategy:** [[../../skills/polymarket-arb/SKILL.md|Arbitrage Skill]]
- **Trading Hub:** [[TRADING-HUB.md|Trading Hub]]

---

*Market graph maintained by Khem. Updated daily.*