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

# Numpy imports 
import numpy as np

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
    

    """
    ------------------------------------------------------------------------------------------
    CoinGecko Functions
    ------------------------------------------------------------------------------------------
    """
    '''-----------------------------------'''
    def get_cg_id(self, ticker: str) -> str:
        """
        Queries Coingecko.com for the ID of the coin based on the ticker.
        """
        # Read the csv file to make sure the id is not already present. 
        csv_file = pd.read_csv(coin_id_path)

        # Get the index of the ticker
        ticker_index = csv_file[csv_file["ticker"] == ticker.lower()].index[0]

        # Get the cg_id of at that index.
        csv_id = csv_file.loc[ticker_index, "cg_name"]

        # If there is no id for the coin in the csv file. 
        if csv_id is np.nan:
            # Make the API request to fetch the list of all coins
            url = "https://api.coingecko.com/api/v3/coins/list"
            response = requests.get(url)

            if response.status_code == 200:
                coin_list = response.json()

                # Search for the coin by name and extract its ID
                coin_id = None
                for coin in coin_list:
                    if coin["symbol"].lower() == ticker.lower():
                        return coin["id"]
            else:
                print(f"Status: {response.status_code}")
        # If the coin id was found in the csv file, then just return that id. 
        else:
            return None
            

    '''-----------------------------------'''
    def write_cg_id_to_csv(self, ticker: str, cg_id: str) -> None:
        """
        Write the ID to the row that matches the ticker in the parameter.
        """
        # Read the csv file.
        csv_file = pd.read_csv(coin_id_path)

        # Get the index of the ticker.
        ticker_index = csv_file[csv_file["ticker"] == ticker.lower()].index[0]

        # Insert ID into dataframe.
        csv_file.loc[ticker_index, "cg_name"] = cg_id

        # Write dataframe to csv file.
        csv_file.to_csv(coin_id_path, index=False)

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
    

    '''-----------------------------------'''
    def get_gainers_losers(self, limit: int = 100, return_data: str = "all") -> list:
        '''
        Get the list of the current top gaining coins on https://www.coingecko.com/

        limit: Number of coins that will be retrieved. 
        return_data: Is a string that can either be set to "all" or ticker. When set to all it will return the full dataset. 
                     If set to ticker, it will return only the tickers. 
        '''
        # Endpoint URL for getting top gainers
        url = "https://api.coingecko.com/api/v3/coins/markets"

        # Parameters for the request
        params = {
            "vs_currency": "usd",   # You can change the currency here if needed
            "order": "percent_change_24h_desc",  # Sort by market cap in descending order
            "per_page": limit,   # Number of results per page
            "page": 1,        # Page number
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            top_gainers = response.json()

            data = []
            for coin in top_gainers:
                data.append({
                    "id": coin["id"],
                    "symbol": coin["symbol"],
                    "name": coin["name"],
                    "24h_change": coin["price_change_percentage_24h"],
                    "market_cap": coin["market_cap"],
                })
            
            if return_data == "all":
                # Create dataframe from dictionary. 
                df = pd.DataFrame(data)
                # Create separate dataframes for the gainers and losers. 
                gainers = df[df[df["24h_change"] > 0]]
                losers = df[df[df["24h_change"] < 0]]

                # Sort the dataframes. 
                gainers = gainers.sort_values(by="24h_change", ascending=False).reset_index().drop("index", axis=1)
                losers = losers.sort_values(by="24h_change").reset_index().drop("index", axis=1)
                
                return gainers, losers
            elif return_data == "ticker":
                # Parse the dictionary to only include the symbold and the 24 hour change. 
                data = [{"symbol":i["symbol"], "24h_change": i["24h_change"]} for i in data]
                # Create dataframe from dictionary.
                df = pd.DataFrame(data)
                # Create separate dataframes for the gainers and losers.
                gainers = df[df["24h_change"] > 0]
                losers = df[df["24h_change"] < 0]

                # Sort the dataframes. 
                gainers = gainers.sort_values(by="24h_change", ascending=False).reset_index().drop("index", axis=1)
                losers = losers.sort_values(by="24h_change").reset_index().drop("index", axis=1)
                
                return gainers, losers
    '''-----------------------------------'''
    def custom_ticker_sort(self, item):
        price_change = item.get("price_change_percentage_24h")
        if price_change == None:
            return float("-inf")
        return price_change
    

