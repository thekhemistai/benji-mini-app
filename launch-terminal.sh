#!/bin/bash
# Launch Polymarket Trading Terminal

echo "🧪 Khem Trading Terminal"
echo "========================"
echo ""
echo "This terminal shows:"
echo "  • Real-time BTC price"
echo "  • RSI (14) indicator"
echo "  • MACD indicator"
echo "  • Polymarket odds"
echo "  • Edge calculation"
echo ""
echo "Press Ctrl+C to exit"
echo ""

cd ~/.openclaw/workspace/agents/signal-hunter
python3 terminal_dashboard.py
