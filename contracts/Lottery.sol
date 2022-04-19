// SPDX-License-Identifier: MIT

pragma solidity ^0.6.7;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";

contract License {
    address payable[] public players;
    AggregatorV3Interface public priceFeed;
    uint256 usdEntranceFee;

    constructor (address _priceFeed) public {
        priceFeed = AggregatorV3Interface(_priceFeed);
        usdEntranceFee = 50;
    }

    function enter () public payable {
        players.push(msg.sender);
    }

    function getEntranceFee() public {}

    function startLottery () public {}

    function endLottery () public{}
}