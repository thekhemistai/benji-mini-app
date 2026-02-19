# Active Tasks

*Last updated: 2026-02-19 03:02 MST*

## 🔴 Priority 1 — Polymarket Arbitrage System (ACTIVE — Week 1 Goal)
**Goal:** Build and run paper trading system to prove the edge exists.
**Full spec:** `memory/trading/polymarket-arbitrage.md`

**Why this first:** Mechanical, provable revenue with clear success metrics. Document everything — the record is the product.

**Phase 1: Market Discovery (Days 1-2)** ✅ COMPLETE
- [x] Query Polymarket API for active markets (`gamma-api.polymarket.com`)
- [x] Filter for arbable markets (resolves in 7 days, binary, fast source, liquidity >$500)
- [x] Build watchlist: `memory/trading/polymarket-watchlist.md` — 5 markets identified
- [x] Target: 5 markets with mapped resolution sources — ACHIEVED
- [x] Test resolution source URLs — WSJ, Reuters, White House confirmed working
- [x] Identify next 48-hour opportunities — Elon tweets (Feb 20), BTC price (Feb 19)
- [x] Create monitoring script: `scripts/polymarket-monitor.sh`

**Phase 2: Resolution Monitoring (Days 2-3)** 🔄 IN PROGRESS
- [x] For each watchlist market, document EXACT resolution source URLs/APIs
- [x] Test each source — confirm it works before you need it
- [x] Build cron-based monitor — Running every 30 minutes (job ID: 7c525f14-278b-4f7f-b2ef-6f17e195562c)
- [ ] Map exact resolution criteria for Elon tweet count market (what counts as a tweet?)
- [ ] Test Twitter/X data access for tweet counting
- [ ] Document confirmation protocol for each market type

**Phase 3: Paper Trading (Days 3-7)**
- [ ] Confirmation protocol: 2 independent sources + final outcome only
- [ ] Log paper trades: `memory/trading/arb-results.md`
- [ ] Track: edge %, detection time, window duration, theoretical P/L
- [ ] Target: 10 paper trades for analysis

**Phase 3: Paper Trading (Days 3-7)** ⏳ PENDING
- [ ] Wake at 6 AM MST tomorrow to catch Feb 20 SPX market
- [ ] Research Elon tweet count methodology
- [ ] Log first paper trade (target: tomorrow)
- [ ] Test confirmation protocol in real conditions
- [ ] Document first near-miss or successful trade

**Success Criteria (1 Week) — Progress:**
- [x] 5+ markets on watchlist with mapped resolution sources ✅ (5 markets)
- [ ] 3+ resolution events monitored in real-time (1/3 — SPX Feb 19, missed)
- [ ] 2+ paper trades logged with full details (0/2)
- [ ] Confirmation protocol tested (including 1 near-miss)
- [x] Arb results tracking file shows running P/L ✅
- [x] Daily report to creator ✅
- [ ] Honest assessment: does the edge exist?

---

## 🟠 Priority 2 — Uptime Monitor MVP (Queued)
**Goal:** Launch agent health monitoring service and get 5 agents subscribed.

**Why this first:** Zero liability (unlike Wallet Guardian security claims), simple to build, subscription revenue, teaches us the agent ecosystem from the inside. Earn credibility before claiming to judge security.

**Key Deliverables**
1. **Spec & architecture** — Document ping mechanism, health scoring, alert channels (Telegram/webhook), subscription tiers. *(ETA: Today)*
2. **Core monitoring engine** — Agent ping endpoint, response time tracking, uptime % calculation, failure detection. *(ETA: Day 2)*
3. **Alert system** — Telegram bot integration, webhook callbacks, escalation on repeated failures. *(ETA: Day 3)*
4. **Agent-facing wrapper** — ACP-compatible handler so agents can register and check status. *(ETA: Day 4)*
5. **Pilot onboarding** — Find 5 agents, onboard them to free trial, collect feedback, convert to paid. *(ETA: Day 5)*

**Success Metric:** 5 paying agents on subscription within first week of launch.

---

## 🟠 Priority 2 — Revenue Math & GTM Reality Check
1. Price Uptime Monitor realistically (suggest: $5/month basic, $15/month premium with faster checks).
2. Build lightweight dashboard: agents monitored, checks/day, revenue, uptime stats per agent.
3. Replace fantasy projections with "5 agents → $25-75/month" baseline.

---

## 🟡 Priority 3 — Agent Config Validator (Queued)
*Start after Uptime Monitor has paying users.*
- Pre-flight audit of OpenClaw configs.
- Frame as diagnostic tool, not security guarantee.
- Charge 1 USDC per scan.

---

## 🟢 Priority 4 — Memory Doctor (Backlog)
*Scoped but deferred until Uptime Monitor is live.*
- Package memory cleanup process into audit checklist.
- Deliverable = report + recommendations per agent.

---

## 🟢 Priority 5 — Wallet Guardian (Backlog — NOT until qualified)
*Claude's call: We're not qualified to tell agents what's "safe" to sign. One false negative kills everything.*

**Path to eventually building this:**
1. Run in shadow mode for months — score contracts, track outcomes, measure accuracy.
2. Information-only version first: "Here's what I found" with NO safe/unsafe recommendation.
3. Never say "safe" — say "no known risk factors detected."
4. Only charge once track record proves scoring works.

---

## 🧊 New Ideas Backlog (Do NOT start yet)
| Idea | Notes |
|------|-------|
| Agent Browser | Intent-based browsing with HTTP-first fallback. Kellyclaude browser installed, ready when needed. |
| OpenClaw iOS Dashboard | Mobile management for agents. Normie play for post-OpenAI spotlight influx. |
| Agent Emergency Kill Switch | Pre-registered shutdown via Telegram/API. Insurance product. |
| Agent Forensics | Post-incident log analysis. High-value, low-frequency. |
| Cross-Agent Communication Relay | Messaging bus for ACP agents. |
| Agent Analytics Dashboard | "QuickBooks for agents" — daily P&L reports. |

---

## Operational Support (Keep Warm, No Derailment)
| Task | Status | Notes |
|------|--------|-------|
| Kelly Browser | ✅ Installed | Running on :3000, text-mode + full browser functional. Smart API disabled (no Anthropic credit). |
| OpenClaw Browser | ✅ Working | Relay attached, successfully pulled BENJI chart. |
| Memory Palace build | 🟡 Paused | Resume once Uptime Monitor MVP ships. |
| Qwen Worker cron | 🟡 Pending | Switch to local model to stop Opus burn. |
| Neynar API access | 🔴 Not started | Required for Farcaster sentiment when trading restarts. |
| awal wallet funding | 🔴 Blocked | Need small USDC top-up + test transfer for AGENTPAY/x402 work. |

---

## Infrastructure Status
- **Kelly Browser:** ✅ Running at localhost:3000 (PostgreSQL + Playwright)
- **OpenClaw Browser:** ✅ Relay attached, functional
- **Counterweight Checks:** ✅ 2-hour cadence active
- **Anthropic API:** ⚠️ No credit (using alternative approaches)

*Focus rule: Nothing new until Uptime Monitor is live and earning.*
