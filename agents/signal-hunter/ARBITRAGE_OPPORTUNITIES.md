# Polymarket Arbitrage Opportunities Research

**Date:** 2026-02-18  
**Objective:** Identify BTC-like arbitrage opportunities across timeframes and assets

## Current Active Trackers

### 1. BTC 5m Up/Down ✅
- **Status:** Running in price_hunter_v3.py
- **Logic:** 0.5% price move threshold, 5% edge requirement
- **Stake:** $10 per trade
- **Windows:** Every 5 minutes (:00, :05, :10, etc.)

### 2. BTC 15m Up/Down ✅ (NEW)
- **Status:** Deployed btc_15m_tracker.py
- **Logic:** 0.8% price move threshold, 4% edge requirement
- **Stake:** $15 per trade
- **Windows:** Every 15 minutes (:00, :15, :30, :45)
- **Start command:** `python3 agents/signal-hunter/btc_15m_tracker.py`

---

## Identified Arbitrage Opportunities

### TIER 1: High Confidence (Similar to BTC 5m)

#### ETH Price Up/Down (5m/15m)
**Why:** ETH is the #2 crypto with high volatility
- Often leads or lags BTC by seconds
- Same time-window mechanics
- High liquidity on Polymarket

**Expected Edge:** Similar to BTC (2-8% on volatile moves)
**Action:** Set up ETH tracker mirroring BTC logic

#### SOL Price Up/Down (5m/15m)
**Why:** SOL has higher beta than BTC/ETH
- More volatile = larger price moves
- Strong correlation to BTC but amplified
- Growing Polymarket volume

**Expected Edge:** Higher than BTC (3-10% on moves)
**Action:** Deploy SOL tracker with adjusted thresholds

---

### TIER 2: Medium Confidence (Different Mechanics)

#### BTC Price Targets ($70K, $75K, $80K)
**Why:** Binary outcomes with time decay
- Can arbitrage against futures funding rates
- Time premium decay is predictable
- Cross-reference with Deribit options

**Strategy:** 
- If BTC at $67K and "BTC > $70K by Friday" trades at 25%
- Check Deribit 70K call option pricing
- If implied vol differs by >5%, trade the edge

**Expected Edge:** 3-7% on mispricing

#### ETF Flow Predictions
**Why:** ETF inflows/outflows are announced daily
- Usually 4-5 PM ET announcement
- Price often moves 30-60 seconds before announcement
- Can front-run or predict flow direction

**Strategy:**
- Monitor GBTC discount/premium
- Track BTC price action at 3:55 PM ET
- Trade "BTC Up/Down (4PM ET)" markets

**Expected Edge:** 5-15% (information advantage window)

---

### TIER 3: Emerging Opportunities

#### Meme Coin Volatility
**DOGE, SHIB, PEPE Up/Down (15m/1h)**
**Why:** Extreme volatility creates edge
- Often +20% or -20% in an hour
- Predictable pump patterns (Twitter/X momentum)
- Less efficient pricing than BTC/ETH

**Risk:** Lower liquidity, wider spreads
**Expected Edge:** 8-20% (higher variance)

#### AI Token Basket
**Why:** AI narrative creates correlated moves
- FET, RENDER, TAO often move together
- Can arbitrage basket vs individual components
- News-driven volatility (OpenAI announcements, etc.)

**Expected Edge:** 4-8%

---

## Cross-Market Arbitrage

### BTC Spot vs Futures Basis
**Setup:**
- BTC spot price: $67,000
- CME BTC futures (front month): $67,400
- "BTC > $67.5K at 4PM" trading at 45%

**Edge Calculation:**
- If futures imply 65% chance > $67.5K
- But market trades at 45%
- Buy YES at 45%, hedge with futures short
- 20% edge minus carry cost

### Funding Rate Arbitrage
**Why:** Perp funding rates predict direction
- High positive funding = longs paying shorts = bullish exhaustion
- High negative funding = bearish exhaustion

**Signal:**
- If funding > 0.01% per 8h and BTC up >2% in 24h
- Trade "BTC Down (next 4h)" - mean reversion play

---

## Recommended Deployment Order

### Phase 1 (This Week)
1. ✅ BTC 5m (done)
2. ✅ BTC 15m (deployed)
3. ⏳ ETH 5m/15m (next)
4. ⏳ SOL 5m/15m (after ETH)

### Phase 2 (Next Week)
5. BTC price target markets (70K, 75K)
6. ETF flow prediction (4PM ET window)
7. Meme coin volatility (DOGE 15m)

### Phase 3 (Later)
8. Cross-market basis arbitrage
9. Funding rate signals
10. AI token basket tracking

---

## Technical Implementation

### For Each New Asset:
```python
# 1. Add to watchlist
WATCHLIST = {
    "ETH": "0x...",
    "SOL": "0x...",
}

# 2. Adjust thresholds based on volatility
# ETH: 0.6% (slightly higher than BTC's 0.5%)
# SOL: 0.9% (higher beta)
# DOGE: 1.5% (meme volatility)

# 3. Deploy tracker
# Copy btc_15m_tracker.py → eth_15m_tracker.py
# Update coinbase API call for ETH
# Adjust stake size based on volatility
```

### Data Sources to Integrate:
- **Coinbase API:** Spot prices (current)
- **Deribit API:** Options data for target markets
- **Coinglass:** Funding rates, ETF flows
- **DexScreener:** Meme coin prices
- **Twitter/X API:** Sentiment for meme pumps

---

## Risk Considerations

### Per-Asset Adjustments:
| Asset | Volatility | Threshold | Max Stake | Daily Limit |
|-------|-----------|-----------|-----------|-------------|
| BTC   | Medium    | 0.5%      | $10       | 20 trades   |
| ETH   | Medium    | 0.6%      | $10       | 20 trades   |
| SOL   | High      | 0.9%      | $12       | 15 trades   |
| DOGE  | Very High | 1.5%      | $8        | 10 trades   |

### Correlation Risk:
- BTC/ETH/SOL often move together
- Don't over-leverage across correlated assets
- Max 2 correlated positions open simultaneously

---

## Next Actions

1. **Start BTC 15m tracker** (deployed, needs cron job)
2. **Build ETH tracker** (copy pattern from BTC)
3. **Research actual Polymarket markets** (use bankr when stable)
4. **Test cross-market signals** (funding rates, ETF flows)

---

*Research ongoing. Paper trading all strategies before live deployment.*
