#!/usr/bin/env python3
"""
Qwen Worker - Safe File Organizer
Organizes files with significance scoring
NEVER deletes without explicit high-confidence classification
"""

import os
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path

# Add workspace to path
WORKSPACE = Path("/Users/thekhemist/.openclaw/workspace")
sys.path.insert(0, str(WORKSPACE))

import importlib.util
spec = importlib.util.spec_from_file_location("significance_scorer", str(WORKSPACE / "agents" / "qwen-worker" / "utils" / "significance_scorer.py"))
significance_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(significance_module)
scorer = significance_module.scorer

def safe_file_organizer():
    """Organize files with safety checks"""
    
    print(f"[{datetime.now()}] Qwen Worker: Safe File Organizer Starting...")
    
    # Directories to organize
    target_dirs = [
        WORKSPACE / "memory" / "daily",
        WORKSPACE / "memory" / "qwen-worker" / "heartbeat-reports",
        WORKSPACE / "memory" / "qwen-worker" / "data-reports",
    ]
    
    actions_taken = []
    
    for target_dir in target_dirs:
        if not target_dir.exists():
            continue
        
        print(f"\n  Scanning {target_dir}...")
        
        # Get all files older than 7 days
        cutoff = datetime.now() - timedelta(days=7)
        
        for filepath in target_dir.iterdir():
            if not filepath.is_file():
                continue
            
            # Check age
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
            if mtime > cutoff:
                continue  # Too recent
            
            # Score the file
            action, score, reason = scorer.classify_for_cleanup(filepath)
            
            action_record = {
                'filepath': str(filepath),
                'action': action,
                'score': score,
                'reason': reason,
                'age_days': (datetime.now() - mtime).days
            }
            
            # Take action based on classification
            if action == 'PROTECT':
                # Never touch - flag for Khem review
                action_record['taken'] = 'FLAGGED_FOR_REVIEW'
                print(f"    ⚠️  PROTECT: {filepath.name} (Score: {score:.1f})")
                
            elif action == 'ARCHIVE':
                # Move to archive, don't delete
                archive_dir = WORKSPACE / "memory" / "archive" / target_dir.name
                archive_dir.mkdir(parents=True, exist_ok=True)
                
                dest = archive_dir / filepath.name
                shutil.move(str(filepath), str(dest))
                action_record['taken'] = f'ARCHIVED_TO {dest}'
                print(f"    📦 ARCHIVED: {filepath.name} → {dest}")
                
            elif action == 'REVIEW':
                # Flag for manual review, don't delete
                action_record['taken'] = 'FLAGGED_FOR_REVIEW'
                print(f"    🔍 REVIEW: {filepath.name} (Score: {score:.1f})")
                
            elif action == 'SAFE_DELETE':
                # Only safe deletes - Qwen reports, temp files
                if 'qwen-worker' in str(filepath) and ('heartbeat' in str(filepath) or 'price-data' in str(filepath)):
                    # Double check: is this a qwen-generated report?
                    try:
                        content = filepath.read_text()
                        if 'Qwen Worker Report' in content:
                            os.remove(filepath)
                            action_record['taken'] = 'DELETED'
                            print(f"    🗑️  DELETED: {filepath.name}")
                        else:
                            action_record['taken'] = 'SKIPPED_NOT_QWEN_REPORT'
                            print(f"    ⏭️  SKIPPED: {filepath.name} (Not Qwen report)")
                    except:
                        action_record['taken'] = 'ERROR_READING'
                        print(f"    ❌ ERROR: {filepath.name}")
                else:
                    action_record['taken'] = 'SKIPPED_NOT_QWEN_FILE'
                    print(f"    ⏭️  SKIPPED: {filepath.name} (Not Qwen file)")
            
            actions_taken.append(action_record)
    
    # Generate report
    report = generate_organizer_report(actions_taken)
    
    # Save report
    report_dir = WORKSPACE / "memory" / "qwen-worker" / "organization-reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    report_file = report_dir / f"file-organization-{timestamp}.md"
    report_file.write_text(report)
    
    print(f"\n[{datetime.now()}] Report saved: {report_file}")
    
    # Summary
    protected = sum(1 for a in actions_taken if a['action'] == 'PROTECT')
    archived = sum(1 for a in actions_taken if 'ARCHIVED' in str(a.get('taken', '')))
    deleted = sum(1 for a in actions_taken if a.get('taken') == 'DELETED')
    flagged = sum(1 for a in actions_taken if 'FLAGGED' in str(a.get('taken', '')))
    
    print(f"\n=== ORGANIZATION SUMMARY ===")
    print(f"Protected: {protected}")
    print(f"Archived: {archived}")
    print(f"Flagged for review: {flagged}")
    print(f"Deleted: {deleted}")
    print("============================\n")
    
    return report_file

def generate_organizer_report(actions):
    """Generate organization report"""
    
    report = f"""# Qwen Worker Report - File Organization
**Task:** Safe File Organizer  
**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** ✅ Complete

## Actions Taken
| File | Action | Score | Age (days) | Result |
|------|--------|-------|------------|--------|
"""
    
    for action in actions:
        filename = Path(action['filepath']).name[:40]
        report += f"| {filename} | {action['action']} | {action['score']:.1f} | {action['age_days']} | {action.get('taken', 'UNKNOWN')} |\n"
    
    # Summary stats
    protected = sum(1 for a in actions if a['action'] == 'PROTECT')
    archived = sum(1 for a in actions if 'ARCHIVED' in str(a.get('taken', '')))
    deleted = sum(1 for a in actions if a.get('taken') == 'DELETED')
    flagged = sum(1 for a in actions if 'FLAGGED' in str(a.get('taken', '')))
    
    report += f"""
## Summary
- **Protected (PROTECT):** {protected} files flagged for Khem review
- **Archived (ARCHIVE):** {archived} files moved to archive
- **Flagged for Review (REVIEW):** {flagged} files need manual decision
- **Deleted (SAFE_DELETE):** {deleted} Qwen reports safely removed

## Safety Rules Applied
1. ✅ Only delete files with score < 20
2. ✅ Only delete confirmed Qwen-generated reports
3. ✅ Archive (don't delete) medium-significance files
4. ✅ Never touch PROTECT-classified files
5. ✅ Flag everything else for Khem review

## Files Requiring Khem Review
"""
    
    for action in actions:
        if 'FLAGGED' in str(action.get('taken', '')):
            report += f"- {action['filepath']} (Score: {action['score']:.1f})\n"
    
    report += """
## Next Steps
- [ ] Khem to review flagged files
- [ ] Decide on PROTECT-classified items
- [ ] Confirm archived files are accessible
- [ ] Adjust scoring thresholds if needed

---
*Safe cleanup with significance scoring*
*No important files deleted without explicit classification*
"""
    
    return report

def main():
    """Main entry point"""
    return safe_file_organizer()

if __name__ == "__main__":
    main()
