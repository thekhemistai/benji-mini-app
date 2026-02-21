"""
Khem Polymarket Arbitrage Toolkit

Lightweight, fast toolkit for information arbitrage on Polymarket.
Adapted from Polymarket's official agents framework — stripped of 
LLM prediction layers that add latency.

Key modules:
- polypymarket: Gamma API client, market models, opportunity detection
"""

__version__ = "0.1.0"

from .polymarket import (
    GammaArbClient,
    ArbMarket,
    ArbEvent,
    ArbOpportunity,
)

__all__ = [
    "GammaArbClient",
    "ArbMarket", 
    "ArbEvent",
    "ArbOpportunity",
]
