# Operating system related imports 
import os
from dotenv import load_dotenv
load_dotenv()

# Alchemy api imports
import alchemy

# Time & Date related imports
import time
import datetime as dt

# Pandas imports
import pandas as pd
pd.options.display.float_format = "{:.3f}".format

# Import wallet database.
from Wallet.wallet_db import WalletDatabase

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
        self.wrapped_native_coin = f"W{self.native_coin}"
        self.csv_name = csv_file
        self.csv_file_path = csv_file_paths + self.csv_name
        self.wallet_db = WalletDatabase(self.csv_file_path)


        self.stable_coins = ["USDC", "USDT"]
        self.oracle = Oracle.coin_oracle.CoinOracle()

    '''-----------------------------------'''
    def update_token_balances(self):
        # Get the current time and date.
        current = dt.datetime.now()
        cur_time = str(current.time()).split(".")[0]
        cur_date = current.date()



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
                           "value": "${:.2f}".format(value) 
                           }}

        # Token balances for alt-coins. 
        token_balances = self.alchemy.core.get_token_balances(ethereum_wallet)["token_balances"]

        # Iterate through each token balance entry
        for token_balance_entry in token_balances:
            contract_address = token_balance_entry.contract_address
            ticker = self.oracle.get_ticker_by_address(address=contract_address.upper())
            token_balance_hex = token_balance_entry.token_balance
            
            # Convert the token balance from hex to an integer
            token_balance = int(token_balance_hex, 16)
            

            if token_balance != 0 and ticker != None:
                # Get the coin id
                try:
                    coin_price = self.oracle.get_coin_prices(coin_id=ticker, source="cmc")
                    if ticker in self.stable_coins:
                        stable_conversion = 10 ** 6
                        token_balance = token_balance / stable_conversion
                    elif ticker == self.wrapped_native_coin:
                        token_balance = token_balance / wei_to_ether_conversion
                    else:
                        token_balance = token_balance / (10 ** 18) 
                    #token_balance = token_balance / wei_to_ether_conversion
                    value = coin_price * token_balance
                    # Add coin to wallet holdings dictionary. 
                    wallet_holdings[ticker] = {
                        "balance": token_balance,
                        "value": "${:.2f}".format(value)
                    }
                except AttributeError:
                    print(f"Contract: {contract_address}")
                except TypeError:
                    print(f"Ticker2: {ticker}")
                    ticker = contract_address
                    print(f'Contract: {contract_address}')

            else:
                value = 0

        # List to hold the holdings data.
        data_list = []
        for ticker, info in wallet_holdings.items():
            data_list.append({"ticker": ticker, **info})
        
        # Create dataframe. 
        df = pd.DataFrame(data_list)
        df["date"] = [cur_date] * len(df)
        df["time"] = [cur_time] * len(df)
        df = df[["date", "time", "ticker", "balance", "value"]]
        df.to_csv(self.csv_file_path, index=False)
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
class PolygonWallet(Wallet):
    def __init__(self) -> None:
        api_key = os.getenv("alchemy_polygon")
        network = alchemy.Network.MATIC_MAINNET
        csv_file = "polygon_wallet.csv"
        native_coin = "MATIC"
        super().__init__(api_key, network, csv_file, native_coin)
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''