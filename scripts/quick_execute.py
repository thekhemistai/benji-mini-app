#!/usr/bin/env python3
"""
Quick Execution Script for Polymarket Arbitrage
One command: position, refresh, execute
"""

import asyncio
import sys
import argparse
from datetime import datetime

# Import the bridge
from polymarket_ui_bridge import quick_execute


def main():
    parser = argparse.ArgumentParser(
        description='Quick execute Polymarket trade via browser automation'
    )
    parser.add_argument('market_slug', help='Market slug (e.g., btc-updown-15m-1771580100)')
    parser.add_argument('side', choices=['up', 'down'], help='Side to buy')
    parser.add_argument('--size', type=float, default=10.0, help='Position size in USD (default: 10)')
    
    args = parser.parse_args()
    
    # Run the execution
    asyncio.run(quick_execute(args.market_slug, args.side, args.size))


if __name__ == "__main__":
    main()
