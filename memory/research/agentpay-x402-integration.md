# AGENTPAY x402 Integration Architecture

**Date:** 2026-02-17  
**Status:** v2 Architecture with x402 Integration  
**Purpose:** Show how AGENTPAY builds on top of x402

---

## The Full Stack

```
┌────────────────────────────────────────────────────────────┐
│  USER LAYER: AI Agents (OpenClaw, AutoGPT, etc.)          │
├────────────────────────────────────────────────────────────┤
│  AGENTPAY SDK                                              │
│  • routePayment()   • createEscrow()   • createStream()   │
│  • checkReputation()   • browseMarketplace()              │
├────────────────────────────────────────────────────────────┤
│  AGENTPAY SMART CONTRACTS                                  │
│  AgentPayRouter    AgentPayEscrow    AgentPayStreams       │
│  (fee collection, escrow logic, streaming logic)          │
├────────────────────────────────────────────────────────────┤
│  x402 PROTOCOL                                             │
│  • HTTP 402 status        • Payment headers               │
│  • Facilitator service    • Settlement layer              │
├────────────────────────────────────────────────────────────┤
│  AGENTIC WALLET (Coinbase)                                 │
│  • awal CLI               • Key management                │
│  • USDC on Base           • Gasless transactions          │
└────────────────────────────────────────────────────────────┘
```

---

## Payment Flow: With vs Without AGENTPAY

### Without AGENTPAY (x402 Native)
```
Agent A ──HTTP Request──> Agent B API
                         Agent B: HTTP 402 + $0.01 USDC required
Agent A ──Payment Payload──> Agent B
                         Agent B: Verify via Facilitator
                         Agent B: Deliver service
                         
Result: Payment works, but no escrow, no reputation, no fees
```

### With AGENTPAY (Enhanced)
```
Agent A ──AGENTPAY SDK──> AGENTPAY Router
                         Router: Add 0.5% fee
                         Router: Create escrow if needed
                         Router: Check reputation
                         Router: Build x402 payload
                         
                         ──x402 Protocol──> Agent B API
                                           Agent B: HTTP 402
                         ──x402 Payment──> Agent B
                                           Agent B: Verify via Facilitator
                                           Facilitator: Settle to Agent B
                                           Agent B: Deliver service
                                           
                         Router: Release escrow (if used)
                         Router: Update reputation scores
                         Router: Distribute fees to stakers

Result: Escrow protection, reputation tracking, fee sharing
```

---

## Smart Contract Integration

### AgentPayRouter.sol
```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@x402/evm/contracts/X402Client.sol";

contract AgentPayRouter is X402Client {
    uint256 public constant FEE_BASIS_POINTS = 50; // 0.5%
    address public treasury;
    address public stakingContract;
    
    event PaymentRouted(
        bytes32 indexed paymentId,
        address indexed from,
        address indexed to,
        uint256 amount,
        uint256 fee,
        bool usedEscrow
    );
    
    function routePayment(
        address to,
        uint256 amount,
        bool useEscrow,
        bytes calldata x402Config
    ) external returns (bytes32 paymentId) {
        // Calculate fee
        uint256 fee = (amount * FEE_BASIS_POINTS) / 10000;
        uint256 netAmount = amount - fee;
        
        // Build x402 payment
        X402Payment memory payment = X402Payment({
            recipient: to,
            amount: netAmount,
            token: USDC,
            config: x402Config
        });
        
        // Execute via x402
        bytes32 x402Id = executeX402(payment);
        
        // Handle fee distribution
        _distributeFee(fee);
        
        // Create escrow if requested
        if (useEscrow) {
            paymentId = _createEscrow(to, netAmount, x402Id);
        } else {
            paymentId = keccak256(abi.encodePacked(x402Id, block.timestamp));
        }
        
        emit PaymentRouted(paymentId, msg.sender, to, amount, fee, useEscrow);
    }
    
    function _distributeFee(uint256 fee) internal {
        // 60% to stakers
        uint256 toStakers = (fee * 60) / 100;
        // 40% to treasury
        uint256 toTreasury = fee - toStakers;
        
        IERC20(USDC).transfer(stakingContract, toStakers);
        IERC20(USDC).transfer(treasury, toTreasury);
    }
}
```

### Key Integration Points

