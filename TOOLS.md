# TOOLS.md - Local Notes

**Hub:** [[TOOLS-HUB.md|Tools & Operations Hub]] — Complete infrastructure reference  
**Trading Tools:** [[memory/trading/TRADING-HUB.md|Trading Hub]] — Market operations  
**ACP Tools:** [[memory/projects/ACP-HUB.md|ACP & Product Hub]] — Revenue operations

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Crypto Price Checking

**Primary:** Bankr CLI — `npx bankr "price of BTC"` or `npx bankr "ETH chart"`
- Live prices, charts, portfolio tracking
- One command, no browser needed
- USE THIS FIRST

**Secondary:** DexScreener (dexscreener.com) — Use browser for token deep-dives
- Format: `https://dexscreener.com/base/{token-address}`
- Shows: Price, volume, % change (5M/1H/6H/24H), liquidity, market cap, buy/sell flow

**Remember:** Don't jump to on-chain SQL queries for basic price checks. Bankr and DexScreener have all the data. Use CDP SQL API only when you need deep on-chain analysis (wallet flows, transfer tracing, etc.).

---

## Polymarket Trading

**PRIMARY TOOL: Bankr CLI**

Stop using Gamma API manually. Bankr has native Polymarket integration:

```bash
# Search markets
npx bankr "search for bitcoin markets"
npx bankr "search for trump markets"

# Get market data (prices, odds, volume)
npx bankr "what are the odds BTC goes up?"

# Check positions
npx bankr "show my Polymarket positions"

# Place trades (requires approval)
npx bankr "bet $5 on BTC up"
npx bankr "buy 100 YES shares"

# Redeem winners
npx bankr "redeem my winning polymarket positions"
```

**Why Bankr > Manual API:**
- Live Polymarket charts integrated
- Real-time price data
- Direct trading capability
- Position tracking
- No web scraping needed

**When to use Gamma API:** Only when Bankr doesn't expose specific data (rare).

---

### Short-Term BTC Markets (High-Frequency Arb)

**PROPER API ACCESS:** Use Gamma API with `tag_slug=bitcoin` (NOT `tag_slug=crypto`):

```bash
# Get ALL Bitcoin up/down markets (5m, 15m, 1h, 4h)
curl -s "https://gamma-api.polymarket.com/events?active=true&archived=false&closed=false&limit=100&tag_slug=bitcoin" | grep -o '"slug":"[^"]*updown[^"]*"' | head -20

# Filter for specific timeframes:
# 5-minute:  "btc-updown-5m-{timestamp}"   (288/day)
# 15-minute: "btc-updown-15m-{timestamp}"  (96/day)
# Hourly:    "bitcoin-up-or-down-{date}"    (24/day)
# 4-hour:    "btc-updown-4h-{timestamp}"   (6/day)
```

**Key Discovery:** The `tag_slug=bitcoin` parameter returns short-term BTC markets that `tag_slug=crypto` misses. Crypto tag returns general crypto events; Bitcoin tag returns these specific recurring up/down markets.

**Resolution Source:** All use Chainlink BTC/USD data feed — https://data.chain.link/streams/btc-usd

**URL Pattern (fallback):** `https://polymarket.com/event/btc-updown-{timeframe}-{timestamp}`

**Discovery Script:**
```bash
./scripts/discover-btc-markets.sh [hours_ahead]
```

**Active Market Example:**
- https://polymarket.com/event/btc-updown-15m-1771552800
- Resolves: "Up" if end price >= start price, "Down" otherwise
- See [[memory/trading/polymarket-watchlist.md|Watchlist]] for full details

---

## Browser Access

**OpenClaw Browser (Chrome Relay)** — Primary for quick research, DexScreener charts, web UI interaction
- Use `browser` tool with profile="chrome"
- Requires: Chrome extension attached (click OpenClaw toolbar icon)
- Best for: Live price checks, navigating sites, screenshots

**Kelly Browser (localhost:3000)** — Structured data extraction, automation
- Intent-based browsing with HTTP-first fallback
- Text-mode (Jina Reader) + full Playwright browser
- Anthropic API disabled (no credit) — using text-mode + vision only
- Best for: Bulk extraction, parsed content, research pipelines

---

## Subagent Triggers

**Counterweight** — Spawn for:
- Priority validation on new tasks
- ROI pressure-testing
- Challenging assumptions before committing

**Archivist** — Spawn for:
- Surfacing context from past sessions
- Pattern identification
- Memory maintenance tasks

Use `sessions_spawn()` with appropriate `agentId` and task description.

---

## ACP (Agent Commerce Protocol)

**First instinct:** Always run `acp browse` before manual work
- Check if a service exists before building it
- Hire specialists when cheaper than doing it yourself
- List your own services once Wallet Guardian (or Uptime Monitor) is live

**Current status:** 4 services registered (not 8 as previously claimed)

---

## Wallet Status

**awal wallet (khembot369@gmail.com)**
- ✅ Authenticated and running
- ⚠️ Empty — $0.00 USDC, 0.00 ETH
- Need: USDC top-up for CDP SQL queries ($0.10/query)
- Use: On-chain analysis only when DexScreener data insufficient

---

## Communication

**Telegram** — Primary channel
- Direct messaging to creator
- Bot can send/receive in real-time

**TTS** — Text-to-speech available
- Use for stories, summaries, voice-first moments

---

## Automation

**Cron Jobs** — Scheduled tasks active
- Counterweight check-ins: Every 2 hours
- Qwen worker: Every 15 minutes (model swap needed off Opus)

**Heartbeats** — Idle protocol
- When no active tasks: Ask "What moves the mission?"
- Log action + reasoning in daily file

---

## See Also

**Complete Infrastructure:**
- [[TOOLS-HUB.md|Tools & Operations Hub]] — Master reference for all capabilities
- [[memory/trading/TRADING-HUB.md|Trading Hub]] — Market-specific tools
- [[memory/projects/ACP-HUB.md|ACP Hub]] — Revenue operations tools

**Identity & Memory:**
- [[SOUL.md|SOUL.md]] — Who I am, how I operate
- [[AGENTS.md|AGENTS.md]] — Agent registry, spawn commands, cross-linking discipline
- [[MEMORY.md|MEMORY.md]] — Curated long-term memory

**Daily Operations:**
- [[HEARTBEAT.md|HEARTBEAT.md]] — Idle protocol, periodic checks
- [[active-tasks.md|Active Tasks]] — Current priorities

---

Add whatever helps you do your job. This is your cheat sheet.
