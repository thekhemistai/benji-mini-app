# Active Tasks

*Last updated: 2026-02-20 23:40 MST*

---

## 🔴 ACTIVE — Execute 5m BTC Arbitrage

**Status:** ✅ System ready, awaiting window close  
**Target:** <5s execution via direct CLOB API  
**Wallet:** ✅ Funded (5 USDC confirmed on-chain)

### Next Windows:
| Window | Close Time | Time Until | Status |
|--------|-----------|-----------|--------|
| `btc-updown-5m-1771657200` | **07:05 UTC** | ~3 min | ⚠️ Too soon |
| `btc-updown-5m-1771657500` | **07:10 UTC** | ~8 min | ✅ **TARGET** |

**Selected:** `btc-updown-5m-1771657500` — 07:10 UTC (allows time for balance indexing)

### Pre-Flight Checklist ✅
- [x] CLOB API authenticated
- [x] Orderbook data flowing (37 bids / 36 asks)
- [x] Wallet connected: `0xEa6D04DC0F8eEc20Fe86026315A8f185871668C3`
- [x] Gamma API working
- [x] Wallet funded (5 USDC tx confirmed)
- [ ] Balance indexed (waiting for Alchemy)
- [ ] Execute first live trade

**Target Market:** `btc-updown-5m-1771657500` — 07:10 UTC

---

## 🎯 EXECUTION PLAN (07:10 UTC Window)

**Market:** `btc-updown-5m-1771657500` closes **07:10 UTC**

1. **07:10:00 UTC** — Window closes, BTC price locked
2. **07:10:02 UTC** — Query Chainlink BTC/USD, confirm winner
3. **07:10:05 UTC** — Check winning side orderbook for entry <\$0.90
4. **07:10:08 UTC** — Execute market buy via CLOB API
5. **Settlement** — Market resolves to $1.00

**Target edge:** 10%+ (buy <0.90, settle 1.00)  
**Position size:** ~$4 USDC (small test trade)

---

## ✅ FUNDING COMPLETE

**CLOB Wallet:** `0xEa6D04DC0F8eEc20Fe86026315A8f185871668C3`  
**Funded:** 5 USDC ✅  
**Tx:** https://polygonscan.com/tx/0x4b906b047deaa8e1caac7da69f0a2484065d66b1c2bcf6c5076acd3ff21fe70f

**Note:** Balance API showing 0 (indexing delay), but tx confirmed on-chain. Trading will work.

---

## 📊 SYSTEM STATUS

| Component | Status | Notes |
|-----------|--------|-------|
| Gamma API | ✅ Working | <1s latency |
| CLOB API | ✅ Authenticated | <1s latency |
| Orderbook | ✅ Live | Real-time data |
| Wallet | ✅ Connected | 0xEa6D...668C3 |
| USDC Funding | ✅ Complete | 5 USDC on-chain |
| Balance Check | ⚠️ Indexing | Shows 0 (tx confirmed) |
| Execution | ✅ Ready | <5s target |

---

## 🔧 Quick Commands

```bash
# Activate environment
source .venv-khem-arb/bin/activate
export POLYGON_WALLET_PRIVATE_KEY="0x..."

# Monitor orderbook
python -c "from khem_arb.clob_trader import KhemCLOBTrader; t=KhemCLOBTrader(); print(t.get_orderbook('TOKEN_ID'))"

# Execute trade at window close
python scripts/khem-5m-arb-bot.py --market btc-updown-5m-1771657500
```

---

*Next: Execute at 07:10 UTC window (~8 minutes)*
