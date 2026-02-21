"""
Khem Direct CLOB Execution Module

Sub-second execution via direct Polymarket CLOB API.
No Bankr latency. No browser automation. Pure speed.

Requirements:
- POLYGON_WALLET_PRIVATE_KEY in environment
- USDC deposited on Polygon
- CLOB API key auto-derived from wallet
"""

import os
import time
from decimal import Decimal
from typing import Optional, Dict, Any
from dotenv import load_dotenv

from py_clob_client.client import ClobClient
from py_clob_client.clob_types import OrderArgs, MarketOrderArgs, OrderType
from py_clob_client.constants import POLYGON

from khem_arb.polymarket import GammaArbClient, ArbMarket

load_dotenv()


class KhemCLOBTrader:
    """
    Direct CLOB execution for sub-second arbitrage.
    
    Performance targets:
- Resolution to execution: <5 seconds
    - Order placement to confirmation: <2 seconds
    - Total latency: <10 seconds (vs Bankr 60-120s)
    """
    
    def __init__(self):
        self.private_key = os.getenv("POLYGON_WALLET_PRIVATE_KEY")
        if not self.private_key:
            raise ValueError("POLYGON_WALLET_PRIVATE_KEY not set in environment")
        
        self.clob_url = "https://clob.polymarket.com"
        self.chain_id = POLYGON
        
        # Initialize CLOB client
        self.client = ClobClient(
            host=self.clob_url,
            key=self.private_key,
            chain_id=self.chain_id
        )
        
        # Create or derive API credentials
        self._init_api_creds()
        
        # Gamma client for market data
        self.gamma = GammaArbClient()
        
        print("✅ KhemCLOBTrader initialized")
        print(f"   Wallet: {self.get_wallet_address()}")
    
    def _init_api_creds(self):
        """Initialize CLOB API credentials."""
        try:
            creds = self.client.create_or_derive_api_creds()
            self.client.set_api_creds(creds)
            print("   CLOB API: Authenticated")
        except Exception as e:
            print(f"   CLOB API Warning: {e}")
    
    def get_wallet_address(self) -> str:
        """Get wallet address from private key."""
        from eth_account import Account
        return Account.from_key(self.private_key).address
    
    def get_orderbook(self, token_id: str) -> Dict[str, Any]:
        """Get orderbook for a token."""
        return self.client.get_order_book(token_id)
    
    def get_price(self, token_id: str) -> float:
        """Get current mid price for a token."""
        return float(self.client.get_price(token_id))
    
    def execute_limit_order(
        self,
        token_id: str,
        side: str,  # BUY or SELL
        price: float,
        size: float
    ) -> Dict[str, Any]:
        """
        Execute a limit order.
        
        Args:
            token_id: CLOB token ID
            side: BUY or SELL
            price: Limit price (0.01 to 0.99)
            size: Position size in shares
        
        Returns:
            Order response from CLOB
        """
        order_args = OrderArgs(
            price=price,
            size=size,
            side=side,
            token_id=token_id
        )
        
        # Create and sign order
        signed_order = self.client.create_order(order_args)
        
        # Submit order
        response = self.client.post_order(signed_order, OrderType.GTC)
        
        return response
    
    def execute_market_order(
        self,
        token_id: str,
        size: float
    ) -> Dict[str, Any]:
        """
        Execute a market order (fill immediately at best available price).
        
        Args:
            token_id: CLOB token ID
            size: Position size in shares
        
        Returns:
            Order response from CLOB
        """
        order_args = MarketOrderArgs(
            token_id=token_id,
            amount=size
        )
        
        # Create market order
        signed_order = self.client.create_market_order(order_args)
        
        # Submit with FOK (Fill or Kill)
        response = self.client.post_order(signed_order, OrderType.FOK)
        
        return response
    
    def execute_arbitrage_trade(
        self,
        market: ArbMarket,
        winning_outcome: str,  # "UP" or "DOWN"
        max_entry_price: float = 0.90,
        position_size: float = 100.0  # USDC
    ) -> Optional[Dict[str, Any]]:
        """
        Execute information arbitrage trade.
        
        Strategy:
        1. Confirm winning outcome from resolution source
        2. Check if market price < max_entry_price on winning side
        3. Execute immediately if spread exists
        4. Hold until settlement at $1.00
        
        Args:
            market: ArbMarket object with token IDs
            winning_outcome: "UP" or "DOWN"
            max_entry_price: Maximum price to pay (default 0.90 for 10% edge)
            position_size: USDC to invest
        
        Returns:
            Trade execution result or None if no trade executed
        """
        start_time = time.time()
        
        # Get token ID for winning outcome
        if winning_outcome.upper() == "UP":
            token_id = market.clobTokenIds[0] if len(market.clobTokenIds) > 0 else None
        else:
            token_id = market.clobTokenIds[1] if len(market.clobTokenIds) > 1 else None
        
        if not token_id:
            print(f"❌ No token ID for {winning_outcome}")
            return None
        
        # Check current price
        current_price = self.get_price(token_id)
        print(f"📊 {market.slug} | {winning_outcome} | Price: ${current_price:.2f}")
        
        # Check if arbitrage opportunity exists
        if current_price >= max_entry_price:
            print(f"⏸️  No spread. Price ${current_price:.2f} >= max ${max_entry_price:.2f}")
            return None
        
        # Calculate position size (shares = USDC / price)
        shares = position_size / current_price
        
        print(f"🎯 ARBITRAGE DETECTED!")
        print(f"   Entry: ${current_price:.2f}")
        print(f"   Exit: $1.00")
        print(f"   Edge: {(1.0 - current_price) * 100:.1f}%")
        print(f"   Shares: {shares:.2f}")
        print(f"   Position: ${position_size:.2f}")
        
        # Execute market order for speed
        print(f"🚀 Executing market order...")
        try:
            result = self.execute_market_order(token_id, shares)
            execution_time = time.time() - start_time
            
            print(f"✅ TRADE EXECUTED in {execution_time:.2f}s")
            print(f"   Order ID: {result.get('orderID', 'N/A')}")
            
            return {
                "market": market.slug,
                "outcome": winning_outcome,
                "entry_price": current_price,
                "shares": shares,
                "position_size": position_size,
                "execution_time": execution_time,
                "result": result
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ TRADE FAILED after {execution_time:.2f}s: {e}")
            return None
    
    def get_balance(self) -> Dict[str, float]:
        """Get USDC balance."""
        from web3 import Web3
        
        # USDC contract on Polygon
        usdc_address = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
        
        # Minimal ERC20 ABI for balanceOf
        abi = [{
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function"
        }]
        
        w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
        contract = w3.eth.contract(address=usdc_address, abi=abi)
        
        address = self.get_wallet_address()
        balance = contract.functions.balanceOf(address).call()
        
        return {
            "usdc": balance / 1e6,  # USDC has 6 decimals
            "address": address
        }


# Test function
def test_clob_connection():
    """Test CLOB connection without private key."""
    print("🧪 Testing CLOB connection...")
    
    # Test public endpoints
    client = ClobClient("https://clob.polymarket.com")
    
    # Try to get markets
    try:
        markets = client.get_markets()
        print(f"✅ CLOB API reachable. Markets: {len(markets.get('data', []))}")
        return True
    except Exception as e:
        print(f"❌ CLOB API error: {e}")
        return False


if __name__ == "__main__":
    # Test connection
    test_clob_connection()
    
    # If private key is set, test full integration
    if os.getenv("POLYGON_WALLET_PRIVATE_KEY"):
        print("\n🔑 Private key detected. Testing full integration...")
        try:
            trader = KhemCLOBTrader()
            
            # Check balance
            balance = trader.get_balance()
            print(f"\n💰 Balance: {balance['usdc']:.2f} USDC")
            
        except Exception as e:
            print(f"❌ Integration test failed: {e}")
    else:
        print("\n⏸️  POLYGON_WALLET_PRIVATE_KEY not set. Skipping full test.")
        print("   Set the env var to test live trading.")
