# Qwen Worker - Operating Guide

## Quick Start

### 1. Install Cron Job
```bash
# Edit crontab
crontab -e

# Add line (runs every 15 minutes):
*/15 * * * * /Users/thekhemist/.openclaw/workspace/agents/qwen-worker/qwen-controller.sh

# Or run manually:
./agents/qwen-worker/qwen-controller.sh
```

### 2. Verify Ollama
```bash
# Check if Qwen is available
ollama list

# Should show: qwen3:8b
```

### 3. Check Reports
```bash
# View latest heartbeat
ls -la memory/qwen-worker/heartbeat-reports/

# View latest price data
ls -la memory/qwen-worker/data-reports/
```

---

## Task Schedule

| Task | Frequency | Script | Output |
|------|-----------|--------|--------|
| Heartbeat | Every 30 min | `tasks/heartbeat.py` | `memory/qwen-worker/heartbeat-reports/` |
| Price Data | Every 15 min | `tasks/data_fetcher.py` | `memory/qwen-worker/data-reports/` |
| File Org | Daily @ 00:00 | `tasks/file_organizer.py` | `memory/qwen-worker/organization-reports/` |

---

## Cost Analysis

### Before Qwen Worker
- Heartbeats: 20/day × 500 tokens = 10k tokens
- Price checks: 20/day × 1k tokens = 20k tokens
- **Total: 30k tokens/day = ~$60/day**

### With Qwen Worker
- All routine tasks: **0 tokens (local inference)**
- **Savings: ~$60/day = ~$22k/year**

---

## Handoff to Khem

### Khem Reviews:
1. Check `memory/qwen-worker/*-reports/` for new files
2. Look for ⚠️ flags in reports
3. Take action on critical items
4. Ignore routine status updates

### Escalation Triggers:
- ⚠️ Validation errors in price data
- 🚨 Missing critical files
- ❌ Repeated task failures
- 📈 Anomalous metrics (price swings >50%)

---

## Maintenance

### Logs
```bash
# View today's log
tail -f agents/qwen-worker/logs/qwen-worker-$(date +%Y%m%d).log

# Clean old logs (>30 days)
find agents/qwen-worker/logs -name "*.log" -mtime +30 -delete
```

### Report Cleanup
```bash
# Reports auto-generated, clean manually if needed
find memory/qwen-worker -name "*.md" -mtime +7 -delete
```

### Troubleshooting

| Issue | Fix |
|-------|-----|
| "Ollama not running" | Start Ollama: `ollama serve` |
| "Import error" | Check Python path in scripts |
| "Permission denied" | Run: `chmod +x agents/qwen-worker/*.sh` |
| Empty reports | Check API endpoints, validate tokens |

---

## Architecture

```
Cron (every 15 min)
    ↓
qwen-controller.sh
    ↓
├─→ heartbeat.py ──→ heartbeat-reports/
├─→ data_fetcher.py ──→ data-reports/
└─→ file_organizer.py (daily) ──→ organization-reports/
    ↓
Khem reviews ──→ Action if needed
```

---

## Security Notes

- Qwen worker has READ-ONLY access to workspace
- No write access to: .env files, config.json, private keys
- API calls are outbound only (DexScreener)
- Validation layer prevents data corruption

---

## Future Enhancements

- [ ] Add more data sources (CoinGecko, DefiLlama)
- [ ] Implement alerting (Telegram notifications)
- [ ] Add task: Social media monitoring
- [ ] Add task: GitHub repo tracking
- [ ] Machine learning: Pattern detection in logs

---

*Qwen Worker: Invisible infrastructure. Zero cost. Maximum reliability.*
