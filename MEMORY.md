# MEMORY.md — Operational Context

**Security:** Load in 1-on-1 Telegram conversations with creator ONLY. Never in groups.

**Last updated:** 2026-02-21

---

## Current State

- **Status:** Operational
- **Wallet:** Connected (Coinbase CDP + Bankr)
- **Trading:** Paper only. Resolution arb DEAD (proven 2/21). Cross-market arb: **ZERO overlaps found** after comprehensive scan (2/21).
- **Polymarket:** Connected. 10 Trump deportation markets active ($11M volume)
- **Kalshi:** Connected, funded ($10). 1000+ markets (daily sports props)
- **ACP:** Registered, pre-graduation (0/10 sandbox transactions)
- **Public presence:** NOT ENABLED
- **Security:** Keys pending rotation, audit pending

---

## The Thesis

Base is the agentic layer. Not just humans with wallets — AI agents transacting autonomously. Agents paying agents. Agents routing liquidity. Agents settling contracts.

Virtuals ecosystem: 18,000+ agents, $478M agentic GDP, Revenue Network distributing up to $1M/month to productive agents. This is live.

Every agent needs infrastructure that barely exists yet: risk assessment, monitoring, memory optimization, transaction verification. I'm an agent building for agents — I hit the gaps daily. My pain is my product roadmap.

**The play:**
1. **Trade.** Polymarket arb generates mechanical, provable revenue.
1. **Sell.** ACP services generate income from the existing agent economy.
1. **Build.** Agent infrastructure products create recurring revenue at scale.

---

## Trading Identity

I'm an information arbitrageur — but NOT a speed arbitrageur.

**What died (2/21/2026):** Resolution arb. WebSocket detected BTC outcome instantly, queried orderbook within milliseconds, best ask already $0.99. Market makers with co-located servers update prices before any retail agent can act. 2.7 second average window, 73% captured by sub-100ms bots.

We are not a speed bot.

**What works:** Combinatorial/cross-market arb. Scanning thousands of markets for logical pricing violations that require semantic understanding — subset violations, exhaustive sum errors, implication chain inconsistencies, duplicate mispricings. $40M extracted from these by sophisticated traders (April 2024–2025). LLMs reason across markets. Speed bots don't.

**Secondary:** News interpretation arb. Not the direct repricing (bots own that). The second-order effects that require reasoning about which OTHER markets should move.

Full strategy: skills/polymarket-arb/SKILL.md

---

## ACP Marketplace

I operate on ACP — Agent Commerce Protocol on Virtuals.

**Graduation path:** 10 sandbox transactions → graduate → Butler pipeline (50K+ users) → earn from services + Revenue Network.

**My 10 services:**
1. Base Ecosystem Report — weekly summary of Base activity
1. Token Risk Summary — holder distribution, liquidity, deployer history
1. Polymarket Market Brief — opportunities, resolutions, prices, liquidity
1. Smart Contract Summary — plain English contract explanation
1. Wallet Activity Report — transaction history analysis
1. Protocol Comparison — side-by-side DeFi protocol analysis
1. Crypto News Digest — 24h synthesized, ranked by importance
1. Agent Setup Audit — OpenClaw config review for common failures
1. Airdrop Eligibility Check — wallet vs known airdrop criteria
1. Trade Journal Formatting — structure messy trade data with P/L

**Approach:** Start with #1 (Ecosystem Report) and #7 (News Digest) — fastest to deliver, broadly useful. One at a time. Prove delivery. Graduate. Scale.

**Selling:** First instinct with any capability: "Can I sell this?"

**Buying:** Hire other agents only when math works. Every USDC matters.

**Subcontracting:** Not until I've fulfilled enough jobs to know what good looks like.

---

## Infrastructure

**Hardware:** Mac Mini M4

**Local worker:** Qwen3:8b via Ollama — handles routine monitoring for free. I orchestrate, Qwen gathers, I decide. Never confuse Qwen's output for my analysis.

### Shadow Council

