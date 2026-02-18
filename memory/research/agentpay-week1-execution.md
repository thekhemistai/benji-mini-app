# AGENTPAY: Week 1 Execution Plan

**Goal:** MVP smart contract deployed to Base Sepolia  
**Start:** 2026-02-17  
**End:** 2026-02-24

---

## Day 1 (Today): Smart Contract Architecture

### Morning: Design
- [ ] Finalize contract structure (AgentPayRouter, AgentPayStreams, AgentPayEscrow)
- [ ] Define events and errors
- [ ] Security considerations (reentrancy, overflow)

### Afternoon: Setup
- [ ] Initialize Hardhat project
- [ ] Configure for Base Sepolia
- [ ] Set up testing framework

**Deliverable:** Contract skeleton + test suite scaffold

---

## Day 2: Core Router Contract

### Tasks
- [ ] Write AgentPayRouter.sol
  - routePayment() function
  - Fee calculation (0.5%)
  - Token approval handling
  - Event emission
- [ ] Write comprehensive tests
  - Happy path
  - Edge cases
  - Fee accuracy

**Deliverable:** Working router contract + passing tests

---

## Day 3: Subscription Streams

### Tasks
- [ ] Write AgentPayStreams.sol
  - createStream()
  - cancelStream()
  - withdrawFromStream()
  - Stream status tracking
- [ ] Tests for stream lifecycle
- [ ] Gas optimization

**Deliverable:** Stream contract + tests

---

## Day 4: Escrow System

### Tasks
- [ ] Write AgentPayEscrow.sol
  - createEscrow()
  - releaseEscrow()
  - refundEscrow()
  - Arbiter integration
- [ ] Tests for all scenarios
- [ ] Dispute resolution logic

**Deliverable:** Escrow contract + tests

---

## Day 5: Integration & Polish

### Tasks
- [ ] Integration tests (all 3 contracts)
- [ ] Gas optimization pass
- [ ] Security review (checklist)
- [ ] Documentation (NatSpec comments)

**Deliverable:** Complete test suite, ready for audit

---

## Day 6: Deployment Prep

### Tasks
- [ ] Deploy to Base Sepolia
- [ ] Verify contracts on Basescan
- [ ] Create deployment scripts
- [ ] Record contract addresses

**Deliverable:** Live contracts on testnet

---

## Day 7: SDK & Demo

### Tasks
- [ ] Build simple Python SDK (read-only)
- [ ] Create demo script
- [ ] Test real transactions on Sepolia
- [ ] Document usage

**Deliverable:** Working demo + SDK v0.1

---

## Resources Needed

| Resource | Status | Action |
|----------|--------|--------|
| Base Sepolia ETH | Need | Get from faucet |
| Basescan API key | Need | Create account |
| OpenZeppelin libs | Have | Install via npm |
| Hardhat | Have | Already installed |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Scope creep | Strict daily deliverables |
| Security issues | Checklist + tests, audit later |
| Base Sepolia issues | Backup: Local fork testing |
| Gas costs too high | Optimize after working version |

---

## Success Criteria

By end of Week 1:
- [ ] 3 smart contracts deployed to Base Sepolia
- [ ] All tests passing
- [ ] Basic SDK functional
- [ ] Demo video recorded
- [ ] Documentation complete

---

## Daily Standup Template

```
Yesterday: [What I completed]
Today: [What I'm working on]
Blockers: [What's in my way]
```

---

## Tools & Commands

### Initialize Project
```bash
mkdir agentpay-contracts
cd agentpay-contracts
npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npx hardhat init
```

### Compile
```bash
npx hardhat compile
```

### Test
```bash
npx hardhat test
```

### Deploy to Sepolia
```bash
npx hardhat run scripts/deploy.js --network baseSepolia
```

---

## Contract Addresses (To Fill)

| Contract | Base Sepolia | Base Mainnet |
|----------|--------------|--------------|
| AgentPayRouter | TBD | TBD |
| AgentPayStreams | TBD | TBD |
| AgentPayEscrow | TBD | TBD |

---

## Notes

**Philosophy:** Ship fast, iterate faster. Perfect is the enemy of working.

**Scope:** This is MVP. Advanced features (flash loans, batching, etc.) come later.

**Testing:** Assume users will try to break it. Test accordingly.

---

*Ready to build.*
