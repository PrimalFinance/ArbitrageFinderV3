# Operating system related imports 
import os
from dotenv import load_dotenv
load_dotenv()


# Web3 related imports
from web3 import Web3

# Requests related imports
import requests

# Import Coin oracle
import Oracle.coin_oracle

ethereum_wallet = "0x43d1C1B1C1f8c49a24932B9d316CF8655006B5a5"

class Wallet:
    def __init__(self, api_url: str, network: str = "") -> None:
        self.network_rpc = api_url
        self.network = network
        self.oracle = Oracle.coin_oracle.CoinOracle()
    '''-----------------------------------'''
    def get_erc_token_balance(self, ticker: str):
        """
        This function will return the total balance of a wallet on the network passed. 
        Some networks are not supported yet. You can check what networks are supported in the "network_rpcs" dictionary.
        """

        # Get the address of the ticker for the network. 
        token_contract_address = self.oracle.get_address_by_ticker(ticker=ticker, network=self.network)
        # Request the balance from alchemy api. 
        endpoint = f"/?module=account&action=tokenbalance&contractaddress={token_contract_address}&address={ethereum_wallet}"
        url = self.network_rpc + endpoint
        response = requests.get(url=url)
        data = response.json()

        print(f"Data: {data}")



    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''



class ArbitrumWallet(Wallet):
    def __init__(self) -> None:
        api_url = ""
        super().__init__(api_url, "arbitrum")
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''


class OptimismWallet(Wallet):
    def __init__(self) -> None:
        # Alchemy API endpoint for the Optimism network
        alchemy_api_url = f"https://optimism-mainnet.alchemyapi.io/v2/{os.getenv('alchemy_optimism')}"
        super().__init__(alchemy_api_url, "optimism")
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''