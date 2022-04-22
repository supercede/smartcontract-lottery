from brownie import network, exceptions
import pytest
from web3 import Web3
from scripts.deploy import deploy_lottery, fund_with_link
from scripts.helpers import LOCAL_ENVIRONMENTS, get_account


def test_get_entrance_fee():
    if network.show_active() not in LOCAL_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()

    # Calculate entrance fee
    # for test, VRFPriceConsumer is mocked at 2000USD/ETH
    # ∴ 50USD = 0.025ETH

    entrance_fee = lottery.getEntranceFee()
    expected_entrance_fee = Web3.toWei(0.025, "ether")
    assert entrance_fee == expected_entrance_fee


def test_cant_enter_unless_started():
    if network.show_active() not in LOCAL_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    value = lottery.getEntranceFee()

    with pytest.raises(exceptions.VirtualMachineError):
        lottery.enter({"from": account, "value": value})


def test_can_start_and_enter_lottery():
    if network.show_active() not in LOCAL_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    value = lottery.getEntranceFee()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": value})

    assert lottery.players(0) == account


def test_can_end_lottery():
    if network.show_active() not in LOCAL_ENVIRONMENTS:
        pytest.skip()

    lottery = deploy_lottery()
    account = get_account()
    value = lottery.getEntranceFee()

    lottery.startLottery({"from": account})
    lottery.enter({"from": account, "value": value})

    tx = fund_with_link(lottery.address)
    tx.wait(1)
    lottery.endLottery({"from": account})

    print(lottery.lottery_state())

    # solidity enums are zero based
    # 0 OPEN
    # 1 CLOSED
    # 2 CALCULATING_WINNER
    assert lottery.lottery_state() == 2
