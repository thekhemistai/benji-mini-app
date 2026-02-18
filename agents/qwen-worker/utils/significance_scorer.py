#!/usr/bin/env python3
"""
Significance Scoring System
Measures "weight" or importance of files/tasks/data
Prevents accidental deletion of valuable content
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

WORKSPACE = Path("/Users/thekhemist/.openclaw/workspace")

class SignificanceScorer:
    """Scores files and tasks by importance"""
    
    # Weight factors (0-100 scale)
    FACTORS = {
        'creator_attention': 30,    # Did creator spend time on this?
        'cross_references': 20,     # How many other files reference this?
        'financial_value': 25,      # Does this generate or save money?
        'strategic_importance': 15, # Is this core to mission?
        'uniqueness': 10,          # Can this be recreated easily?
    }
    
    def __init__(self):
        self.scores = {}
        
    def score_file(self, filepath: Path) -> Dict:
        """Calculate significance score for a file"""
        if not filepath.exists():
            return {'score': 0, 'reason': 'File not found'}
        
        scores = {}
        
        # Factor 1: Creator attention (lines, edit recency)
        try:
            content = filepath.read_text()
            lines = len(content.split('\n'))
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
            age_days = (datetime.now() - mtime).days
            
            # More lines = more attention
            # Recent edits = more relevant
            scores['creator_attention'] = min(100, (lines / 10) + max(0, 30 - age_days))
        except:
            scores['creator_attention'] = 0
        
        # Factor 2: Cross-references
        ref_count = self._count_references(filepath.name)
        scores['cross_references'] = min(100, ref_count * 20)
        
        # Factor 3: Financial value
        scores['financial_value'] = self._estimate_financial_value(filepath, content if 'content' in locals() else "")
        
        # Factor 4: Strategic importance
        scores['strategic_importance'] = self._estimate_strategic_value(filepath)
        
        # Factor 5: Uniqueness (can it be regenerated?)
        scores['uniqueness'] = self._estimate_uniqueness(filepath, content if 'content' in locals() else "")
        
        # Calculate weighted total
        total = 0
        for factor, weight in self.FACTORS.items():
            total += scores.get(factor, 0) * (weight / 100)
        
        scores['total'] = round(total, 1)
        scores['filepath'] = str(filepath)
        scores['size_bytes'] = filepath.stat().st_size if filepath.exists() else 0
        
        return scores
    
    def _count_references(self, filename: str) -> int:
        """Count how many files reference this filename"""
        count = 0
        for root, dirs, files in os.walk(WORKSPACE):
            # Skip node_modules and .git
            dirs[:] = [d for d in dirs if d not in ['node_modules', '.git', '.next']]
            
            for file in files:
                if file.endswith(('.md', '.txt', '.json', '.js', '.ts', '.py')):
                    try:
                        filepath = Path(root) / file
                        if filepath.stat().st_size < 1_000_000:  # Skip huge files
                            content = filepath.read_text()
                            if filename in content:
                                count += 1
                    except:
                        continue
        return count
    
    def _estimate_financial_value(self, filepath: Path, content: str) -> float:
        """Estimate financial significance (0-100)"""
        score = 0
        
        # Keywords indicating financial value
        financial_keywords = [
            'revenue', 'profit', 'cost', 'pricing', '$', 'tokenomics',
            'trading', 'portfolio', 'investment', 'budget', 'fee',
            'AGENTPAY', 'gumroad', 'fiverr', 'income', 'savings'
        ]
        
        content_lower = content.lower()
        for keyword in financial_keywords:
            if keyword in content_lower:
                score += 10
        
        # Location-based scoring
        path_str = str(filepath).lower()
        if 'trading' in path_str or 'portfolio' in path_str:
            score += 20
        if 'research' in path_str and 'agentpay' in path_str:
            score += 30
        if 'active-tasks' in path_str:
            score += 25
        
        return min(100, score)
    
    def _estimate_strategic_value(self, filepath: Path) -> float:
        """Estimate strategic importance (0-100)"""
        score = 0
        path_str = str(filepath).lower()
        
        # Core system files
        if path_str.endswith(('soul.md', 'agents.md', 'identity.md', 'user.md')):
            score += 80
        
        # Architecture docs
        if 'architecture' in path_str or 'master-plan' in path_str:
            score += 70
        
        # Daily logs (recent = more important)
        if 'daily' in path_str:
            try:
                # Extract date from filename
                date_str = filepath.stem
                file_date = datetime.strptime(date_str, '%Y-%m-%d')
                days_old = (datetime.now() - file_date).days
                score += max(0, 50 - days_old)  # Decay over time
            except:
                score += 10
        
        # Memory files
        if 'memory' in path_str:
            score += 20
        
        # Qwen worker reports (low strategic value, high operational)
        if 'qwen-worker' in path_str:
            score += 5
        
        return min(100, score)
    
    def _estimate_uniqueness(self, filepath: Path, content: str) -> float:
        """Estimate how unique/irreplaceable this content is (0-100)"""
        score = 100  # Assume unique
        
        # Can be regenerated?
        if 'report' in str(filepath).lower() and 'qwen' in str(filepath).lower():
            score = 10  # Qwen reports are regenerated
        
        if 'heartbeat' in str(filepath).lower():
            score = 5  # Heartbeat reports are temporary
        
        if 'price-data' in str(filepath).lower():
            score = 15  # Price data can be fetched again
        
        # Original creative work?
        if 'research' in str(filepath).lower() and 'master-plan' in str(filepath).lower():
            score = 95  # Original thinking
        
        if 'soul.md' in str(filepath).lower():
            score = 100  # Irreplaceable
        
        return score
    
    def classify_for_cleanup(self, filepath: Path) -> Tuple[str, float, str]:
        """
        Classify file for cleanup decision
        Returns: (action, score, reason)
        """
        scores = self.score_file(filepath)
        total_score = scores.get('total', 0)
        
        # Classification thresholds
        if total_score >= 70:
            return ('PROTECT', total_score, 'High significance - manual review required')
        elif total_score >= 40:
            return ('ARCHIVE', total_score, 'Medium significance - archive, do not delete')
        elif total_score >= 20:
            return ('REVIEW', total_score, 'Low significance - review before deletion')
        else:
            return ('SAFE_DELETE', total_score, 'Very low significance - safe to delete')
    
    def scan_directory(self, directory: Path, pattern: str = "*") -> List[Dict]:
        """Scan directory and score all matching files"""
        results = []
        
        for filepath in directory.glob(pattern):
            if filepath.is_file():
                scores = self.score_file(filepath)
                action, total, reason = self.classify_for_cleanup(filepath)
                scores['action'] = action
                scores['action_reason'] = reason
                results.append(scores)
        
        # Sort by score descending
        results.sort(key=lambda x: x.get('total', 0), reverse=True)
        return results
    
    def generate_report(self, directory: Path, pattern: str = "*") -> str:
        """Generate cleanup report with significance scores"""
        results = self.scan_directory(directory, pattern)
        
        report = f"""# Significance Scoring Report
