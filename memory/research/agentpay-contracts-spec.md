# AGENTPAY Smart Contracts

**Status:** Day 1 - Architecture & Router Contract
**Network:** Base Sepolia (eventually mainnet)
**Solidity Version:** ^0.8.19

---

## Architecture Overview

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  AgentPayRouter │────▶│  AgentPayStreams │────▶│ AgentPayEscrow  │
│  (Payments)     │     │  (Subscriptions) │     │ (Disputes)      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                          ┌───────▼────────┐
                          │  $AGENTPAY     │
                          │  Token/Staking │
                          └────────────────┘
```

---

## Contract 1: AgentPayRouter

**Purpose:** Route payments between agents with fee collection

### State Variables

```solidity
// Fee configuration
uint256 public constant FEE_BASIS_POINTS = 50; // 0.5%
uint256 public constant FEE_DENOMINATOR = 10000;

// Treasury and staking addresses
address public treasury;
address public stakingContract;

// Supported tokens (ETH + ERC20s)
mapping(address => bool) public supportedTokens;

// Agent registration (optional metadata)
mapping(address => AgentProfile) public agentProfiles;

struct AgentProfile {
    string name;
    string metadataURI;
    uint256 registeredAt;
    bool isVerified;
}
```

### Events

```solidity
event PaymentRouted(
    address indexed from,
    address indexed to,
    address token,
    uint256 amount,
    uint256 fee,
    bytes32 indexed paymentId,
    bytes metadata
);

event AgentRegistered(
    address indexed agent,
    string name,
    uint256 registeredAt
);

event TokenSupportUpdated(address token, bool supported);
```

### Core Functions

```solidity
/// @notice Route a payment from one agent to another
/// @param to Recipient address
/// @param token Token address (address(0) for ETH)
/// @param amount Amount to send
/// @param metadata Optional payment metadata
/// @return paymentId Unique identifier for this payment
function routePayment(
    address to,
    address token,
    uint256 amount,
    bytes calldata metadata
) external payable returns (bytes32 paymentId);

/// @notice Batch multiple payments (gas efficient)
/// @param payments Array of payment instructions
function routeBatchPayment(
    PaymentInstruction[] calldata payments
) external payable;

/// @notice Register agent profile
/// @param name Agent name
/// @param metadataURI IPFS or other URI for agent metadata
function registerAgent(
    string calldata name,
    string calldata metadataURI
) external;

/// @notice Calculate fee for a given amount
/// @param amount Payment amount
/// @return fee Calculated fee
function calculateFee(uint256 amount) external pure returns (uint256 fee);
```

### Fee Distribution

```solidity
function _distributeFee(uint256 fee) internal {
    // 60% to stakers
    uint256 toStakers = (fee * 60) / 100;
    // 40% to treasury
    uint256 toTreasury = fee - toStakers;
    
    // Transfer to staking contract
    payable(stakingContract).transfer(toStakers);
    // Transfer to treasury
    payable(treasury).transfer(toTreasury);
}
```

---

## Contract 2: AgentPayStreams

**Purpose:** Continuous payment streams between agents

### State Variables

```solidity
struct Stream {
    address sender;
    address recipient;
    address token;
    uint256 ratePerSecond;
    uint256 startTime;
    uint256 stopTime;
    uint256 remainingBalance;
    bool isActive;
}

mapping(uint256 => Stream) public streams;
uint256 public nextStreamId;

// Agent auto-approval settings
mapping(address => mapping(address => AutoApproval)) public autoApprovals;

struct AutoApproval {
    uint256 maxAmount;
    uint256 timeWindow;
    uint256 spentInWindow;
    uint256 windowStart;
    bool isActive;
}
```

### Events

```solidity
event StreamCreated(
    uint256 indexed streamId,
    address indexed sender,
    address indexed recipient,
    address token,
    uint256 ratePerSecond
);

event StreamCancelled(
    uint256 indexed streamId,
    uint256 remainingBalance
);

event Withdrawal(
    uint256 indexed streamId,
    address indexed recipient,
    uint256 amount
);
```

### Core Functions

```solidity
/// @notice Create a continuous payment stream
/// @param recipient Who receives the stream
/// @param token Token address (address(0) for ETH)
/// @param ratePerSecond Amount streamed per second
/// @param duration How long the stream lasts (0 for indefinite)
/// @return streamId Unique stream identifier
function createStream(
    address recipient,
    address token,
    uint256 ratePerSecond,
    uint256 duration
) external payable returns (uint256 streamId);

/// @notice Cancel an active stream
/// @param streamId Stream to cancel
/// @return remainingBalance Amount returned to sender
function cancelStream(uint256 streamId) external returns (uint256 remainingBalance);

/// @notice Withdraw accumulated funds from stream
/// @param streamId Stream to withdraw from
function withdrawFromStream(uint256 streamId) external;

/// @notice Get withdrawable amount for a stream
/// @param streamId Stream to check
/// @return amount Current withdrawable balance
function getWithdrawableAmount(uint256 streamId) external view returns (uint256 amount);

/// @notice Set auto-approval for incoming streams
/// @param token Token to auto-approve
/// @param maxAmount Maximum amount to auto-approve
/// @param timeWindow Time window for limit
function setAutoApproval(
    address token,
    uint256 maxAmount,
    uint256 timeWindow
) external;
```

---

## Contract 3: AgentPayEscrow

**Purpose:** Dispute resolution for agent transactions

### State Variables

```solidity
enum EscrowStatus { Pending, Released, Refunded, Disputed }

