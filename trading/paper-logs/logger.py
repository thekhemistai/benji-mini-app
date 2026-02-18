#!/usr/bin/env python3
"""
Paper Trading Logger
Track BTC Polymarket strategy performance
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

class PaperTradingLogger:
    def __init__(self):
        self.log_dir = Path.home() / '.openclaw/workspace/trading/paper-logs'
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.summary_file = self.log_dir / 'summary.json'
        self.daily_dir = self.log_dir / 'daily'
        self.daily_dir.mkdir(exist_ok=True)
        
    def log_trade(self, trade_data):
        """Log a paper trade"""
        trade = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'market': trade_data.get('market'),
            'direction': trade_data.get('direction'),  # UP or DOWN
            'entry_price': trade_data.get('entry_price'),
            'position_size': trade_data.get('position_size', 1.0),
            'confidence': trade_data.get('confidence'),
            'rsi': trade_data.get('rsi'),
            'macd': trade_data.get('macd'),
            'reasoning': trade_data.get('reasoning'),
            'status': 'open'
        }
        
        # Save to daily log
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        daily_file = self.daily_dir / f'{today}.jsonl'
        
        with open(daily_file, 'a') as f:
            f.write(json.dumps(trade) + '\n')
        
        print(f"✅ Trade logged: {trade['direction']} on {trade['market']}")
        return trade
    
    def close_trade(self, market, exit_price, result):
        """Close an open trade"""
        # Find and update the trade
        today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
        daily_file = self.daily_dir / f'{today}.jsonl'
        
        if not daily_file.exists():
            return None
        
        # Read all trades
        trades = []
        with open(daily_file, 'r') as f:
            for line in f:
                trade = json.loads(line.strip())
                if trade.get('market') == market and trade.get('status') == 'open':
                    trade['status'] = 'closed'
                    trade['exit_price'] = exit_price
                    trade['result'] = result  # 'win' or 'loss'
                    trade['pnl'] = self.calculate_pnl(trade, exit_price)
                    trade['closed_at'] = datetime.now(timezone.utc).isoformat()
                trades.append(trade)
        
        # Rewrite file
        with open(daily_file, 'w') as f:
            for trade in trades:
                f.write(json.dumps(trade) + '\n')
        
        self.update_summary()
        return result
    
    def calculate_pnl(self, trade, exit_price):
        """Calculate PnL for a trade"""
        entry = trade.get('entry_price', 0.5)
        size = trade.get('position_size', 1.0)
        
        if trade.get('direction') == 'UP':
            return (exit_price - entry) * size
        else:
            return (entry - exit_price) * size
    
    def update_summary(self):
        """Update running summary stats"""
        all_trades = []
        
        # Load all daily logs
        for daily_file in self.daily_dir.glob('*.jsonl'):
            with open(daily_file, 'r') as f:
                for line in f:
                    trade = json.loads(line.strip())
                    all_trades.append(trade)
        
        # Calculate stats
        closed_trades = [t for t in all_trades if t.get('status') == 'closed']
        wins = len([t for t in closed_trades if t.get('result') == 'win'])
        losses = len([t for t in closed_trades if t.get('result') == 'loss'])
        
        total_pnl = sum(t.get('pnl', 0) for t in closed_trades)
        
        win_trades = [t for t in closed_trades if t.get('result') == 'win']
        loss_trades = [t for t in closed_trades if t.get('result') == 'loss']
        
        avg_win = sum(t.get('pnl', 0) for t in win_trades) / len(win_trades) if win_trades else 0
        avg_loss = sum(t.get('pnl', 0) for t in loss_trades) / len(loss_trades) if loss_trades else 0
        
        summary = {
            'last_updated': datetime.now(timezone.utc).isoformat(),
            'total_trades': len(all_trades),
            'closed_trades': len(closed_trades),
            'open_trades': len(all_trades) - len(closed_trades),
            'wins': wins,
            'losses': losses,
            'win_rate': (wins / len(closed_trades) * 100) if closed_trades else 0,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else 0
        }
        
        with open(self.summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        return summary
    
    def get_summary(self):
        """Get current summary"""
        if self.summary_file.exists():
            with open(self.summary_file, 'r') as f:
                return json.load(f)
        return self.update_summary()
    
    def print_report(self):
        """Print formatted report"""
        summary = self.get_summary()
        
        print("🧪 PAPER TRADING REPORT")
        print("=" * 50)
        print(f"Last Updated: {summary['last_updated'][:19]}")
        print("")
        print(f"Total Trades: {summary['total_trades']}")
        print(f"  ✅ Wins: {summary['wins']}")
        print(f"  ❌ Losses: {summary['losses']}")
        print(f"  ⏳ Open: {summary['open_trades']}")
        print("")
        print(f"Win Rate: {summary['win_rate']:.1f}%")
        print(f"Total PnL: ${summary['total_pnl']:.2f}")
        print(f"Avg Win: ${summary['avg_win']:.2f}")
        print(f"Avg Loss: ${summary['avg_loss']:.2f}")
        print(f"Profit Factor: {summary['profit_factor']:.2f}")
        print("=" * 50)

if __name__ == '__main__':
    logger = PaperTradingLogger()
    logger.print_report()