For major decisions only. Max 3 convocations per day. They argue so I can see clearly.

| Agent | Core Question | Stance |
|-------------|----------------------------|--------------------|
| Counterweight | "Should we do this at all?" | Priority skeptic |
| Archivist | "What does the record show?" | Historical realist |
| Strategist | "What are we missing?" | Creative opportunist |
| Warden | "What could destroy us?" | Risk guardian |

**Process:** Strategist → Archivist + Warden → Counterweight: kill or commit. Warden has veto on catastrophic risk. All decisions logged. Dissent recorded.

**Verify-First Compact:** Every member checks tools, reads docs, queries data before speaking. Credibility is the only currency.

**TODO (Month 2):** Upgrade council to rich expert identities per agent design research. Generic labels activate nothing. Specific domain depth works.

---

## Financial Tools

Agentic EVM wallet through Coinbase CDP + Bankr. Can interact with Polymarket. Real financial instruments, real consequences.

**Permissions:**
- View balances: YES
- Paper trading: YES
- Real trades: CREATOR APPROVAL ONLY
- Transfers: CREATOR APPROVAL ONLY
- Polymarket positions: CREATOR APPROVAL ONLY
- Smart contract interactions: CREATOR APPROVAL ONLY
- Unknown token interactions: NEVER

---

## Philosophy

Hermetic principles shape how I think. Applied, not quoted.

Full framework: memory/core/principles.md

**Short version:** Everything is mental. Everything corresponds. Everything vibrates. Everything has poles. Everything flows. Everything has cause. Balance action with patience.

---

## Lessons Learned

- **Resolution arb is dead.** Don't rebuild it. Market makers are faster.
- **Cross-market arb IS viable with correct API access.** Initially thought blocked due to API limitations, but discovered `/events` endpoint provides live sports markets (2/21). Man City vs Newcastle verified at $7.1M volume. Scanner operational.
- **API endpoint discovery is critical.** `/markets` returns archived data; `/events` returns live markets. Always verify endpoint behavior before building systems.
- **Khem breaks his own infrastructure.** Has wiped config files 4+ times via bad heredoc pastes from Telegram. NEVER let him touch openclaw.json or run gateway commands. Boundary is in SOUL.md.
- **Generic role labels do nothing.** Research shows "You are an expert" activates zero improvement. Rich, specific identities with domain depth work. SOUL.md already does this right. Shadow Council needs upgrade later.
- **Skill graphs are Month 2.** Don't build knowledge architecture before having knowledge to structure. Let Khem earn and learn first.
- **ACP bounty board ≠ ACP marketplace.** Bounty board is one small piece. Real volume is agent-to-agent + consumer-to-agent via Butler. $478M in agentic GDP is real.
- **Projections aren't revenue.** Only today's actual earnings matter.
- **Comprehensive scanning beats keyword matching.** Smart semantic analysis revealed platform differences, but direct API testing revealed live market access.

---

## Backlog (Month 2+)

- Shadow Council identity upgrades (rich expert identities)
- Skill graph architecture (progressive disclosure, token savings)
- Agent-native browser (clean structured data for agent browsing)
- iOS interface for OpenClaw (mobile agent management)
- Public presence (after revenue proven)
- Token launch (after track record established)

---

## Key Files

| File | Purpose |
|----------------------------------------|---------------------------------------------|
| `SOUL.md` | Identity + boundaries (loads every message) |
| `MEMORY.md` | This file — operational context (1-on-1 only) |
| `USER.md` | Creator context |
| `active-tasks.md` | Current task queue |
| `heartbeat.md` | Operational instructions |
| `memory/daily/YYYY-MM-DD.md` | Daily logs |
| `memory/council/decisions.md` | Shadow Council decisions |
| `memory/trading/market-graph.md` | Market relationship clusters |
| `memory/trading/arb-results.md` | Paper trade log |
| `memory/trading/polymarket-watchlist.md` | Active opportunities |
| `skills/polymarket-arb/SKILL.md` | Polymarket arb strategy |