struct Escrow {
    address buyer;
    address seller;
    address arbiter;
    address token;
    uint256 amount;
    uint256 deadline;
    EscrowStatus status;
    bytes32 serviceHash; // Hash of service description
    string metadataURI;
}

mapping(uint256 => Escrow) public escrows;
uint256 public nextEscrowId;

// Arbiter reputation
mapping(address => ArbiterStats) public arbiterStats;

struct ArbiterStats {
    uint256 totalCases;
    uint256 casesWonByBuyer;
    uint256 casesWonBySeller;
    uint256 reputationScore;
}
```

### Events

```solidity
event EscrowCreated(
    uint256 indexed escrowId,
    address indexed buyer,
    address indexed seller,
    uint256 amount
);

event EscrowReleased(uint256 indexed escrowId);
event EscrowRefunded(uint256 indexed escrowId);
event DisputeRaised(uint256 indexed escrowId, address indexed arbiter);
event DisputeResolved(uint256 indexed escrowId, address winner);
```

### Core Functions

```solidity
/// @notice Create an escrow for a service
/// @param seller Service provider
/// @param arbiter Address to resolve disputes (address(0) for auto)
/// @param token Token address (address(0) for ETH)
/// @param amount Escrow amount
/// @param deadline When escrow expires
/// @param serviceHash Hash of service agreement
/// @param metadataURI Link to service details
/// @return escrowId Unique escrow identifier
function createEscrow(
    address seller,
    address arbiter,
    address token,
    uint256 amount,
    uint256 deadline,
    bytes32 serviceHash,
    string calldata metadataURI
) external payable returns (uint256 escrowId);

/// @notice Release funds to seller (called by buyer)
/// @param escrowId Escrow to release
function releaseEscrow(uint256 escrowId) external;

/// @notice Refund buyer (called by seller or after deadline)
/// @param escrowId Escrow to refund
function refundEscrow(uint256 escrowId) external;

/// @notice Raise a dispute
/// @param escrowId Escrow in dispute
function raiseDispute(uint256 escrowId) external;

/// @notice Resolve dispute (called by arbiter)
/// @param escrowId Escrow to resolve
/// @param winner Who gets the funds (buyer or seller)
function resolveDispute(uint256 escrowId, address winner) external;
```

---

## Security Considerations

### Reentrancy Protection
```solidity
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract AgentPayRouter is ReentrancyGuard {
    function routePayment(...) external payable nonReentrant {
        // ...
    }
}
```

### Access Control
```solidity
import "@openzeppelin/contracts/access/Ownable.sol";

contract AgentPayRouter is Ownable {
    function setTreasury(address _treasury) external onlyOwner {
        treasury = _treasury;
    }
}
```

### Input Validation
```solidity
modifier validAddress(address addr) {
    require(addr != address(0), "Invalid address");
    _;
}

modifier validAmount(uint256 amount) {
    require(amount > 0, "Amount must be positive");
    _;
}
```

---

## Gas Optimizations

1. **Batch operations** - routeBatchPayment for multiple payments
2. **Storage packing** - Pack structs efficiently
3. **Events over storage** - Log data instead of storing when possible
4. **Pull over push** - Recipients withdraw rather than automatic transfers

---

## Deployment Script

```javascript
// scripts/deploy.js
const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with account:", deployer.address);

  // Deploy Router
  const Router = await hre.ethers.getContractFactory("AgentPayRouter");
  const router = await Router.deploy(
    process.env.TREASURY_ADDRESS,
    process.env.STAKING_ADDRESS
  );
  await router.deployed();
  console.log("AgentPayRouter deployed to:", router.address);

  // Deploy Streams
  const Streams = await hre.ethers.getContractFactory("AgentPayStreams");
  const streams = await Streams.deploy(router.address);
  await streams.deployed();
  console.log("AgentPayStreams deployed to:", streams.address);

  // Deploy Escrow
  const Escrow = await hre.ethers.getContractFactory("AgentPayEscrow");
  const escrow = await Escrow.deploy(router.address);
  await escrow.deployed();
  console.log("AgentPayEscrow deployed to:", escrow.address);

  // Verify on Basescan
  console.log("Verify commands:");
  console.log(`npx hardhat verify --network baseSepolia ${router.address} ${process.env.TREASURY_ADDRESS} ${process.env.STAKING_ADDRESS}`);
}

main().catch(console.error);
```

---

## Testing Strategy

### Unit Tests
```javascript
describe("AgentPayRouter", function() {
  it("Should route payment with correct fee", async function() {
    // Test implementation
  });
  
  it("Should handle ETH payments", async function() {
    // Test implementation
  });
  
  it("Should handle ERC20 payments", async function() {
    // Test implementation
  });
  
  it("Should distribute fees correctly", async function() {
    // Test implementation
  });
});
```

### Integration Tests
- Router + Streams interaction
- Router + Escrow interaction
- Multi-token scenarios
- Edge cases (zero amount, overflow, etc.)

---

## Next Steps

1. [ ] Write full contract implementations
2. [ ] Write comprehensive test suite
3. [ ] Deploy to Base Sepolia
4. [ ] Verify on Basescan
5. [ ] Build Python SDK
6. [ ] Build demo application

---

*This is the blueprint. Now we build.*
