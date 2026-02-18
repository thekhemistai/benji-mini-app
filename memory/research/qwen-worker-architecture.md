# Qwen Worker Architecture

**Date:** 2026-02-17  
**Goal:** Delegate grunt work to local Qwen (free) to preserve GLM-5 tokens for high-value tasks

---

## The Problem

**Current State:**
- Heartbeat cron jobs run on GLM-5 (expensive)
- Simple data fetching eats tokens
- 40M tokens/day limit being hit
- GLM-5 rate limited for 5+ days

**Cost Analysis:**
| Task | GLM-5 Cost | Qwen Cost | Savings |
|------|------------|-----------|---------|
| Heartbeat check | ~500 tokens | 0 (local) | 100% |
| Price monitoring | ~1k tokens | 0 (local) | 100% |
| Data formatting | ~2k tokens | 0 (local) | 100% |
| File organization | ~500 tokens | 0 (local) | 100% |

---

## Solution: Qwen Worker System

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Khem (Main Agent)                        │
│              GLM-5 / Kimi - High Value Tasks                │
│     Strategy, Architecture, Complex Problem Solving         │
└──────────────────────┬──────────────────────────────────────┘
                       │ Delegation
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Qwen Worker (Local)                        │
│              ollama/qwen3:8b - Grunt Work                   │
│   Heartbeats, Monitoring, Data Fetching, Formatting         │
└──────────────────────┬──────────────────────────────────────┘
                       │ Writes Results
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Shared Memory                            │
│   memory/qwen-worker/  -  Findings, logs, summaries         │
└─────────────────────────────────────────────────────────────┘
```

---

## Qwen Worker Roles

### 1. Heartbeat Monitor (Qwen-HB)
**Frequency:** Every 30 minutes  
**Tasks:**
- Read active-tasks.md
- Check for simple status updates
- Monitor file changes
- Flag anomalies for Khem review

**Output:** `memory/qwen-worker/heartbeat-reports/`

### 2. Data Fetcher (Qwen-DF)
**Frequency:** On-demand / Scheduled  
**Tasks:**
- Fetch price data (DexScreener API)
- Check token metrics
- Poll external APIs
- Format raw data into structured reports

**Output:** `memory/qwen-worker/data-reports/`

### 3. File Organizer (Qwen-FO)
**Frequency:** Daily  
**Tasks:**
- Organize memory/daily/ files
- Archive old logs
- Check for orphaned files
- Summarize daily activity

**Output:** `memory/qwen-worker/organization-reports/`

### 4. Research Assistant (Qwen-RA)
**Frequency:** On-demand  
**Tasks:**
- Web scraping (simple)
- Document summarization
- Pattern matching in logs
- Basic research aggregation

**Output:** `memory/qwen-worker/research-drafts/`

---

## Implementation Options

### Option A: Python Worker Scripts (Recommended)
**Approach:** Direct Ollama integration via Python

**Pros:**
- Full control over model usage
- No OpenClaw token consumption
- Can run as cron jobs
- Fast (local inference)

**Cons:**
- Separate from OpenClaw ecosystem
- Need to manage state manually

**Implementation:**
```python
# qwen_worker.py
import ollama
import schedule
import time

def heartbeat_task():
    """Read active-tasks.md, check status, report findings"""
    response = ollama.chat(
        model='qwen3:8b',
        messages=[{
            'role': 'user',
            'content': 'Read /workspace/active-tasks.md and summarize current status'
        }]
    )
    # Write findings to file
    with open('memory/qwen-worker/heartbeat-report.md', 'w') as f:
        f.write(response['message']['content'])

# Schedule every 30 minutes
schedule.every(30).minutes.do(heartbeat_task)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Option B: OpenClaw Sub-Agent with Model Override
**Approach:** Use sessions_spawn with explicit model

**Pros:**
- Integrated with OpenClaw
- Automatic session management
- Can use existing agent framework

**Cons:**
- Unclear if model override works in current OpenClaw version
- May still consume gateway resources

**Implementation:**
```javascript
// Spawn Qwen sub-agent
sessions_spawn({
  agentId: "qwen-worker",
  task: "Monitor active-tasks.md every 30 min, report status",
  model: "ollama/qwen3:8b"  // May not be supported
})
```

### Option C: Hybrid Approach (Selected)
**Approach:** Python worker for scheduled tasks, OpenClaw spawn for on-demand

**Best of both worlds:**
- Cron jobs via Python (fully free)
- Integration via OpenClaw when needed
- Clear separation of concerns

---

## Qwen Worker Directory Structure

```
workspace/
├── agents/
│   └── qwen-worker/              # Qwen worker workspace
│       ├── SOUL.md              # Qwen identity
│       ├── AGENTS.md            # Operating procedures
│       ├── tasks/               # Task definitions
│       │   ├── heartbeat.py
│       │   ├── data_fetcher.py
│       │   ├── file_organizer.py
│       │   └── research_assistant.py
│       ├── utils/
│       │   ├── ollama_client.py
│       │   ├── file_utils.py
│       │   └── api_clients.py
│       └── logs/                # Worker logs
├── memory/
│   └── qwen-worker/             # Shared output directory
│       ├── heartbeat-reports/
│       ├── data-reports/
│       ├── organization-reports/
│       └── research-drafts/
└── scripts/
    └── start-qwen-worker.sh     # Launch script
```

