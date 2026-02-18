// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title AgentLog
 * @notice Immutable activity logging for AI agents
 * @dev Stores log entry hashes on-chain, full data on IPFS
 */
contract AgentLog {
    
    // ============ Structs ============
    
    struct LogEntry {
        bytes32 entryId;
        address agent;
        uint256 timestamp;
        string actionType;      // "TRADE", "DECISION", "ERROR", etc.
        bytes32 dataHash;       // Hash of full data (IPFS)
        bytes32 reasoningHash;  // Hash of reasoning (IPFS)
        bytes32 previousHash;   // For chain integrity
        uint256 blockNumber;
        bool exists;
    }
    
    // ============ State ============
    
    // entryId => LogEntry
    mapping(bytes32 => LogEntry) public logs;
    
    // agent => array of entryIds
    mapping(address => bytes32[]) public agentLogs;
    
    // agent => log count
    mapping(address => uint256) public logCount;
    
    // Global log counter for unique IDs
    uint256 private _globalLogCount;
    
    // Owner for admin functions
    address public owner;
    
    // ============ Events ============
    
    event LogCreated(
        bytes32 indexed entryId,
        address indexed agent,
        string actionType,
        uint256 timestamp,
        bytes32 dataHash
    );
    
    event AgentRegistered(address indexed agent, uint256 timestamp);
    
    // ============ Modifiers ============
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    // ============ Constructor ============
    
    constructor() {
        owner = msg.sender;
        _globalLogCount = 0;
    }
    
    // ============ Core Functions ============
    
    /**
     * @notice Create a new log entry
     * @param actionType Type of action (e.g., "TRADE", "DECISION")
     * @param dataHash Hash of full log data (stored on IPFS)
     * @param reasoningHash Hash of reasoning data (stored on IPFS)
     * @return entryId Unique identifier for this log entry
     */
    function createLog(
        string calldata actionType,
        bytes32 dataHash,
        bytes32 reasoningHash
    ) external returns (bytes32 entryId) {
        
        // Generate unique entry ID
        _globalLogCount++;
        entryId = keccak256(abi.encodePacked(
            msg.sender,
            block.timestamp,
            _globalLogCount,
            block.number
        ));
        
        // Get previous hash for chain integrity
        bytes32 previousHash = _getPreviousHash(msg.sender);
        
        // Create log entry
        LogEntry memory newLog = LogEntry({
            entryId: entryId,
            agent: msg.sender,
            timestamp: block.timestamp,
            actionType: actionType,
            dataHash: dataHash,
            reasoningHash: reasoningHash,
            previousHash: previousHash,
            blockNumber: block.number,
            exists: true
        });
        
        // Store log
        logs[entryId] = newLog;
        agentLogs[msg.sender].push(entryId);
        logCount[msg.sender]++;
        
        // Emit event
        emit LogCreated(
            entryId,
            msg.sender,
            actionType,
            block.timestamp,
            dataHash
        );
        
        return entryId;
    }
    
    /**
     * @notice Verify a log entry exists and get its data
     * @param entryId The log entry ID to verify
     * @return entry The full log entry data
     */
    function verifyLog(bytes32 entryId) external view returns (LogEntry memory entry) {
        require(logs[entryId].exists, "Log entry does not exist");
        return logs[entryId];
    }
    
    /**
     * @notice Get all log entries for an agent
     * @param agent The agent address
     * @param offset Starting index for pagination
     * @param limit Maximum number of entries to return
     * @return entries Array of log entries
     */
    function getAgentLogs(
        address agent,
        uint256 offset,
        uint256 limit
    ) external view returns (LogEntry[] memory entries) {
        uint256 totalLogs = agentLogs[agent].length;
        
        if (offset >= totalLogs) {
            return new LogEntry[](0);
        }
        
        uint256 end = offset + limit;
        if (end > totalLogs) {
            end = totalLogs;
        }
        
        uint256 resultCount = end - offset;
        entries = new LogEntry[](resultCount);
        
        for (uint256 i = 0; i < resultCount; i++) {
            bytes32 entryId = agentLogs[agent][offset + i];
            entries[i] = logs[entryId];
        }
        
        return entries;
    }
    
    /**
     * @notice Get the total number of logs for an agent
     * @param agent The agent address
     * @return count Number of logs
     */
    function getAgentLogCount(address agent) external view returns (uint256) {
        return logCount[agent];
    }
    
    /**
     * @notice Verify the integrity of a log chain
     * @param entryId The entry to start verification from
     * @return isValid True if chain is valid
     */
    function verifyChainIntegrity(bytes32 entryId) external view returns (bool isValid) {
        LogEntry memory entry = logs[entryId];
        if (!entry.exists) return false;
        
        // If no previous hash, it's the first entry (valid)
        if (entry.previousHash == bytes32(0)) return true;
        
        // Verify previous entry exists
        LogEntry memory previousEntry = logs[entry.previousHash];
        return previousEntry.exists;
    }
    
    // ============ Admin Functions ============
    
    /**
     * @notice Transfer ownership
     * @param newOwner New owner address
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid address");
        owner = newOwner;
    }
    
    // ============ Internal Functions ============
    
    /**
     * @notice Get the hash of the previous log entry for an agent
     * @param agent The agent address
     * @return previousHash Hash of previous entry, or 0 if first entry
     */
    function _getPreviousHash(address agent) internal view returns (bytes32) {
        uint256 count = agentLogs[agent].length;
        if (count == 0) {
            return bytes32(0);
        }
        return agentLogs[agent][count - 1];
    }
}
