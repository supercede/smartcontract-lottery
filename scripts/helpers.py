from brownie import (
    accounts,
    network,
    config,
    VRFCoordinatorMock,
    MockV3Aggregator,
    LinkToken,
    Contract,
)

LOCAL_ENVIRONMENTS = ["development", "ganache-local"]
FORKED_LOCAL_ENVIRONMENTS = ["mainnet-fork", "mainnet-fork-dev"]

DECIMALS = 8  # Price feed aggregator usually returns 8 decimals
STARTING_PRICE = 200000000000  # 2000 + 8 decimals

# dictionary of contracts to mocks (key - config name, value - mock)
contracts_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if (
        network.show_active() in LOCAL_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    return accounts.add(config["wallets"]["from_key"])


def deploy_mocks():
    account = get_account()
    MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})


def get_contract(contract_name):

    # find mock of contract name from dictionary
    # if the network is in local blockchain, deploy the mock if it's not already
    # if it is not in local blockchain, find the address from brownie config and build the contract
    # return the contract

    contract_mock = contracts_to_mock[contract_name]

    if network.show_active() in LOCAL_ENVIRONMENTS:
        if len(contract_mock) <= 0:
            deploy_mocks()
        contract = contract_mock[-1]
    else:
        contract_address = network.show_active()[contract_name]
        contract = Contract.from_abi(
            contract_mock.name, contract_address, contract_mock.abi
        )

    return contract
