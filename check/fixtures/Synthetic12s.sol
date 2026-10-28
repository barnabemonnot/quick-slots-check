// SPDX-License-Identifier: MIT
// Synthetic fixture for check/scan.py. Not taken from any project.
pragma solidity ^0.8.20;

contract SyntheticClock {
    uint256 public constant GENESIS_TIME = 1606824023;
    uint256 public constant SECONDS_PER_SLOT = 12;
    uint256 public constant BLOCKS_PER_YEAR = 2628000;
    uint256 public rewardPerBlock = 1e18;
    uint256 public votingPeriod = 45818; // block count
    uint256 public withdrawalDelayBlocks = 100;
    uint256 public constant EPOCH_PRICE = 4444444444444445;
    address constant BEACON_ROOTS = 0x000f3df6d732807ef1319fb7b8bb8522d0beac02;

    function currentEpoch() external view returns (uint256) {
        return (block.timestamp - GENESIS_TIME) / 12 / 32;
    }

    function slotStart(uint256 slot) public pure returns (uint256) {
        return GENESIS_TIME + slot * 12;
    }

    function deadline() external view returns (uint256) {
        return block.number + 7200; // one day of blocks
    }

    function blockTime() external pure returns (uint256 block_time) {
        block_time = 12;
    }
}

contract SyntheticSystemContracts {
    address constant WITHDRAWAL_REQUESTS = 0x00000961ef480eb55e80d19ad83579a64c007002;

    function oldHash(uint256 n) external view returns (bytes32) {
        require(block.number - n <= 256, "outside window");
        return blockhash(n);
    }
}

contract SyntheticLock {
    uint256 public constant LOCK_WINDOW = 50400; // one week of blocks

    function slotsSince(uint256 nowTime, uint256 startTime) external pure returns (uint256) {
        return (nowTime - startTime) / 12;
    }
}
