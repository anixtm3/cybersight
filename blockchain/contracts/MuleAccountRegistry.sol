// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract MuleAccountRegistry {

    address public owner;

    struct MuleAccount {
        bool flagged;
        uint256 riskScore;
        uint256 timestamp;
        string reason;
    }

    mapping(string => MuleAccount) private muleAccounts;

    event AccountFlagged(
        string accountId,
        uint256 riskScore,
        uint256 timestamp
    );

    event AccountUnflagged(
        string accountId,
        uint256 timestamp
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function flagAccount(
        string memory accountId,
        uint256 riskScore,
        string memory reason
    ) public onlyOwner {

        muleAccounts[accountId] = MuleAccount({
            flagged: true,
            riskScore: riskScore,
            timestamp: block.timestamp,
            reason: reason
        });

        emit AccountFlagged(
            accountId,
            riskScore,
            block.timestamp
        );
    }

    function unflagAccount(
        string memory accountId
    ) public onlyOwner {

        require(
            muleAccounts[accountId].flagged,
            "Account not flagged"
        );

        muleAccounts[accountId].flagged = false;

        emit AccountUnflagged(
            accountId,
            block.timestamp
        );
    }

    function isBlacklisted(
        string memory accountId
    ) public view returns (bool) {

        return muleAccounts[accountId].flagged;
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
            string memory reason
        )
    {
        MuleAccount memory account = muleAccounts[accountId];

        return (
            account.flagged,
            account.riskScore,
            account.timestamp,
            account.reason
        );
    }
}