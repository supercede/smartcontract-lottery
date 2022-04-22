import time
from brownie import accounts, network
import pytest
from web3 import Web3
from scripts.deploy import deploy_lottery, fund_with_link
from scripts.helpers import LOCAL_ENVIRONMENTS, get_account, get_contract

# dev environment
def test_can_pick_winner_correctly():
    if network.show_active() not in LOCAL_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    value = lottery.getEntranceFee()

    lottery.startLottery({"from": account})

    lottery.enter({"from": account, "value": value})
    lottery.enter({"from": get_account(index=1), "value": value})
    lottery.enter({"from": get_account(index=2), "value": value})

    tx = fund_with_link(lottery.address)  # lottery.address works too
    tx.wait(1)
    end_tx = lottery.endLottery({"from": account})

    lottery_balance = lottery.balance()

    # VRF Coordinator callBackWithRandomness() - check mock - which calls fulfil randomness with our random number
    requestId = end_tx.events["RequestedRandomness"]["requestId"]
    randomness = 778
    # static randomness = 778
    # 778 % 3 = 1 (accounts[1] is the winner), pay out
    winner_initial_balance = accounts[1].balance()

    get_contract("vrf_coordinator").callBackWithRandomness(
        requestId, randomness, lottery.address, {"from": account}
    )

    print(f"winner_initial_balance {winner_initial_balance}")
    print(f"lottery_balance {lottery_balance}")

    assert lottery.lotteryWinner() == accounts[1]
    assert lottery.balance() == 0
    assert accounts[1].balance() == winner_initial_balance + lottery_balance


# testnet env
def test_can_pick_winner():
    if network.show_active() in LOCAL_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    value = lottery.getEntranceFee()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": value})
    lottery.enter({"from": account, "value": value})

    lottery_balance = lottery.balance()
    initial_balance = account.balance()

    tx = fund_with_link(lottery)
    tx.wait(1)

    lottery.endLottery({"from": account})
    time.sleep(200)

    print(f"accounts.balance() {account.balance()}")
    print(f"initial_balance + lottery_balance {initial_balance + lottery_balance}")

    assert lottery.lotteryWinner() == account
    assert lottery.balance() == 0
    # assert accounts.balance() == initial_balance + lottery_balance
