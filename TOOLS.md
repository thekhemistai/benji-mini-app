# TOOLS.md - Local Notes

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

**Primary:** DexScreener (dexscreener.com) — Use browser to navigate directly to token pages
- Format: `https://dexscreener.com/base/{token-address}`
- Example: `https://dexscreener.com/base/0xBC45647eA894030a4E9801Ec03479739FA2485F0`
- Shows: Price, volume, % change (5M/1H/6H/24H), liquidity, market cap, buy/sell flow

**Secondary:** Bankr (if available via Bankr integration) — For live chart data

**Remember:** Don't jump to on-chain SQL queries for basic price checks. DexScreener has all the data and is free. Use CDP SQL API only when you need deep on-chain analysis (wallet flows, transfer tracing, etc.).

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

Add whatever helps you do your job. This is your cheat sheet.
