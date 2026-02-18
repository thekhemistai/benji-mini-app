#!/bin/bash
# Auto-backup script for Khem's critical files
# Runs every hour via cron
# Protects against git reset --hard disasters

WORKSPACE="/Users/thekhemist/.openclaw/workspace"
BACKUP_DIR="$WORKSPACE/.auto-backups"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)

# Files to backup (space-separated)
CRITICAL_FILES="IDENTITY.md USER.md SOUL.md MEMORY.md AGENTS.md HEARTBEAT.md TOOLS.md"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Git backup (if in repo)
cd "$WORKSPACE" || exit 1

# Check if there are uncommitted changes to critical files
NEED_COMMIT=0
for file in $CRITICAL_FILES; do
    if [ -f "$file" ]; then
        if ! git diff --quiet HEAD -- "$file" 2>/dev/null || ! git ls-files --error-unmatch "$file" > /dev/null 2>&1; then
            NEED_COMMIT=1
            break
        fi
    fi
done

if [ $NEED_COMMIT -eq 1 ]; then
    git add -f $CRITICAL_FILES 2>/dev/null
    git commit -m "Auto-backup: $TIMESTAMP" --no-verify 2>/dev/null || true
    echo "[$TIMESTAMP] Auto-committed critical files"
fi

# Also make timestamped file copies
mkdir -p "$BACKUP_DIR/$TIMESTAMP"
for file in $CRITICAL_FILES; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/$TIMESTAMP/"
    fi
done

# Keep only last 24 backups (24 hours)
ls -1t "$BACKUP_DIR" | tail -n +25 | xargs -I {} rm -rf "$BACKUP_DIR/{}" 2>/dev/null || true

echo "[$TIMESTAMP] Backup complete. Critical files: $(echo $CRITICAL_FILES | wc -w)"
