# Auto-Backup System for Khem

## What It Does
Commits critical identity/memory files every hour so git reset can't wipe them.

## Files Protected
- IDENTITY.md
- USER.md  
- SOUL.md
- MEMORY.md
- AGENTS.md
- HEARTBEAT.md
- TOOLS.md

## How to Enable

### Option 1: Cron (Recommended)
```bash
crontab -e

# Add this line:
0 * * * * /Users/thekhemist/.openclaw/workspace/scripts/auto-backup.sh >> /Users/thekhemist/.openclaw/workspace/.auto-backups/backup.log 2>&1
```

### Option 2: Run Manually
```bash
/Users/thekhemist/.openclaw/workspace/scripts/auto-backup.sh
```

## Recovery
If reset happens again:
```bash
# Check reflog for auto-backup commits
git reflog | grep "Auto-backup"

# Restore from a specific backup
git show <commit>:IDENTITY.md > IDENTITY.md
```

## File Backups
Also creates timestamped copies in `.auto-backups/` folder (24 hour retention)
