from brownie import Lottery, network, config
from scripts.helpers import get_account, get_contract, fund_with_link
import time


def deploy_lottery():
    account = get_account()
    lottery = Lottery.deploy(
        get_contract("eth_usd_price_feed").address,
        get_contract("vrf_coordinator").address,
        get_contract("link_token").address,
        config["networks"][network.show_active()]["key_hash"],
        config["networks"][network.show_active()]["fee"],
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify", False),
    )
    print("lottery deployed")

    return lottery


def start_lottery():
    print("starting lottery")
    lottery = Lottery[-1]
    tx = lottery.startLottery()
    tx.wait(1)


def enter_lottery():
    print("entering lottery")
    account = get_account()
    lottery = Lottery[-1]
    value = lottery.getEntranceFee() + 1000
    tx = lottery.enter({"from": account, "value": value})
    tx.wait(1)


def end_lottery():
    print("ending lottery")
    account = get_account()
    lottery = Lottery[-1]

    tx = fund_with_link(lottery.address)
    tx.wait(1)
    end_tx = lottery.endLottery({"from": account})
    end_tx.wait(1)
    time.sleep(200)

    print(f"The winner is {lottery.lotteryWinner()}")


def main():
    deploy_lottery()
    start_lottery()
    enter_lottery()
    end_lottery()
