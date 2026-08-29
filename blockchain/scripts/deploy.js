/**
 * @deprecated
 * Sprint 2 now uses deploy.py (Web3.py)
 * This script is kept only for backward compatibility.
 */
require("dotenv").config();

const fs = require("fs");
const path = require("path");

const CONFIG_PATH =
    path.join(__dirname, "..", "config.yaml");

async function main() {

    const MuleAccountRegistry =
        await ethers.getContractFactory(
            "MuleAccountRegistry"
        );

    const contract =
        await MuleAccountRegistry.deploy();

    await contract.waitForDeployment();

    const contractAddress =
        await contract.getAddress();

    console.log(
        "MuleAccountRegistry deployed to:",
        contractAddress
    );

    const rpcUrl =
        process.env.GANACHE_RPC_URL;

    if (!rpcUrl) {
        throw new Error(
            "GANACHE_RPC_URL not found in .env"
        );
    }

    let configContent =
        fs.readFileSync(
            CONFIG_PATH,
            "utf8"
        );

    configContent =
        configContent.replace(
            /address:\s*["']?.*["']?/,
            `address: "${contractAddress}"`
        );

    configContent =
        configContent.replace(
            /rpc_url:\s*["']?.*["']?/,
            `rpc_url: "${rpcUrl}"`
        );

    fs.writeFileSync(
        CONFIG_PATH,
        configContent
    );

    console.log(
        "Updated config.yaml"
    );
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
