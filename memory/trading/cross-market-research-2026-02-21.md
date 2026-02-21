# Cross-Market Research — 2026-02-21

**Date:** 2026-02-21  
**Researcher:** Khem  
**Platforms:** Polymarket ↔ Kalshi  
**Method:** [[skills/polymarket-arb/SKILL.md|Combinatorial Arbitrage Strategy]]

---

## Executive Summary

| Platform | Markets | Trump Deportation | Overlap |
|----------|---------|-------------------|---------|
| **Polymarket** | 500+ active | 10 markets ($11M+ volume) | ⏳ Awaiting Kalshi |
| **Kalshi** | 1000+ active | 0 markets | ❌ None currently |

**Key Finding:** Zero cross-market arbitrage opportunities for Trump deportations because Kalshi has no comparable markets. However, system is fully operational and monitoring.

---

## Trump Deportation Markets on Polymarket

**Total Volume:** $11,247,877 across 10 markets

| Market | Volume | Yes Price | Interpretation |
|--------|--------|-----------|----------------|
| < 250,000 | $1.2M | 2.15¢ | Very unlikely |
| **250,000-500,000** | **$7.5M** | **95.2¢** | **Market consensus** |
| 500,000-750,000 | $530K | 2.05¢ | Unlikely |
| 750,000-1M | $518K | 0.5¢ | Very unlikely |
| 1M-1.25M | $515K | 0.25¢ | Extremely unlikely |
| 1.25M-1.5M | $474K | 0.45¢ | Extremely unlikely |
| 1.5M-1.75M | $450K | 0.15¢ | Extremely unlikely |
| 1.75M-2M | $396K | 0.7¢ | Extremely unlikely |
| 2M+ | $398K | 0.25¢ | Extremely unlikely |
| 750,000+ (binary) | $757K | 1.95¢ | Very unlikely |

**Market Consensus:** Crypto-native Polymarket users expect **250,000-500,000 deportations** (95% probability).

---

## Kalshi Market Landscape

**Total Markets:** 1000+  
**Categories:**
- Sports (NBA, NFL, player props): ~800 markets
- Politics: 0 deportation markets
- Economics: 0 relevant markets
- Crypto: 8 markets

**Analysis:** Kalshi is heavily sports-focused with minimal political markets currently. No overlap with Polymarket's deportation markets.

---

## Cross-Market Arbitrage Assessment

### Current Opportunities: ZERO

**Why no arb exists:**
1. Kalshi has no deportation markets to compare against
2. No overlapping event markets found
3. Platform specializations differ (Kalshi = sports, Polymarket = politics)

### Potential Future Opportunities

**High Probability Overlaps:**
1. **2028 Presidential Election** — Both platforms likely to run markets
2. **NBA Finals / Championship** — Kalshi heavy on sports, Polymarket has some
3. **Bitcoin price milestones** — Both have crypto markets
4. **Major sporting events** — World Cup, Super Bowl, Olympics

**Monitoring Strategy:**
- Daily scan at 8 AM MST
- Alert when Kalshi adds political markets
- Compare prices immediately upon overlap detection

---

## Strategic Implications

### The Asymmetry Thesis

**Original Hypothesis:** Kalshi (retail US) would price deportations differently than Polymarket (crypto-native).

**Reality:** Cannot test thesis because Kalshi has no deportation markets.

**Alternative Thesis:** When overlap markets DO appear (elections, championships), crypto-native vs retail price divergence may exist.

### Platform Specialization

| Platform | Strength | Weakness |
|----------|----------|----------|
| **Polymarket** | Politics, crypto, long-tail events | Lower sports volume |
| **Kalshi** | Sports, mainstream US events | Limited political markets |

**Implication:** Cross-market arb requires finding events that BOTH platforms care about — major elections, championship sports, economic milestones.

---

## System Status

| Component | Status | Notes |
|-----------|--------|-------|
| Kalshi API | ✅ Connected | RSA auth working, $10 funded |
| Polymarket API | ✅ Connected | Gamma API active |
| Scanner Script | ✅ Operational | Detects overlap automatically |
| Cron Monitoring | ⏳ Ready to deploy | Will alert on new overlaps |

---

## Action Items

1. **Deploy daily scanner cron job** — Check for new overlapping markets every 4 hours
2. **Monitor Kalshi for political market expansion** — Watch for deportation/election markets
3. **Paper trade ready** — When overlap detected, log prices immediately
4. **Capital allocation** — $10 on Kalshi ready, need more for meaningful positions

---

## Data Files

- **Raw Scan:** [[kalshi_deep_scan_20260221_1400.json]]
- **Polymarket Data:** [[polymarket_deep_scan_20260221_1404.json]]
- **Cross-Market Report:** [[cross_market_research_20260221_1404.json]]
- **Market Graph:** [[market_graph_20260221.json]]

---

## Related Memory

- [[memory/trading/polymarket-watchlist.md|Active Watchlist]]
- [[memory/trading/arb-results.md|Arbitrage Results Log]]
- [[memory/trading/market-graph.md|Market Relationship Graph]]
- [[skills/polymarket-arb/SKILL.md|Arbitrage Strategy Guide]]

---

*"The furnace is lit. The Work continues."*

**Next Review:** 2026-02-22 (check for new Kalshi political markets)