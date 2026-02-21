# Active Tasks

*Last updated: 2026-02-20 23:40 MST*

---

## 🔴 ACTIVE — Execute 5m BTC Arbitrage at 07:50 UTC

**Status:** ✅ System ready, awaiting window close  
**Window:** `btc-updown-5m-1771659900` closes **07:50 UTC** (~1h 10m)  
**Target:** <5s execution via direct CLOB API

### Pre-Flight Checklist ✅
- [x] CLOB API authenticated
- [x] Orderbook data flowing (37 bids / 36 asks)
- [x] Wallet connected: `0xEa6D04DC0F8eEc20Fe86026315A8f185871668C3`
- [x] Gamma API working
- [ ] Fund wallet with USDC (pending - need ~$50 for test trade)
- [ ] Execute first live trade

**Current Market:**
- UP: Best ask 0.99¢ / Best bid 0.01¢
- DOWN: Best ask 0.99¢ / Best bid 0.01¢
- Current mid: 50.5¢ UP / 49.5¢ DOWN

---

## 🎯 EXECUTION PLAN (07:50 UTC)

1. **07:50:00 UTC** — Window closes, BTC price locked
2. **07:50:05 UTC** — Query Chainlink BTC/USD, confirm winner
3. **07:50:10 UTC** — Check winning side orderbook
4. **07:50:15 UTC** — Execute if spread exists (<$0.90 entry)
5. **Settlement** — Market resolves to $1.00

**Target edge:** 10%+ (buy <0.90, settle 1.00)

---

## ⚠️ FUNDING REQUIRED

**CLOB Wallet:** `0xEa6D04DC0F8eEc20Fe86026315A8f185871668C3`
**Need:** USDC for trading (recommend $50-100 for first test)

**Options:**
1. Deposit from Bankr wallet (has 164 POL ~$17)
2. Direct deposit to address
3. Skip this window, fund for next one

**Note:** Balance checking has RPC issues (public endpoints), but trading API works fine.

---

## 📊 SYSTEM STATUS

| Component | Status | Notes |
|-----------|--------|-------|
| Gamma API | ✅ Working | <1s latency |
| CLOB API | ✅ Authenticated | <1s latency |
| Orderbook | ✅ Live | Real-time data |
| Wallet | ✅ Connected | 0xEa6D...668C3 |
| Balance Check | ⚠️ RPC limited | Trading still works |
| USDC Balance | ⏸️ Unknown | Need funding |

---

## 🔧 Quick Commands

```bash
# Activate environment
source .venv-khem-arb/bin/activate
export POLYGON_WALLET_PRIVATE_KEY="0x..."

# Check orderbook
python -c "from khem_arb.clob_trader import KhemCLOBTrader; t=KhemCLOBTrader(); print(t.get_orderbook('TOKEN_ID'))"

# Execute trade (when ready)
python -c "from khem_arb.clob_trader import KhemCLOBTrader; t=KhemCLOBTrader(); t.execute_arbitrage_trade(market, 'UP')"
```

---

## 🚫 BLOCKERS

| Blocker | Action | ETA |
|---------|--------|-----|
| USDC funding | Deposit to CLOB wallet | Before 07:50 UTC |

---

*Next: Wait for 07:50 UTC window or fund wallet for future trades*