**Directory:** {directory}  
**Pattern:** {pattern}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
| Action | Count |
|--------|-------|
| PROTECT | {sum(1 for r in results if r['action'] == 'PROTECT')} |
| ARCHIVE | {sum(1 for r in results if r['action'] == 'ARCHIVE')} |
| REVIEW | {sum(1 for r in results if r['action'] == 'REVIEW')} |
| SAFE_DELETE | {sum(1 for r in results if r['action'] == 'SAFE_DELETE')} |

## Detailed Scores
| File | Total | Action | Creator | Cross-Ref | Financial | Strategic | Unique |
|------|-------|--------|---------|-----------|-----------|-----------|--------|
"""
        
        for r in results[:50]:  # Top 50
            filename = Path(r['filepath']).name[:30]
            report += f"| {filename} | {r['total']:.1f} | {r['action']} | {r.get('creator_attention', 0):.0f} | {r.get('cross_references', 0):.0f} | {r.get('financial_value', 0):.0f} | {r.get('strategic_importance', 0):.0f} | {r.get('uniqueness', 0):.0f} |\n"
        
        report += f"""
## Cleanup Recommendations

### PROTECT (Manual Review Required)
"""
        for r in results:
            if r['action'] == 'PROTECT':
                report += f"- **{Path(r['filepath']).name}** (Score: {r['total']:.1f})\n"
        
        report += "\n### ARCHIVE (Move to Archive, Keep)\n"
        for r in results:
            if r['action'] == 'ARCHIVE':
                report += f"- {Path(r['filepath']).name} (Score: {r['total']:.1f})\n"
        
        report += "\n### SAFE_DELETE (Low Risk)\n"
        for r in results:
            if r['action'] == 'SAFE_DELETE':
                report += f"- {Path(r['filepath']).name} (Score: {r['total']:.1f})\n"
        
        report += """
---
*Scoring factors: Creator attention (30%), Cross-references (20%), Financial value (25%), Strategic importance (15%), Uniqueness (10%)*
"""
        
        return report

# Global instance
scorer = SignificanceScorer()

if __name__ == "__main__":
    # Test
    import sys
    
    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1])
    else:
        target_dir = WORKSPACE / "memory" / "daily"
    
    print(f"Scanning {target_dir}...")
    report = scorer.generate_report(target_dir)
    
    output_file = WORKSPACE / "memory" / "qwen-worker" / "organization-reports" / f"significance-scan-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(report)
    
    print(f"Report saved: {output_file}")
    print(report[:2000])  # Preview
