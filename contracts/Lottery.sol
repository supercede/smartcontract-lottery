// SPDX-License-Identifier: MIT

pragma solidity ^0.6.7;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable {
    address payable[] public players;
    AggregatorV3Interface public priceFeed;
    uint256 usdEntranceFee;
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE lottery_state;

    constructor(address _priceFeed) public {
        priceFeed = AggregatorV3Interface(_priceFeed);
        usdEntranceFee = 50 * (10**18);
        lottery_state = LOTTERY_STATE.CLOSED;
    }

    function enter() public payable {
        uint256 value = msg.value;
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "This lottery is currently closed"
        );
        require(
            msg.value >= getEntranceFee(),
            "More ETH is required to join this lottery"
        );
        players.push(msg.sender);
    }

    function getEntranceFee() public view returns (uint256) {
        (, int256 price, , , ) = priceFeed.latestRoundData();
        uint256 adjustedPrice = uint256(price) * 10**10; // pricefeed.decimals() is 8, 18 (magnitude of wei to eth) - 8 = 10

        // convert usd entrance fee to wei equivalent
        uint256 entranceFee = (usdEntranceFee * 10**18) / adjustedPrice;
        return entranceFee;
    }

    function startLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.CLOSED,
            "This lottery cannot be opened right now"
        );
        lottery_state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {}
}
