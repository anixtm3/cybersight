// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/// @title MuleAccountRegistry
/// @notice On-chain registry of flagged mule accounts. Stores only a
///         hashed account identifier — never the raw account number —
///         plus the flagging authority and evidence basis, so the
///         record can be trusted across banks and cyber cells without
///         a single owning database, and can withstand cross-examination
///         in court.
/// @dev    Records are immutable once written — no update/unflag
///         function is provided on purpose. Evidentiary provenance
///         must not be editable after the fact.
contract MuleAccountRegistry {
    enum EvidenceBasis {
        COMPLAINT_PATTERN,   // flagged from complaint-time fraud indicators
        BANK_REPORT,         // reported directly by a bank nodal officer
        LEA_INVESTIGATION,   // flagged by a law-enforcement investigation
        ML_PREDICTION,       // flagged by the prediction pipeline
        MANUAL_REVIEW        // flagged after analyst review
    }

    struct FlagRecord {
        bytes32 accountHash;      // SHA-256 hash of the account number (salted off-chain)
        address flaggedBy;        // wallet that submitted the transaction
        string authority;         // human-readable authority, e.g. "Delhi Cyber Cell", "I4C"
        EvidenceBasis evidenceBasis;
        uint8 riskScore;          // 0-100
        string reason;
        uint256 blockTimestamp;
        bool exists;
    }

    mapping(bytes32 => FlagRecord) private registry;
    bytes32[] private flaggedHashes;

    event AccountFlagged(
        bytes32 indexed accountHash,
        address indexed flaggedBy,
        string authority,
        EvidenceBasis evidenceBasis,
        uint8 riskScore,
        uint256 timestamp
    );

    modifier notAlreadyFlagged(bytes32 accountHash) {
        require(!registry[accountHash].exists, "Account already flagged");
        _;
    }

    /// @notice Flags an account as a mule account. Reverts if the hash
    ///         is already flagged — flags are add-only, never overwritten.
    /// @param accountHash SHA-256 hash of the account number, computed
    ///        off-chain using the same salt as app/crypto_utils.py
    ///        (hash_account_number) so backend lookups match on-chain
    ///        records exactly.
    function flagAccount(
        bytes32 accountHash,
        string calldata authority,
        EvidenceBasis evidenceBasis,
        uint8 riskScore,
        string calldata reason
    ) external notAlreadyFlagged(accountHash) {
        require(accountHash != bytes32(0), "Invalid account hash");
        require(riskScore <= 100, "Risk score must be 0-100");
        require(bytes(authority).length > 0, "Authority is required");

        registry[accountHash] = FlagRecord({
            accountHash: accountHash,
            flaggedBy: msg.sender,
            authority: authority,
            evidenceBasis: evidenceBasis,
            riskScore: riskScore,
            reason: reason,
            blockTimestamp: block.timestamp,
            exists: true
        });

        flaggedHashes.push(accountHash);

        emit AccountFlagged(accountHash, msg.sender, authority, evidenceBasis, riskScore, block.timestamp);
    }

    /// @notice Cheap existence check — backs GET /api/blockchain/check/{account_hash}
    function isBlacklisted(bytes32 accountHash) external view returns (bool) {
        return registry[accountHash].exists;
    }

    /// @notice Full provenance record — backs GET /api/blockchain/proof/{account_hash}
    function getProof(bytes32 accountHash)
        external
        view
        returns (
            address flaggedBy,
            string memory authority,
            EvidenceBasis evidenceBasis,
            uint8 riskScore,
            string memory reason,
            uint256 blockTimestamp
        )
    {
        require(registry[accountHash].exists, "Account not flagged");
        FlagRecord memory record = registry[accountHash];
        return (
            record.flaggedBy,
            record.authority,
            record.evidenceBasis,
            record.riskScore,
            record.reason,
            record.blockTimestamp
        );
    }

    /// @notice For the demo's registry view / dashboard counts.
    function totalFlagged() external view returns (uint256) {
        return flaggedHashes.length;
    }

    function getFlaggedHashAt(uint256 index) external view returns (bytes32) {
        require(index < flaggedHashes.length, "Index out of range");
        return flaggedHashes[index];
    }
}