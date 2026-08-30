require("dotenv").config();

const fs = require("fs");
const path = require("path");

function getContractAddress() {

if (fs.existsSync(path.join(__dirname, "..", "config.yaml"))) {
    const configContent =
        fs.readFileSync(
            path.join(__dirname, "..", "config.yaml"),
            "utf8"
        );

    const match =
        configContent.match(
            /address:\s*["']?(0x[a-fA-F0-9]{40})["']?/
        );

    if (match) {
        return match[1];
    }
}

return null;
}

const CONTRACT_ADDRESS =
getContractAddress();

async function main() {

if (!CONTRACT_ADDRESS) {
    throw new Error(
        "Contract address not found in config.yaml"
    );
}

const contract =
    await ethers.getContractAt(
        "MuleAccountRegistry",
        CONTRACT_ADDRESS
    );

console.log(
    "Using contract:",
    CONTRACT_ADDRESS
);

const accountId =
    "1234567890";

// -----------------------------------
// FLAG ACCOUNT
// -----------------------------------

console.log(
    "\nFlagging mule account..."
);

const flagTx =
    await contract.flagAccount(
        accountId,
        95,
        "Suspicious transaction chain"
    );

await flagTx.wait();

console.log(
    "Account flagged successfully."
);

// -----------------------------------
// CHECK BLACKLIST STATUS
// -----------------------------------

const blacklisted =
    await contract.isBlacklisted(
        accountId
    );

console.log(
    "\nBlacklisted:",
    blacklisted
);

// -----------------------------------
// GET ACCOUNT DETAILS
// -----------------------------------

const data =
    await contract.getAccountDetails(
        accountId
    );

console.log(
    "\nAccount Details:"
);

console.log(
    "Flagged:",
    data[0]
);

console.log(
    "Risk Score:",
    data[1].toString()
);

console.log(
    "Timestamp:",
    data[2].toString()
);

console.log(
    "Reason:",
    data[3]
);

// -----------------------------------
// UNFLAG ACCOUNT
// -----------------------------------

console.log(
    "\nUnflagging account..."
);

const unflagTx =
    await contract.unflagAccount(
        accountId
    );

await unflagTx.wait();

console.log(
    "Account unflagged successfully."
);

// -----------------------------------
// VERIFY STATUS AFTER UNFLAGGING
// -----------------------------------

const finalStatus =
    await contract.isBlacklisted(
        accountId
    );

console.log(
    "\nFinal Blacklisted Status:",
    finalStatus
);

console.log(
    "\nBlockchain test completed successfully."
);

}

main()
.then(() => process.exit(0))
.catch((error) => {
console.error(error);
process.exit(1);
});
