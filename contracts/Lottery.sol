// SPDX-License-Identifier: MIT

pragma solidity ^0.6.7;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable, VRFConsumerBase {
    address payable[] public players;
    AggregatorV3Interface public priceFeed;
    uint256 usdEntranceFee;

    bytes32 internal keyHash;
    uint256 internal fee;
    uint256 public randomResult;
    address payable public lotteryWinner;

    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lottery_state;

    constructor(
        address _priceFeed,
        address _vrfCoordinator,
        address _link,
        bytes32 _keyHash,
        uint256 _fee
    ) public VRFConsumerBase(_vrfCoordinator, _link) {
        priceFeed = AggregatorV3Interface(_priceFeed);
        usdEntranceFee = 50 * (10**18);
        lottery_state = LOTTERY_STATE.CLOSED;
        keyHash = _keyHash;
        fee = _fee;
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

    function endLottery() public onlyOwner {
        require(
            lottery_state == LOTTERY_STATE.OPEN,
            "This lottery is currently not open"
        );
        // require(LINK.balanceOf(address(this)) >= fee, "Not enough LINK - fill contract with faucet");
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER;

        bytes32 requestId = requestRandomness(keyHash, fee);
    }

    function fulfillRandomness(bytes32 requestId, uint256 randomness)
        internal
        override
    {
        require(
            lottery_state == LOTTERY_STATE.CALCULATING_WINNER,
            "Lottery state not in CALCULATING WINNER"
        );
        require(randomness > 0, "This request has not been fulfilled");

        uint256 playerIndex = randomness % players.length;

        lotteryWinner = players[playerIndex];
        lotteryWinner.transfer(address(this).balance);

        lottery_state = LOTTERY_STATE.CLOSED;
        players = new address payable[](0);
        randomResult = randomness;
    }
}
