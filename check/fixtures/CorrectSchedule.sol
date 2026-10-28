// SPDX-License-Identifier: MIT
// Synthetic negative fixture: uses real block timestamps and no fixed duration. Expected hits: none.
pragma solidity ^0.8.20;

contract CorrectClock {
    uint256 public lastUpdate;

    function touch() external {
        lastUpdate = block.timestamp;
    }

    function elapsed() external view returns (uint256) {
        return block.timestamp - lastUpdate;
    }
}
