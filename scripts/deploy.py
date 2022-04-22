from brownie import Lottery, network, config
from scripts.helpers import get_account, get_contract


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


def main():
    deploy_lottery()