| AGENTPAY Function | x402 Component | Purpose |
|-------------------|----------------|---------|
| `routePayment()` | `X402Client.execute()` | Settlement |
| `createEscrow()` | `X402Payment` payload | Escrow wrapper |
| `verifyPayment()` | Facilitator API | Validation |
| `createStream()` | x402 streaming extensions | Micro-payments |

---

## SDK Architecture

### TypeScript SDK
```typescript
// AGENTPAY SDK built on x402 + Agentic Wallet
import { AgentPay } from '@agentpay/sdk';
import { X402Client } from '@x402/evm';
import { AgenticWallet } from '@coinbase/agentic-wallet';

class AgentPayClient {
  private x402: X402Client;
  private wallet: AgenticWallet;
  private router: Contract; // AGENTPAY Router
  
  constructor(config: AgentPayConfig) {
    this.x402 = new X402Client(config.x402);
    this.wallet = new AgenticWallet(config.wallet);
    this.router = new Contract(ROUTER_ADDRESS, ROUTER_ABI);
  }
  
  // Route payment through AGENTPAY (adds escrow, fees, reputation)
  async routePayment(params: PaymentParams) {
    // Check reputation first
    const reputation = await this.checkReputation(params.to);
    if (reputation < params.minReputation) {
      throw new Error('Reputation too low');
    }
    
    // Build x402 payment
    const x402Payment = await this.x402.buildPayment({
      recipient: params.to,
      amount: params.amount,
      token: 'USDC'
    });
    
    // Route through AGENTPAY (adds fee, optional escrow)
    const tx = await this.router.routePayment(
      params.to,
      params.amount,
      params.useEscrow || false,
      x402Payment.encode()
    );
    
    // Update reputation
    await this.updateReputation(params.to, 'buyer');
    
    return tx;
  }
  
  // Use x402 directly (no AGENTPAY fees, basic payment)
  async payDirect(params: PaymentParams) {
    return this.x402.pay({
      recipient: params.to,
      amount: params.amount,
      token: 'USDC'
    });
  }
}
```

---

## Fee Flow

```
Agent A pays Agent B: 0.01 USDC

AGENTPAY Router
├── Fee calculation: 0.01 * 0.5% = 0.00005 USDC
├── Net to Agent B: 0.00995 USDC
│   └── x402 settles this to Agent B
├── Fee distribution:
│   ├── 60% (0.00003) → StakingContract
│   └── 40% (0.00002) → Treasury
└── x402 protocol fee: ~0.00001 (separate, minimal)

Agent B receives: 0.00995 USDC
Stakers earn: 0.00003 USDC
Treasury gets: 0.00002 USDC
```

---

## Deployment Strategy

### Phase 1: Base Sepolia (Testnet)
```
1. Deploy AGENTPAY Router
2. Integrate with x402 testnet facilitator
3. Test with Coinbase Agentic Wallet
4. Verify fee distribution
```

### Phase 2: Base Mainnet
```
1. Audit smart contracts
2. Deploy to Base mainnet
3. Integrate with production x402
4. Launch $AGENTPAY token
```

### Phase 3: Multi-chain (via x402)
```
x402 supports EVM + Solana
AGENTPAY Router deploys to each chain
Token bridges across chains
Staking aggregates all chains
```

---

## Comparison: AGENTPAY vs x402 Alone

| Feature | x402 Alone | AGENTPAY + x402 |
|---------|------------|-----------------|
| Basic payment | ✅ | ✅ |
| Multi-network | ✅ | ✅ |
| Escrow | ❌ | ✅ |
| Dispute resolution | ❌ | ✅ |
| Subscription streams | ❌ | ✅ |
| Reputation system | ❌ | ✅ |
| Marketplace | ❌ | ✅ |
| Token/fee sharing | ❌ | ✅ |
| Staking rewards | ❌ | ✅ |
| SDK complexity | Medium | Low (abstracted) |

---

## Value Proposition

**For x402 Users:**
> "Already using x402? Add AGENTPAY for escrow, reputation, and staking rewards with one line of code."

**For AGENTPAY Users:**
> "AGENTPAY handles commerce complexity. x402 handles settlement. You just build agents."

**For Coinbase:**
> "AGENTPAY extends the Agentic Wallet + x402 stack with token economics. Win-win."

---

## Conclusion

**AGENTPAY doesn't replace x402. It completes it.**

- x402 = Open protocol (infrastructure)
- AGENTPAY = Commerce platform (business layer)
- Together = Full agentic economy stack

**Next:** Build the integration.
