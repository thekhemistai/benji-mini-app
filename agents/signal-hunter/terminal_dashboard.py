#!/usr/bin/env python3
"""
Polymarket Trading Terminal v1.0
Real-time BTC price, Polymarket odds, technical indicators, edge calculator.
Safe. Auditable. Ours.
"""

import json
import time
import subprocess
import re
import requests
from datetime import datetime, timezone
from collections import deque
from typing import Optional, Dict, List

# Try to import rich for pretty terminal UI
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not installed. Install with: pip install rich")

class TradingTerminal:
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.price_history = deque(maxlen=100)  # Last 100 prices for indicators
        self.last_update = None
        self.btc_price = None
        self.polymarket_odds = None
        self.rsi = None
        self.macd = None
        self.signal = None
        
    def get_btc_price(self) -> Optional[float]:
        """Fetch current BTC price from Coinbase."""
        try:
            resp = requests.get(
                "https://api.coinbase.com/v2/exchange-rates?currency=BTC",
                timeout=5
            )
            resp.raise_for_status()
            price = float(resp.json()["data"]["rates"]["USD"])
            self.price_history.append({
                "timestamp": datetime.now(timezone.utc),
                "price": price
            })
            self.btc_price = price
            self.last_update = datetime.now(timezone.utc)
            return price
        except Exception as e:
            return None
    
    def calculate_rsi(self, period: int = 14) -> Optional[float]:
        """Calculate RSI from price history using Wilder's smoothing."""
        if len(self.price_history) < period + 1:
            return None
        
        prices = [p["price"] for p in list(self.price_history)]
        if len(prices) < period + 1:
            return None
        
        # Calculate price changes
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Get last 'period' deltas
        deltas = deltas[-period:]
        
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [abs(d) if d < 0 else 0 for d in deltas]
        
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        # Clamp to valid range
        return max(0.0, min(100.0, rsi))
    
    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Optional[Dict]:
        """Calculate MACD from price history."""
        min_required = slow + signal
        if len(self.price_history) < min_required:
            return None
        
        prices = [p["price"] for p in list(self.price_history)]
        
        # Calculate EMAs using proper formula
        def ema(data, period):
            if len(data) < period:
                return None
            multiplier = 2 / (period + 1)
            # Start with SMA for first EMA value
            sma = sum(data[:period]) / period
            ema_val = sma
            # Calculate subsequent EMAs
            for price in data[period:]:
                ema_val = (price - ema_val) * multiplier + ema_val
            return ema_val
        
        ema_fast = ema(prices, fast)
        ema_slow = ema(prices, slow)
        
        if ema_fast is None or ema_slow is None:
            return None
        
        macd_line = ema_fast - ema_slow
        
        # For signal line, we need MACD history
        # Simplified: calculate signal as EMA of recent price changes
        changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        if len(changes) >= signal:
            signal_ema = ema([0] + changes, signal)  # Pad with 0 to match length
        else:
            signal_ema = 0
        
        histogram = macd_line - signal_ema
        
        return {
            "macd": macd_line,
            "signal": signal_ema,
            "histogram": histogram
        }
    
    def get_polymarket_odds(self) -> Optional[Dict]:
        """Fetch Polymarket odds via Bankr CLI."""
        try:
            result = subprocess.run(
                ["bankr", "show me the bitcoin up or down market"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                return None
            
            output = result.stdout
            # Parse various formats
            up_match = re.search(r'Up[:\s]+\$?([\d.]+)[¢%]?', output)
            down_match = re.search(r'Down[:\s]+\$?([\d.]+)[¢%]?', output)
            
            if up_match and down_match:
                up_val = float(up_match.group(1))
                down_val = float(down_match.group(1))
                # Normalize to probabilities
                if up_val > 1:  # Cents format
                    up_prob = up_val / 100
                    down_prob = down_val / 100
                else:  # Already probability
                    up_prob = up_val
                    down_prob = down_val
                
                return {
                    "up": up_prob,
                    "down": down_prob,
                    "raw": output[:200]  # First 200 chars for debug
                }
            
            return None
        except Exception as e:
            return None
    
    def calculate_edge(self) -> Optional[Dict]:
        """Calculate trading edge based on indicators."""
        if not all([self.btc_price, self.rsi, self.macd, self.polymarket_odds]):
            return None
        
        # Determine directional bias from indicators
        macd_bias = "UP" if self.macd["histogram"] > 0 else "DOWN"
        rsi_bias = "UP" if self.rsi > 50 else "DOWN"
        
        # Combined signal strength
        if macd_bias == rsi_bias:
            confidence = abs(self.macd["histogram"]) / 100 + abs(self.rsi - 50) / 50
            direction = macd_bias
        else:
            confidence = 0.3  # Mixed signals
            direction = macd_bias  # MACD usually leads
        
        # Calculate edge vs Polymarket
        current_odds = self.polymarket_odds["up"] if direction == "UP" else self.polymarket_odds["down"]
        fair_odds = 0.5 + (confidence * 0.2)  # Max 20% edge from indicators
        edge = fair_odds - current_odds if direction == "UP" else current_odds - fair_odds
        
        return {
            "direction": direction,
            "confidence": confidence,
            "current_odds": current_odds,
            "fair_odds": fair_odds,
            "edge": edge,
            "recommendation": "TRADE" if edge > 0.05 else "SKIP"
        }
    
    def generate_display(self) -> str:
        """Generate terminal display."""
        if not RICH_AVAILABLE:
            return self._generate_simple_display()
        
        # Rich UI
        layout = Layout()
        
        # Header
        header = Panel(
            Text("Polymarket Trading Terminal v1.0", style="bold cyan") +
            Text(f"\nLast Update: {self.last_update.strftime('%H:%M:%S') if self.last_update else 'N/A'} UTC", style="dim"),
            title="🧪 Khem Trading System",
            border_style="cyan"
        )
        
        # Price Panel
        price_text = Text()
        if self.btc_price:
            price_text.append(f"BTC Price: ", style="bold")
            price_text.append(f"${self.btc_price:,.2f}", style="green bold" if self.price_history and len(self.price_history) > 1 and self.btc_price > list(self.price_history)[-2]["price"] else "red bold")
        else:
            price_text.append("BTC Price: Loading...", style="yellow")
        
        price_panel = Panel(price_text, title="📊 Price", border_style="blue")
        
        # Indicators Panel
        ind_table = Table(show_header=False, box=None)
        ind_table.add_column("Indicator", style="cyan")
        ind_table.add_column("Value", style="white")
        ind_table.add_column("Signal", style="bold")
        
        if self.rsi:
            rsi_color = "green" if self.rsi > 50 else "red"
            rsi_signal = "BULLISH" if self.rsi > 50 else "BEARISH"
            ind_table.add_row("RSI (14)", f"{self.rsi:.1f}", f"[{rsi_color}]{rsi_signal}[/{rsi_color}]")
        else:
            ind_table.add_row("RSI (14)", "Calculating...", "[yellow]WAIT[/yellow]")
        
        if self.macd:
            macd_color = "green" if self.macd["histogram"] > 0 else "red"
            macd_signal = "BULLISH" if self.macd["histogram"] > 0 else "BEARISH"
            ind_table.add_row("MACD", f"{self.macd['histogram']:+.4f}", f"[{macd_color}]{macd_signal}[/{macd_color}]")
        else:
            ind_table.add_row("MACD", "Calculating...", "[yellow]WAIT[/yellow]")
        
        ind_panel = Panel(ind_table, title="📈 Indicators", border_style="yellow")
        
        # Polymarket Panel
        poly_text = Text()
        if self.polymarket_odds:
            poly_text.append("Bitcoin Up/Down Market\n\n", style="bold")
            poly_text.append(f"UP:   {self.polymarket_odds['up']:.1%}\n", style="green" if self.polymarket_odds['up'] > 0.5 else "white")
            poly_text.append(f"DOWN: {self.polymarket_odds['down']:.1%}\n", style="red" if self.polymarket_odds['down'] > 0.5 else "white")
        else:
            poly_text.append("Loading Polymarket data...", style="yellow")
        
        poly_panel = Panel(poly_text, title="🎯 Polymarket", border_style="magenta")
        
        # Edge Panel
        edge_table = Table(show_header=False, box=None)
        edge_table.add_column("Metric", style="cyan")
        edge_table.add_column("Value", style="white")
        
        if self.signal:
            edge_color = "green" if self.signal['recommendation'] == "TRADE" else "red"
            edge_table.add_row("Direction", f"{self.signal['direction']}")
            edge_table.add_row("Confidence", f"{self.signal['confidence']:.2%}")
            edge_table.add_row("Current Odds", f"{self.signal['current_odds']:.1%}")
            edge_table.add_row("Fair Odds", f"{self.signal['fair_odds']:.1%}")
            edge_table.add_row("Edge", f"{self.signal['edge']:+.1%}")
            edge_table.add_row("Action", f"[{edge_color} bold]{self.signal['recommendation']}[/{edge_color} bold]")
        else:
            edge_table.add_row("Status", "[yellow]Waiting for data...[/yellow]")
        
        edge_panel = Panel(edge_table, title="⚡ Edge Calculator", border_style="green")
        
        # Layout
        layout.split_column(
            Layout(header, size=5),
            Layout(name="main")
        )
        layout["main"].split_row(
            Layout(price_panel, name="left"),
            Layout(name="right")
        )
        layout["right"].split_column(
            Layout(ind_panel, name="indicators"),
            Layout(poly_panel, name="polymarket"),
            Layout(edge_panel, name="edge")
        )
        
        return layout
    
    def _generate_simple_display(self) -> str:
        """Simple text display for non-rich terminals."""
        lines = [
            "="*60,
            "Polymarket Trading Terminal v1.0",
            "="*60,
            "",
            f"BTC Price: ${self.btc_price:,.2f}" if self.btc_price else "BTC Price: Loading...",
            "",
            "Indicators:",
            f"  RSI: {self.rsi:.1f}" if self.rsi else "  RSI: Calculating...",
            f"  MACD: {self.macd['histogram']:+.4f}" if self.macd else "  MACD: Calculating...",
            "",
            "Polymarket Odds:" if self.polymarket_odds else "Polymarket: Loading...",
        ]
        
        if self.polymarket_odds:
            lines.append(f"  UP: {self.polymarket_odds['up']:.1%}")
            lines.append(f"  DOWN: {self.polymarket_odds['down']:.1%}")
        
        if self.signal:
            lines.append("")
            lines.append("Edge Analysis:")
            lines.append(f"  Direction: {self.signal['direction']}")
            lines.append(f"  Edge: {self.signal['edge']:+.1%}")
            lines.append(f"  Action: {self.signal['recommendation']}")
        
        lines.append("")
        lines.append(f"Last Update: {self.last_update.strftime('%H:%M:%S') if self.last_update else 'N/A'} UTC")
        lines.append("="*60)
        
        return "\n".join(lines)
    
    def update(self):
        """Update all data sources."""
        self.get_btc_price()
        self.rsi = self.calculate_rsi()
        self.macd = self.calculate_macd()
        self.polymarket_odds = self.get_polymarket_odds()
        self.signal = self.calculate_edge()
    
    def run(self):
        """Main loop."""
        if RICH_AVAILABLE:
            with Live(self.generate_display(), refresh_per_second=1) as live:
                while True:
                    self.update()
                    live.update(self.generate_display())
                    time.sleep(5)  # Update every 5 seconds
        else:
            while True:
                self.update()
                print(self.generate_display())
                time.sleep(5)

def main():
    print("Starting Polymarket Trading Terminal...")
    print("Install 'rich' for better UI: pip install rich")
    print("")
    
    terminal = TradingTerminal()
    
    # Initial data collection for indicators
    print("Collecting initial price data...")
    for i in range(30):  # Collect 30 prices (2.5 minutes)
        terminal.get_btc_price()
        time.sleep(5)
        print(f"Collected {i+1}/30 price points...", end="\r")
    
    print("\nStarting live terminal...")
    print("Press Ctrl+C to exit")
    print("")
    
    try:
        terminal.run()
    except KeyboardInterrupt:
        print("\n\nShutting down...")

if __name__ == "__main__":
    main()
