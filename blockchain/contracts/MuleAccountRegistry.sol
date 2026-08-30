// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MuleAccountRegistry {

    address public owner;

    struct MuleAccount {
        bool flagged;
        uint256 riskScore;
        uint256 timestamp;
        string reason;
        string flaggingAuthority;
        string evidenceBasis;
    }

    // Plaintext account IDs are NEVER stored.
    // The key is the keccak256 hash of the account identifier.
    mapping(bytes32 => MuleAccount) private muleAccounts;

    event AccountFlagged(
        bytes32 indexed accountHash,
        uint256 riskScore,
        uint256 timestamp,
        string flaggingAuthority,
        string evidenceBasis
    );

    event AccountUnflagged(
        bytes32 indexed accountHash,
        uint256 timestamp
    );

    modifier onlyOwner() {
        require(
            msg.sender == owner,
            "Only owner can perform this action"
        );
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function _hashAccount(
        string memory accountId
    ) internal pure returns (bytes32) {
        return keccak256(abi.encodePacked(accountId));
    }

    function flagAccount(
        string memory accountId,
        uint256 riskScore,
        string memory reason,
        string memory flaggingAuthority,
        string memory evidenceBasis
    ) public onlyOwner {

        require(
            bytes(flaggingAuthority).length > 0,
            "Flagging authority required"
        );

        require(
            keccak256(bytes(evidenceBasis)) ==
                keccak256(bytes("INVESTIGATION_VERIFIED")) ||
            keccak256(bytes(evidenceBasis)) ==
                keccak256(bytes("MONITORING_SUSPECTED")),
            "Invalid evidence basis"
        );

        bytes32 accountHash = _hashAccount(accountId);

        muleAccounts[accountHash] = MuleAccount({
            flagged: true,
            riskScore: riskScore,
            timestamp: block.timestamp,
            reason: reason,
            flaggingAuthority: flaggingAuthority,
            evidenceBasis: evidenceBasis
        });

        emit AccountFlagged(
            accountHash,
            riskScore,
            block.timestamp,
            flaggingAuthority,
            evidenceBasis
        );
    }

    function unflagAccount(
        string memory accountId
    ) public onlyOwner {

        bytes32 accountHash = _hashAccount(accountId);

        require(
            muleAccounts[accountHash].flagged,
            "Account not flagged"
        );

        muleAccounts[accountHash].flagged = false;

        emit AccountUnflagged(
            accountHash,
            block.timestamp
        );
    }

    function isBlacklisted(
        string memory accountId
    ) public view returns (bool) {

        bytes32 accountHash = _hashAccount(accountId);

        return muleAccounts[accountHash].flagged;
    }

    function getAccountDetails(
        string memory accountId
    )
        public
        view
        returns (
            bool flagged,
            uint256 riskScore,
            uint256 timestamp,
            string memory reason,
            string memory flaggingAuthority,
            string memory evidenceBasis,
            bytes32 accountHash
        )
    {
        accountHash = _hashAccount(accountId);

        MuleAccount memory account = muleAccounts[accountHash];

        return (
            account.flagged,
            account.riskScore,
            account.timestamp,
            account.reason,
            account.flaggingAuthority,
            account.evidenceBasis,
            accountHash
        );
    }
}
