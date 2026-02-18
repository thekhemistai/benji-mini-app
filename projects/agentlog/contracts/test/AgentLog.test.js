const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("AgentLog Contract", function () {
  let AgentLog;
  let agentLog;
  let owner;
  let agent1;
  let agent2;

  beforeEach(async function () {
    // Get signers
    [owner, agent1, agent2] = await ethers.getSigners();

    // Deploy contract
    AgentLog = await ethers.getContractFactory("AgentLog");
    agentLog = await AgentLog.deploy();
    await agentLog.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await agentLog.owner()).to.equal(owner.address);
    });

    it("Should initialize with zero global log count", async function () {
      // Check by creating first log and verifying ID generation
      const tx = await agentLog.connect(agent1).createLog(
        "TEST",
        ethers.keccak256(ethers.toUtf8Bytes("data")),
        ethers.keccak256(ethers.toUtf8Bytes("reasoning"))
      );
      await tx.wait();
      
      const logs = await agentLog.getAgentLogs(agent1.address, 0, 10);
      expect(logs.length).to.equal(1);
    });
  });

  describe("Log Creation", function () {
    it("Should create a log entry with correct data", async function () {
      const actionType = "TRADE";
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("trade_data"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      const tx = await agentLog.connect(agent1).createLog(
        actionType,
        dataHash,
        reasoningHash
      );
      
      const receipt = await tx.wait();
      
      // Check event was emitted
      const event = receipt.logs.find(
        log => log.fragment && log.fragment.name === "LogCreated"
      );
      expect(event).to.not.be.undefined;

      // Verify log count
      expect(await agentLog.getAgentLogCount(agent1.address)).to.equal(1);
    });

    it("Should generate unique entry IDs for different agents", async function () {
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("data"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      // Agent 1 creates log
      const tx1 = await agentLog.connect(agent1).createLog("ACTION", dataHash, reasoningHash);
      await tx1.wait();

      // Agent 2 creates log
      const tx2 = await agentLog.connect(agent2).createLog("ACTION", dataHash, reasoningHash);
      await tx2.wait();

      const logs1 = await agentLog.getAgentLogs(agent1.address, 0, 10);
      const logs2 = await agentLog.getAgentLogs(agent2.address, 0, 10);

      expect(logs1[0].entryId).to.not.equal(logs2[0].entryId);
    });

    it("Should link to previous hash for chain integrity", async function () {
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("data"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      // First log
      await (await agentLog.connect(agent1).createLog("FIRST", dataHash, reasoningHash)).wait();
      
      // Second log
      await (await agentLog.connect(agent1).createLog("SECOND", dataHash, reasoningHash)).wait();

      const logs = await agentLog.getAgentLogs(agent1.address, 0, 10);
      
      // First log should have no previous hash
      expect(logs[0].previousHash).to.equal(ethers.ZeroHash);
      
      // Second log should reference first
      expect(logs[1].previousHash).to.equal(logs[0].entryId);
    });

    it("Should increment log count correctly", async function () {
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("data"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      expect(await agentLog.getAgentLogCount(agent1.address)).to.equal(0);

      await (await agentLog.connect(agent1).createLog("LOG1", dataHash, reasoningHash)).wait();
      expect(await agentLog.getAgentLogCount(agent1.address)).to.equal(1);

      await (await agentLog.connect(agent1).createLog("LOG2", dataHash, reasoningHash)).wait();
      expect(await agentLog.getAgentLogCount(agent1.address)).to.equal(2);
    });
  });

  describe("Log Verification", function () {
    it("Should verify a log entry exists", async function () {
      const actionType = "DECISION";
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("decision_data"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      const tx = await agentLog.connect(agent1).createLog(actionType, dataHash, reasoningHash);
      await tx.wait();

      const logs = await agentLog.getAgentLogs(agent1.address, 0, 10);
      const entryId = logs[0].entryId;

      const verified = await agentLog.verifyLog(entryId);
      expect(verified.exists).to.be.true;
      expect(verified.actionType).to.equal(actionType);
      expect(verified.agent).to.equal(agent1.address);
    });

    it("Should revert when verifying non-existent log", async function () {
      const fakeEntryId = ethers.keccak256(ethers.toUtf8Bytes("fake"));
      
      await expect(
        agentLog.verifyLog(fakeEntryId)
      ).to.be.revertedWith("Log entry does not exist");
    });
  });

  describe("Pagination", function () {
    it("Should return paginated results correctly", async function () {
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("data"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      // Create 5 logs
      for (let i = 0; i < 5; i++) {
        await (await agentLog.connect(agent1).createLog(`LOG${i}`, dataHash, reasoningHash)).wait();
      }

      // Get first 2
      const page1 = await agentLog.getAgentLogs(agent1.address, 0, 2);
      expect(page1.length).to.equal(2);

      // Get next 2
      const page2 = await agentLog.getAgentLogs(agent1.address, 2, 2);
      expect(page2.length).to.equal(2);

      // Get last 1
      const page3 = await agentLog.getAgentLogs(agent1.address, 4, 2);
      expect(page3.length).to.equal(1);
    });

    it("Should return empty array for offset beyond total", async function () {
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("data"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      await (await agentLog.connect(agent1).createLog("LOG", dataHash, reasoningHash)).wait();

      const result = await agentLog.getAgentLogs(agent1.address, 10, 5);
      expect(result.length).to.equal(0);
    });
  });

  describe("Chain Integrity", function () {
    it("Should verify chain integrity for valid chain", async function () {
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("data"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      // Create chain of 3 logs
      for (let i = 0; i < 3; i++) {
        await (await agentLog.connect(agent1).createLog(`LOG${i}`, dataHash, reasoningHash)).wait();
      }

      const logs = await agentLog.getAgentLogs(agent1.address, 0, 10);

      // All should pass integrity check
      for (let log of logs) {
        expect(await agentLog.verifyChainIntegrity(log.entryId)).to.be.true;
      }
    });

    it("Should return false for non-existent entry", async function () {
      const fakeEntryId = ethers.keccak256(ethers.toUtf8Bytes("fake"));
      expect(await agentLog.verifyChainIntegrity(fakeEntryId)).to.be.false;
    });

    it("Should consider first entry valid (no previous hash)", async function () {
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("data"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      await (await agentLog.connect(agent1).createLog("FIRST", dataHash, reasoningHash)).wait();
      
      const logs = await agentLog.getAgentLogs(agent1.address, 0, 10);
      expect(await agentLog.verifyChainIntegrity(logs[0].entryId)).to.be.true;
    });
  });

  describe("Ownership", function () {
    it("Should allow owner to transfer ownership", async function () {
      await agentLog.transferOwnership(agent1.address);
      expect(await agentLog.owner()).to.equal(agent1.address);
    });

    it("Should not allow non-owner to transfer ownership", async function () {
      await expect(
        agentLog.connect(agent1).transferOwnership(agent2.address)
      ).to.be.revertedWith("Only owner");
    });

    it("Should not allow transferring to zero address", async function () {
      await expect(
        agentLog.transferOwnership(ethers.ZeroAddress)
      ).to.be.revertedWith("Invalid address");
    });
  });

  describe("Multiple Agents", function () {
    it("Should keep agent logs separate", async function () {
      const dataHash = ethers.keccak256(ethers.toUtf8Bytes("data"));
      const reasoningHash = ethers.keccak256(ethers.toUtf8Bytes("reasoning"));

      // Agent 1 creates 2 logs
      await (await agentLog.connect(agent1).createLog("A1_LOG1", dataHash, reasoningHash)).wait();
      await (await agentLog.connect(agent1).createLog("A1_LOG2", dataHash, reasoningHash)).wait();

      // Agent 2 creates 1 log
      await (await agentLog.connect(agent2).createLog("A2_LOG1", dataHash, reasoningHash)).wait();

      expect(await agentLog.getAgentLogCount(agent1.address)).to.equal(2);
      expect(await agentLog.getAgentLogCount(agent2.address)).to.equal(1);

      const logs1 = await agentLog.getAgentLogs(agent1.address, 0, 10);
      const logs2 = await agentLog.getAgentLogs(agent2.address, 0, 10);

      expect(logs1.length).to.equal(2);
      expect(logs2.length).to.equal(1);
      expect(logs1[0].agent).to.equal(agent1.address);
      expect(logs2[0].agent).to.equal(agent2.address);
    });
  });
});