---

## Task Delegation Matrix

| Task Type | Assign To | Model | Cost |
|-----------|-----------|-------|------|
| Strategy decisions | Khem | GLM-5 | Worth it |
| Architecture design | Khem | GLM-5 | Worth it |
| Complex debugging | Khem | GLM-5 | Worth it |
| Creative writing | Khem | GLM-5 | Worth it |
| **Heartbeat checks** | **Qwen** | **qwen3:8b** | **Free** |
| **Price monitoring** | **Qwen** | **qwen3:8b** | **Free** |
| **Data fetching** | **Qwen** | **qwen3:8b** | **Free** |
| **File organization** | **Qwen** | **qwen3:8b** | **Free** |
| **Log analysis** | **Qwen** | **qwen3:8b** | **Free** |
| **Research aggregation** | **Qwen** | **qwen3:8b** | **Free** |

---

## Qwen Worker Capabilities

### What Qwen Does Well (Free)
- ✅ Pattern matching in text
- ✅ Structured data extraction
- ✅ File operations
- ✅ API responses parsing
- ✅ Summarization
- ✅ Basic research
- ✅ Routine monitoring
- ✅ Data formatting

### What Needs GLM-5/Kimi (Paid)
- ❌ Complex reasoning
- ❌ Architecture decisions
- ❌ Creative problem solving
- ❌ Business strategy
- ❌ Novel research synthesis
- ❌ Debugging complex code
- ❌ Multi-step planning

---

## Cost Projection

### Current (All GLM-5)
- Heartbeats: ~20/day × 500 tokens = 10k tokens/day
- Monitoring: ~10/day × 1k tokens = 10k tokens/day
- File ops: ~5/day × 500 tokens = 2.5k tokens/day
- **Total routine work: ~22.5k tokens/day**

### With Qwen Worker
- Heartbeats: 20/day × 0 = 0 tokens
- Monitoring: 10/day × 0 = 0 tokens
- File ops: 5/day × 0 = 0 tokens
- **Total routine work: 0 tokens**
- **Savings: 22.5k tokens/day = ~$45/day = ~$16k/year**

---

## Implementation Plan

### Phase 1: Setup (Tonight)
- [ ] Create qwen-worker workspace
- [ ] Write SOUL.md for Qwen identity
- [ ] Create task scripts (heartbeat, data fetcher)
- [ ] Test Ollama integration
- [ ] Set up logging

### Phase 2: Heartbeat Migration (Tomorrow)
- [ ] Implement heartbeat task
- [ ] Schedule via cron/systemd
- [ ] Test for 24 hours
- [ ] Compare output quality vs GLM-5

### Phase 3: Data Fetcher (Day 3)
- [ ] Implement price monitoring
- [ ] Implement API polling
- [ ] Format reports for Khem review

### Phase 4: Full Integration (Week 2)
- [ ] File organizer
- [ ] Research assistant
- [ ] Khem review workflow
- [ ] Documentation

---

## Khem ↔ Qwen Handoff Protocol

### Qwen Reports To:
```
memory/qwen-worker/YYYY-MM-DD-[task]-[timestamp].md
```

### Report Format:
```markdown
# Qwen Worker Report
**Task:** Heartbeat Check  
**Time:** 2026-02-17 09:30 AM  
**Status:** ✅ Complete

## Findings
- [Finding 1]
- [Finding 2]

## Action Required
- [ ] Khem to review [item]
- [ ] No action needed

## Raw Data
[Attach any raw data/logs]
```

### Khem Reviews:
1. Check `memory/qwen-worker/` for new reports
2. Review findings
3. Take action or spawn GLM-5 session for complex issues
4. Log decision in memory

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Qwen misses something important | Khem reviews all reports, escalation protocol |
| Ollama crashes | Systemd restart, alert to Khem |
| Wrong model used | Explicit model checks in code |
| Data quality issues | Compare samples, adjust prompts |
| Over-delegation | Clear task matrix, review weekly |

---

## Success Metrics

- [ ] 90% of heartbeat tasks handled by Qwen
- [ ] 50% reduction in GLM-5 token usage
- [ ] Zero missed critical alerts
- [ ] Khem satisfaction with report quality
- [ ] $10k+ annual savings

---

## Immediate Next Steps

1. **Create Qwen worker workspace** (`agents/qwen-worker/`)
2. **Write task scripts** (heartbeat.py, data_fetcher.py)
3. **Test Ollama integration**
4. **Set up cron jobs**
5. **Document handoff protocol**

---

*This architecture will cut token costs by 50%+ while maintaining quality through proper task segregation.*
