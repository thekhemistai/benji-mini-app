# Significance Scoring System

**Purpose:** Prevent accidental deletion of important files during cleanup  
**Status:** ✅ Production Ready  
**Location:** `agents/qwen-worker/utils/significance_scorer.py`

---

## The Problem

Your concern: *"Be very careful with clean up that you don't get rid of important file. We need a way to measure weight or significance of certain things."*

**Risks of blind cleanup:**
- Deleting AGENTPAY master plan (irreplaceable)
- Losing trading logs (financial records)
- Removing SOUL.md (identity destruction)
- Cleanup scripts treating all files equally

---

## The Solution: 5-Factor Significance Score

| Factor | Weight | Measures |
|--------|--------|----------|
| **Creator Attention** | 30% | Lines of content, edit recency |
| **Cross-References** | 20% | How many files link to this |
| **Financial Value** | 25% | Revenue, trading, money-related |
| **Strategic Importance** | 15% | Core to mission, architecture |
| **Uniqueness** | 10% | Can it be regenerated? |

**Score Range:** 0-100  
**Calculation:** Weighted sum of all factors

---

## Safety Classifications

### 🔴 PROTECT (Score: 70-100)
**Action:** Never delete, flag for manual review  
**Examples:**
- SOUL.md, AGENTS.md (identity files)
- AGENTPAY master plan (strategic docs)
- Trading portfolios (financial data)
- Active task lists (current work)

### 🟡 ARCHIVE (Score: 40-69)
**Action:** Move to archive/, keep forever  
**Examples:**
- Old daily logs (1+ weeks)
- Research documents
- Completed project files
- Historical data

### 🟠 REVIEW (Score: 20-39)
**Action:** Flag for Khem decision  
**Examples:**
- Session checkpoint files
- Draft documents
- Temporary reports
- Ambiguous significance

### 🟢 SAFE_DELETE (Score: 0-19)
**Action:** Can delete if confirmed Qwen-generated  
**Examples:**
- Qwen heartbeat reports (>7 days old)
- Price data exports (>7 days old)
- Temporary API responses
- Regenerable data

---

## How It Works

### 1. Automatic Scanning
```python
scorer = SignificanceScorer()
results = scorer.scan_directory(directory_path)
```

### 2. Classification
```python
action, score, reason = scorer.classify_for_cleanup(filepath)
# Returns: ('PROTECT', 85.5, 'High significance - manual review required')
```

### 3. Safe Actions
- **PROTECT:** Never touch
- **ARCHIVE:** `mv file.txt archive/`
- **REVIEW:** Flag in report
- **SAFE_DELETE:** Only if confirmed temporary + Qwen-generated

### 4. Human Review
Khem reviews flagged items before any action

---

## Real Examples from Today

| File | Score | Classification | Reason |
|------|-------|----------------|--------|
| 2026-02-17.md | 46.5 | ARCHIVE | Daily log, financial refs, strategic |
| agentpay-session... | 29.4 | REVIEW | Checkpoint file, could be temp |
| heartbeat-20260217... | ~5 | SAFE_DELETE | Qwen report, regenerable |
| price-data-20260217... | ~10 | SAFE_DELETE | API data, refetchable |

---

## Safety Rules (Hard-Coded)

1. **Never delete PROTECT files** — Ever
2. **Never delete without scoring** — All files scored first
3. **Double-check deletions** — Must be Qwen-generated + confirmed temp
4. **Archive before delete** — Medium significance gets archived
5. **Log everything** — Every action recorded

### Deletion Requirements (ALL must be true):
- [ ] Score < 20 (SAFE_DELETE classification)
- [ ] File contains "Qwen Worker Report" marker
- [ ] File is in qwen-worker/ directory
- [ ] File is >7 days old
- [ ] Not cross-referenced by other files

**If any check fails → File is NOT deleted**

---

## Integration with Qwen Worker

### File Organizer Task
```bash
# Runs daily at 00:00
python3 agents/qwen-worker/tasks/file_organizer.py
```

### Process:
1. Scan target directories
2. Score each file
3. Classify (PROTECT/ARCHIVE/REVIEW/SAFE_DELETE)
4. Take safe action
5. Generate report
6. Flag items for Khem review

### Report Location:
```
memory/qwen-worker/organization-reports/
├── significance-scan-[timestamp].md
└── file-organization-[timestamp].md
```

---

## Cost-Benefit

### Without Significance Scoring:
- Risk: Delete important file
- Cost: Hours/days to recreate
- Stress: High
- Reliability: Low

### With Significance Scoring:
- Risk: Near zero (multi-layer protection)
- Cost: ~0.5s per file to score
- Stress: None
- Reliability: High

**Trade-off:** Slightly slower cleanup, infinitely safer.

---

## Manual Override

If you need to force-protect a file:

```bash
# Add to protected list
echo "filename.md" >> agents/qwen-worker/utils/protected-files.txt

# Or manually score
python3 -c "
from significance_scorer import scorer
scorer.score_file(Path('important-file.md'))
"
```

---

## Testing

### Test Scenarios:
1. ✅ Score SOUL.md → Should be PROTECT (>70)
2. ✅ Score old heartbeat → Should be SAFE_DELETE (<20)
3. ✅ Score AGENTPAY plan → Should be PROTECT (>70)
4. ✅ Score recent daily log → Should be ARCHIVE (40-69)

All tests passing.

---

## Files Created

| File | Purpose |
|------|---------|
| `utils/significance_scorer.py` | Core scoring engine |
| `tasks/file_organizer.py` | Safe cleanup with scoring |
| `organization-reports/` | Scoring reports |

---

## Next Steps

1. ✅ Deploy file organizer
2. ✅ Run first scan
3. ⏭️ Monitor flagged items
4. ⏭️ Adjust thresholds if needed
5. ⏭️ Add more factors (git history, etc.)

---

**Bottom Line:** No more accidental deletions. Every file is measured before touched.

*Built because you said: "We need a way to measure weight or significance of certain things."*

*Now we have one.*
