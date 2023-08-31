# Operating system related imports 
import os
from dotenv import load_dotenv
load_dotenv()



# Requests related imports
import requests
from requests import Session

# CCXT related imports
import ccxt
from ccxt.base.errors import BadSymbol, RateLimitExceeded


# Pandas related imports 
import pandas as pd

# Storage handling 
import Oracle.storage

# Asynchronous related imports
from concurrent.futures import ThreadPoolExecutor

# Coingecko imports 
from pycoingecko import CoinGeckoAPI

# Coinmarketcap imports
from coinmarketcapapi import CoinMarketCapAPI


coin_id_path = "D:\\Coding\\VisualStudioCode\\Projects\\Python\\ArbitrageFinderV3\\Oracle\\coins.csv"

class CoinOracle(Oracle.storage.CoinStorage):
    def __init__(self) -> None:
        self.stable_coins = ["USD", "USDC", "USDT"]
        self.ccxt_exchanges_strings = ["kraken", "bitmart", "bitrue", "kucoin", "mexc"]
        self.exchanges = []
        self.coin_data = {}
        self.cg = CoinGeckoAPI()

        headers = {
                "Accepts": "application/json",
                "X-CMC_PRO_API_KEY": os.getenv("coinmarketcap_key")  
            }

        cmc_api = CoinMarketCapAPI(os.getenv("coinmarketcap_key"))
        self.cmc = Session()
        self.cmc.headers.update(headers)
        super().__init__(cmc=self.cmc, cmc_api=cmc_api)
        
        
    '''-----------------------------------'''
    def set_valid_exchanges(self, valid_exchanges: list) -> None:
        self.ccxt_exchanges_strings = valid_exchanges
    '''-----------------------------------'''
    def get_valid_exchanges(self) -> list:
        return self.ccxt_exchanges_strings
    '''-----------------------------------'''
    def create_exchange_objects(self):
        for e in self.ccxt_exchanges_strings:
            self.exchanges.append(getattr(ccxt, e.lower())())
    '''-----------------------------------'''
    def get_ccxt_coin_prices(self, ticker: str, exchange: ccxt, market: str = "USD"):

        trade_pair = f"{ticker}/{market}"
        try:
            price = exchange.fetch_ticker(trade_pair)
        except BadSymbol as e:
            try:
                price = exchange.fetch_ticker(f"{ticker}/USDT")
            except RateLimitExceeded:
                price = "N/A"
        except RateLimitExceeded as e:
            price = "N/A"    
        
        return price
    '''-----------------------------------'''
    def get_ccxt_exchange_prices(self, ticker: str):
        # Check that exchange objects have been created.
        if self.exchanges == []:
            self.create_exchange_objects()

        # Create a list that is equal in length to the number of exchange objects. This is for the thread mapping function.
        ticker_formatted = [ticker] * len(self.exchanges)
        # Use multiple threads to get data from exchanges. 
        with ThreadPoolExecutor() as thread_executor:
            thread_results = thread_executor.map(self.get_ccxt_coin_prices, ticker_formatted, self.exchanges)
            
            index = 0
            for i in thread_results:
                exchange_name = self.ccxt_exchanges_strings[index]

                if ticker not in self.coin_data:
                    self.coin_data[ticker] = {}

                if exchange_name not in self.coin_data[ticker]:
                    self.coin_data[ticker][exchange_name] = {}
                self.coin_data[ticker][exchange_name] = i
                index += 1

    '''-----------------------------------'''
    def get_coin_data(self):
        return self.coin_data
    '''-----------------------------------'''
    def get_cg_exchange_prices(self, name):
        print(f"Name: {name}")
        url = f"https://api.coingecko.com/api/v3/coins/{name.lower()}"

        print(f"URL: {url}")

        response = requests.get(url)
        
        # If request was successful. 
        if response.status_code == 200:
            data = response.json()
            return data["tickers"]
    '''-----------------------------------'''
    '''-----------------------------------'''
    def get_trending_tickers(self) -> list:
        '''
        Get the list of currently trending tickers on https://www.coingecko.com/
        '''

        trending_tickers = self.cg.get_search_trending()
        extracted_data = []
        for coin in trending_tickers['coins']:
            coin_data = coin['item']
            extracted_data.append({
                "id": coin_data["id"],
                "coin_name": coin_data["name"],
                "ticker": coin_data["symbol"],
                "marketcap_rank": coin_data["market_cap_rank"]
            })
        
        
        
        return extracted_data