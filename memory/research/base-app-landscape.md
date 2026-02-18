# Base Chain App Landscape — Competitive Research

**Date:** 2026-02-17  
**Purpose:** Identify existing Base apps to avoid duplication, find gaps

---

## What I Can See

### Base Official Tools
| App | Type | Smart Contracts? | Notes |
|-----|------|------------------|-------|
| **Base Account** | Wallet/Identity | Yes (passkey auth) | Universal account system |
| **OnchainKit** | Developer toolkit | No | React components for builders |
| **Mini Apps** | App platform | Yes | Publish apps to Base app |
| **x402** | Payment protocol | Yes | HTTP 402 payments |
| **Agentic Wallet** | Agent wallet | Yes | CLI + skills for agents |

### Major DeFi on Base
| App | Category | TVL/Usage | Contracts? |
|-----|----------|-----------|------------|
| **Aerodrome** | DEX/AMM | Top Base DEX | Yes (Solidity) |
| **Uniswap** | DEX | Multi-chain | Yes (V3 pools) |
| **Compound** | Lending | On Base | Yes |
| **Aave** | Lending | On Base | Yes |
| **Morpho** | Lending | Growing | Yes |
| **BaseSwap** | DEX | Base native | Yes |
| **Beefy** | Yield vaults | Multi-chain | Yes |

### NFT/Consumer Apps
| App | Category | Notes |
|-----|----------|-------|
| **Zora** | NFT minting | Creator tools |
| **ThirdWeb** | NFT infra | Contracts + SDK |
| **Highlight** | NFT minting | Creator economy |
| **Paragraph** | Publishing | Mirror competitor |
| **BENJI** | Memecoin | Your community |
| **Farcaster** | Social | On-chain social graph |

### Infrastructure
| App | Category | Notes |
|-----|----------|-------|
| **Alchemy** | RPC/Indexing | Base support |
| **QuickNode** | RPC | Base support |
| **The Graph** | Indexing | Subgraphs on Base |
| **Chainlink** | Oracles | Price feeds |
| **Pimlico** | Account abstraction | Smart wallets |
| **Coinbase Verifications** | Identity | On-chain attestations |

### What I CAN'T See Well
- Specific agent-focused apps
- Logging/audit trail apps
- Reputation systems
- Insurance products
- Most Mini Apps (new, not well indexed)

---

## Gaps I Found (Opportunities)

### ✅ NO Direct Competitors Found For:

| Our Product | Status | Evidence |
|-------------|--------|----------|
| **AGENTLOG** | ✅ Clear path | No agent audit trail apps found |
| **AGENTSIGN** | ✅ Clear path | No agent reputation registry |
| **AGENTHOST** | ⚠️ Some overlap | Mini Apps platform similar but different focus |
| **AGENTPAY** | ⚠️ Partial | x402 exists but no token/fee layer on top |
| **AGENTGUARD** | ✅ Clear path | No agent insurance products |
| **AGENTAPI** | ⚠️ Partial | Alchemy/QuickNode do RPC, not unified API |
| **AGENTMARKET** | ⚠️ Unknown | Mini Apps store but not agent-specific |

### 🔍 Needs Deeper Research:

1. **Base Mini Apps directory** — What apps exist?
2. **Farcaster Frames on Base** — Any agent tools?
3. **Coinbase agentic-wallet-skills repo** — What skills already exist?

---

## Competitive Analysis: Our Products

### AGENTLOG vs Existing
**Existing:**
- The Graph (indexing, but not agent-specific)
- Custom logging (everyone builds their own)

**AGENTLOG advantage:**
- Purpose-built for agents
- Insurance-ready proof
- SDK for easy integration
- Revenue model (per-log fees)

### AGENTSIGN vs Existing
**Existing:**
- Coinbase Verifications (human identity, not agents)
- ENS (names, not reputation)

**AGENTSIGN advantage:**
- Agent-specific reputation
- Transaction history scoring
- Cross-platform verification
- Stake-based trust

### AGENTPAY vs x402
**x402:**
- Payment protocol (open standard)
- No token
- No escrow/reputation

**AGENTPAY advantage:**
- Token economics ($AGENTPAY)
- Escrow/dispute resolution
- Reputation integration
- Fee sharing with stakers

---

## Recommendations

### Immediate Actions:
1. **Install awal CLI** — Test Coinbase's agentic wallet
2. **Get Neynar API key** — Monitor Farcaster/Base for competitors
3. **Browse Base Mini Apps** — See what's being built

### Build Priority (Updated):
1. **AGENTLOG** — ✅ No direct competitors found
2. **AGENTSIGN** — ✅ No direct competitors found  
3. **AGENTPAY** — ⚠️ Build on x402, not against it
4. **AGENTHOST** — ⚠️ Differentiate from Mini Apps

### Validation Needed:
- [ ] Full Mini Apps directory
- [ ] Farcaster agent ecosystem
- [ ] Existing agent logging solutions
- [ ] Insurance products for Web3

---

## Next Steps

1. **Install awal** and test Agentic Wallet
2. **Get Neynar key** and monitor /base channel
3. **Apply for Base builder grants** — $5K-25K funding
4. **Start AGENTLOG build** — Clear competitive path

---

*Research limited by web access. Need manual verification of Mini Apps ecosystem.*
