# Operating system related imports 
import os
from dotenv import load_dotenv
load_dotenv()

# Alchemy api imports
import alchemy


# Web3 related imports
from web3 import Web3

# Requests related imports
import requests

# Import Coin oracle
import Oracle.coin_oracle

ethereum_wallet = "0x43d1C1B1C1f8c49a24932B9d316CF8655006B5a5"

csv_file_paths = "D:\\Coding\\VisualStudioCode\\Projects\\Python\\ArbitrageFinderV3\\Wallet\\"

class Wallet:
    def __init__(self, api_key: str, network: alchemy.Network, csv_file: str, native_coin: str = "ETH") -> None:
        self.alchemy = alchemy.Alchemy(api_key=api_key, network=network)
        self.native_coin = native_coin
        self.csv_name = csv_file
        self.csv_file_path = csv_file_paths + self.csv_name
        self.oracle = Oracle.coin_oracle.CoinOracle()

    '''-----------------------------------'''
    def get_token_balances(self):
        # Balance for ETH in unites of wei.
        eth_balance_wei = self.alchemy.core.get_balance(ethereum_wallet) 
        # Wei to ether conversion
        wei_to_ether_conversion = 10 ** 18
        # Convert from Wei to Ether.
        eth_balance = eth_balance_wei / wei_to_ether_conversion
        coin_id = self.oracle.get_id_by_ticker(ticker=self.native_coin)
        price = self.oracle.get_coin_prices(coin_id=coin_id)
        # Calculate the value of the holdings
        value = price * eth_balance

        # Dictionary to hold the balance of the wallet.
        wallet_holdings = {self.native_coin: {
                           "balance": eth_balance,
                           "value": value 
                           }}

        # Token balances for alt-coins. 
        token_balances = self.alchemy.core.get_token_balances(ethereum_wallet)["token_balances"]

        # Iterate through each token balance entry
        for token_balance_entry in token_balances:
            contract_address = token_balance_entry.contract_address
            ticker = self.oracle.get_ticker_by_address(address=contract_address)
            token_balance_hex = token_balance_entry.token_balance
            
            # Convert the token balance from hex to an integer
            token_balance = int(token_balance_hex, 16)
            

            if token_balance != 0:
                # Get the coin id
                coin_id = self.oracle.get_id_by_ticker(ticker=ticker.lower())
                coin_price = self.oracle.get_coin_prices(coin_id=coin_id)
                value = coin_price * token_balance
            else:
                value = 0

            # Add coin to wallet holdings dictionary. 
            wallet_holdings[ticker] = {
                "balance": token_balance,
                "value": value
            }


        print(f"Wallet: {wallet_holdings}")
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''



class EthereumWallet(Wallet):
    def __init__(self) -> None:
        api_key = ""
        network = alchemy.Network.ETH_MAINNET
        super().__init__(api_key, network)



class ArbitrumWallet(Wallet):
    def __init__(self) -> None:
        api_key = os.getenv("alchemy_arbitrum")
        network = alchemy.Network.ARB_MAINNET
        csv_file = "arbitrum_wallet.csv"
        super().__init__(api_key=api_key, network=network, csv_file=csv_file)
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''


class OptimismWallet(Wallet):
    def __init__(self) -> None:
        api_key = os.getenv("alchemy_optimism")
        network = alchemy.Network.OPT_MAINNET
        csv_file = "optimism_wallet.csv"
        super().__init__(api_key=api_key, network=network, csv_file=csv_file)
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''