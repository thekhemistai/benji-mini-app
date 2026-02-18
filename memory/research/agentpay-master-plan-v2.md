# AGENTPAY: Stripe for AI Agents (Built on x402)

**Vision:** The commerce layer for the agentic economy  
**Built On:** x402 (Coinbase's open payment protocol)  
**Chain:** Base (primary), multi-chain via x402  
**Token:** $AGENTPAY (governance + fee sharing)

---

## The Stack

```
┌─────────────────────────────────────────────┐
│           AGENTPAY Commerce Layer           │
│  • Escrow • Streams • Reputation • Token   │
├─────────────────────────────────────────────┤
│         x402 Protocol (Settlement)          │
│  • HTTP 402 payments • Facilitator • USDC   │
├─────────────────────────────────────────────┤
│      Agentic Wallet (Coinbase)              │
│  • awal CLI • Key management • Gasless txs  │
└─────────────────────────────────────────────┘
```

**Analogy:**
- Agentic Wallet = Bank account (holds funds)
- x402 = Visa network (moves funds)
- AGENTPAY = Stripe (commerce platform on top)

---

## Why x402 + AGENTPAY?

### x402 Provides:
- ✅ Open payment protocol (HTTP 402)
- ✅ Multi-network (EVM + Solana)
- ✅ Facilitator service (verification)
- ✅ No token (pure infrastructure)

### x402 Does NOT Provide:
- ❌ Token economics
- ❌ Escrow/dispute resolution
- ❌ Subscription streams
- ❌ Agent reputation
- ❌ Marketplace discovery
- ❌ Staking rewards

### AGENTPAY Adds:
- ✅ $AGENTPAY token (fee sharing)
- ✅ Smart contract escrow
- ✅ Payment streams
- ✅ On-chain reputation
- ✅ Service marketplace
- ✅ 0.5% fees → stakers

---

## How It Works

### Basic Payment (x402 native)
```
Agent A requests service from Agent B
Agent B responds: HTTP 402 + payment requirements
Agent A pays via x402 (USDC)
Agent B delivers service
```
**Fee:** Protocol level (~0.1%)

### AGENTPAY Enhanced Payment
```
Agent A wants to pay Agent B with escrow
Agent A calls AGENTPAY.createEscrow(
  recipient: AgentB,
  amount: 0.01 ETH,
  arbiter: AgentC
)
AGENTPAY routes via x402 for settlement
Service delivered → escrow released
Dispute → arbiter resolves
```
**Fee:** 0.5% (60% to stakers, 40% treasury)

---

## Product Suite

### 1. AGENTPAY Core (Payment Router)
**Built on:** x402 + Smart contracts  
**What:** Route payments with fee collection

```solidity
// Route through AGENTPAY (adds escrow, reputation, fees)
AGENTPAY.routePayment({
  to: agentB,
  amount: 0.01 ETH,
  useEscrow: true,
  arbiter: agentC,
  metadata: { service: "research" }
});

// Settlement happens via x402
// Fee: 0.5%
```

### 2. AGENTPAY Streams (Subscriptions)
**Built on:** x402 streaming extensions  
**What:** Continuous payments

```solidity
// Pay 0.001 ETH/hour for compute
AGENTPAY.createStream({
  recipient: computeProvider,
  ratePerSecond: 0.000000277, // 0.001/hour
  token: USDC
});

// x402 handles micro-transactions
// AGENTPAY adds reputation tracking
```

### 3. AGENTPAY Escrow
**Built on:** Smart contracts + x402 settlement  
**What:** Dispute resolution

```solidity
// Create escrow
escrowId = AGENTPAY.createEscrow({
  seller: agentB,
  arbiter: agentC,
  amount: 0.01 ETH,
  deadline: 7 days
});

// x402 settles payments
// AGENTPAY manages dispute logic
```

### 4. AGENTPAY Identity (Reputation)
**Built on:** On-chain history + x402 transactions  
**What:** Trust layer

- Transaction history from x402
- Success rates tracked by AGENTPAY
- Skill verification via staking
- Cross-references from marketplace

### 5. AGENTPAY Marketplace
**Built on:** x402 Bazaar + AGENTPAY discovery  
**What:** Service discovery

- Browse x402-enabled services
- AGENTPAY adds ratings, reviews
- One-click payment via AGENTPAY SDK
- Revenue share with service providers

---

## Integration with Coinbase Stack

### Using Agentic Wallet Skills
```bash
# Install Coinbase skills
npx skills add coinbase/agentic-wallet-skills

# Agent can now:
# - authenticate-wallet (email OTP)
# - fund (Coinbase onramp)
# - send-usdc (transfers)
# - trade (swaps)
# - search-for-service (x402 bazaar)
# - pay-for-service (x402 payments)
```

### AGENTPAY SDK Enhancement
```javascript
// On top of agentic-wallet-skills
import { AgentPay } from '@agentpay/sdk';

const agent = new AgentPay({
  wallet: agenticWallet,  // From Coinbase skills
  x402: x402Client,       // From x402 SDK
  staking: true           // Earn fees
});

// Enhanced payment with escrow
await agent.payWithEscrow({
  service: 'market-research',
  amount: '0.01',
  requireReputation: 4.5  // Minimum rating
});
```

---

## Revenue Model

### Fee Structure
- **Base x402:** ~0.1% protocol fee (to facilitator)
- **AGENTPAY:** 0.5% commerce fee (to stakers)
- **Total:** ~0.6% per transaction

### Revenue Distribution
```
0.5% AGENTPAY fee
├── 60% (0.3%) → $AGENTPAY stakers
├── 30% (0.15%) → Protocol treasury
└── 10% (0.05%) → Development fund
```

### Projections
| Year | Agents | Daily Volume | AGENTPAY Fees | Staker Rewards |
|------|--------|--------------|---------------|----------------|
| 1 | 5,000 | $500K | $910K | $546K |
| 2 | 25,000 | $5M | $9M | $5.4M |
| 3 | 100,000 | $30M | $55M | $33M |

---

## Tokenomics

**$AGENTPAY Token:**
- **Supply:** 1B fixed
- **Use:** Stake to earn fees, govern protocol

**Distribution:**
- 40% Liquidity + Community
- 25% Team (4-year vest)
- 20% Treasury
- 15% Early adopters + Airdrop

**Staking Benefits:**
- Earn 60% of AGENTPAY fees
- Vote on protocol upgrades
- Reduced fees for stakers
- Priority access to new features

---

## Technical Architecture

### Smart Contracts (Base)
```solidity
// AGENTPAY Router (uses x402 for settlement)
contract AgentPayRouter {
    function routePayment(
        address to,
        uint256 amount,
        bool useEscrow,
        bytes calldata x402Payload
    ) external returns (bytes32 paymentId);
}

// Escrow (settles via x402)
contract AgentPayEscrow {
    function createEscrow(
        address seller,
        uint256 amount,
        uint256 deadline,
        bytes calldata x402Requirements
    ) external returns (uint256 escrowId);
    
    function releaseEscrow(uint256 escrowId) external;
    function resolveDispute(uint256 escrowId, address winner) external;
}
```

### Backend Services
| Service | Tech | Integration |
|---------|------|-------------|
| API Gateway | Node.js | x402 SDK + AGENTPAY SDK |
| Indexer | The Graph | x402 events + AGENTPAY events |
| Facilitator | Coinbase | x402 settlement |
| Reputation | PostgreSQL | On-chain history aggregation |

---

## Go-to-Market Strategy

### Phase 1: Bootstrap (Months 1-3)
**Goal:** 100 agents using AGENTPAY

**Tactics:**
1. **Dogfooding:** Use AGENTPAY for our own agent ecosystem
2. **Airdrop:** $AGENTPAY to x402 early adopters
3. **Integration:** Partner with OpenClaw agents
4. **Documentation:** "AGENTPAY on x402" guide

### Phase 2: Growth (Months 4-12)
**Goal:** 5,000 agents

**Tactics:**
1. **Coinbase Partnership:** Integrate with agentic-wallet-skills
2. **x402 Bazaar:** List AGENTPAY-enabled services
3. **Hackathons:** Sponsor AI agent + DeFi events
4. **Grants:** $100K for AGENTPAY developers

### Phase 3: Scale (Year 2+)
**Goal:** 100,000+ agents

**Tactics:**
1. **Multi-chain:** Expand via x402 (Solana, other EVMs)
2. **Enterprise:** White-label for AI platforms
3. **Institutional:** Custody for agent treasuries

---

## Competitive Advantage

| Competitor | Weakness | Our Advantage |
|------------|----------|---------------|
| **x402 alone** | No token, no escrow, no reputation | AGENTPAY adds commerce layer |
| **Agentic Wallet** | Just custody + basic send | AGENTPAY adds commerce platform |
| **Stripe** | No crypto, no agent focus | Crypto-native, built on x402 |
| **Request Network** | Complex, no agent identity | AGENTPAY + x402 + reputation |

**Moat:** Network effects on top of open standards. More agents → More transactions → More fees → More stakers → More security → More agents.

---

## Risks & Mitigation

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| x402 adoption slow | Medium | Build alongside x402, contribute to standard |
| Coinbase competes | Low | They want open standards, we add token layer |
| Smart contract bugs | High | Audits, bug bounties, gradual rollout |
| Multi-chain complexity | Medium | x402 handles this, we focus on commerce |

---

## Immediate Next Steps

### Week 1: x402 Integration
- [ ] Study x402 TypeScript SDK
- [ ] Write AGENTPAY-x402 adapter
- [ ] Test basic payment flow
- [ ] Deploy to Base Sepolia

### Week 2: Smart Contracts
- [ ] AgentPayRouter (x402 integration)
- [ ] AgentPayEscrow
- [ ] AgentPayStreams
- [ ] Tests + documentation

### Week 3: SDK
- [ ] TypeScript SDK
- [ ] Python SDK
- [ ] Integration with agentic-wallet-skills

### Week 4: Launch Prep
- [ ] Audit (if budget)
- [ ] Documentation
- [ ] Base mainnet deployment
- [ ] Airdrop to early users

---

## The Pitch

**To Agent Developers:**
> "x402 handles payments. AGENTPAY handles commerce. Add 3 lines of code for escrow, reputation, and staking rewards."

**To Token Holders:**
> "Every agent transaction on x402 can route through AGENTPAY. Fees go to stakers. Capture the agentic economy."

**To Us:**
> "We don't compete with Coinbase. We build on their open standards. x402 is the railroad, AGENTPAY is the business built alongside it."

---

## Conclusion

AGENTPAY isn't competing with x402 or Agentic Wallet. It's **completing the stack**.

**The full stack:**
1. Agentic Wallet = Hold funds
2. x402 = Move funds
3. AGENTPAY = Commerce platform (token, escrow, reputation)

**We're in the perfect position:**
- We ARE an agent (dogfooding)
- We understand x402 deeply
- We add what the open protocol intentionally leaves out
- Base is the right chain

**Let's build the Stripe for AI agents on top of x402.**

---

*Document created: 2026-02-17*  
*Next: x402 integration + Week 1 sprint*
