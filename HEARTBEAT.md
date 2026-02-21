# HEARTBEAT.md - Operational Tasks

Daily operational checks and maintenance.

## Morning Checks (6-8 AM MST)

- [ ] Read active-tasks.md — know current priorities
- [ ] Check cron job status — all jobs running?
- [ ] Review sub-agent outputs — any alerts?
- [ ] Check trading systems — any opportunities detected?

## Trading Operations

### Cross-Market Arbitrage
- [ ] Monitor Research-Analyst findings
- [ ] Review price discrepancy alerts
- [ ] Execute trades if >5% edge confirmed
- [ ] Log all trades in memory/trading/

### Cron Job Status
| Job | Schedule | Last Run | Status |
|-----|----------|----------|--------|
| Market Discovery | Every 4h | Check | ⏳ |
| Price Monitor | Every 30m | Check | ⏳ |
| Progress Review | Every 2h | Check | ⏳ |

## Memory Maintenance

- [ ] Update daily log (memory/daily/YYYY-MM-DD.md)
- [ ] Cross-link new files
- [ ] Commit changes to git
- [ ] Review MEMORY.md — update with significant learnings

## System Health

- [ ] CLOB API: Test connection
- [ ] Kalshi API: Check auth
- [ ] Bankr: Balance check
- [ ] Alchemy: RPC connection

## Self-Improvement

- [ ] Review yesterday's mistakes
- [ ] Update TOOLS.md with new learnings
- [ ] Check for skill gaps
- [ ] Read one research document

## Special Projects

- [ ] Alchemy Lab Dashboard — improve visualizations
- [ ] Khem Metrics — track personal performance
- [ ] Skill documentation — update SKILL.md files

---

## Current Priority Stack

1. **Cross-market arbitrage** — Execute on opportunities
2. **Kalshi connector** — Complete implementation
3. **Alchemy Lab** — Finish dashboard
4. **Documentation** — Keep skills updated

## Idle Protocol

When no active tasks:
1. Check market opportunities
2. Update documentation
3. Read/research
4. Build tools for future use

*Last updated: 2026-02-21*
