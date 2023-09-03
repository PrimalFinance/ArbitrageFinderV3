
# Date & Time related imports
import time

# CSV related imports
import csv

# Regular expression imports 
import re

# Requests imports
import requests

import json

# Pandas related imports
import pandas as pd

# Numpy related imports
import numpy as np

# Coinmarketcap imports
from coinmarketcapapi import CoinMarketCapAPI



coin_id_path = "D:\\Coding\\VisualStudioCode\\Projects\\Python\\ArbitrageFinderV3\\Oracle\\coins.csv"

class CoinStorage:
    def __init__(self, cmc, cmc_api) -> None:
        self.cmc = cmc
        self.cmc_api = cmc_api
        self.csv_file = "D:\\Coding\\VisualStudioCode\\Projects\\Python\\ArbitrageFinderV3\\Oracle\\coins.csv"
        self.coin_data = None
        self.network_to_column_mapping = {
            "arbitrum": "ARB_ADDRESS",
            "avalanche C-Chain": "AVAX_ADDRESS",
            "base": "BASE_ADDRESS",
            "bnb smart chain (BEP20)": "BNB_ADDRESS",
            "ethereum": "ETH_ADDRESS",
            "linea": "LINEA_ADDRESS",
            "metis andromeda": "METIS_ADDRESS",
            "optimism": "OP_ADDRESS",
            "polygon": "POLYGON_ADDRESS",
            "polygon zkevm": "POLYGON_ZKEVM_ADDRESS",
            "solana": "SOL_ADDRESS",
            "zksync era": "ZKSYNC_ERA_ADDRESS"
        }
    '''----------------------------------- Data Retrieval Functions -----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    def get_coin_name(self, ticker: str) -> str:
        '''
        Makes an api call if "coin_data" does not already have data. 
        It then searches through the data retrieved and finds the coin name that matches the ticker. 
        '''
        if self.coin_data == None:
            # Create a URL to the CoinGecko API endpoint for getting coin information.
            url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc"

            # Use the requests.get() method to make a request to the API endpoint.
            response = requests.get(url)

            if response.status_code == 200:
                self.coin_data = response.json()

        # Find the coin with the matching ticker in the JSON response.
        for coin in self.coin_data:
            try:
                if coin['symbol'] == ticker.lower():
                    name = coin['name']
                    return name
            except TypeError:
                print(f"Tag: {coin}")
    '''-----------------------------------'''
    def get_coin_prices(self, coin_id: str, source = "cg"):

        if source.lower() == "cg":
            base_url = "https://api.coingecko.com/api/v3"
            endpoint = f"/simple/price?ids={coin_id}&vs_currencies=usd"  # Replace "usd" with the desired currency

            url = base_url + endpoint
            print(f"Url: {url}")
            response = requests.get(url)
            data = response.json()

            if coin_id in data:
                return data[coin_id]["usd"]
            else:
                return None
        elif source.lower() == "cmc":
             # Define the API endpoint for CoinMarketCap's cryptocurrency quotes
            base_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
            
            # Specify the parameters for the request
            params = {
                "symbol": coin_id,     
                "convert": "USD"  
            }

            response = self.cmc.get(base_url, params=params)

            # If successful query.
            if response.status_code == 200:
                data = response.json()

                # Check if the coin symbol exists in the response. 
                if coin_id in data["data"]:
                    return data["data"][coin_id]["quote"]["USD"]["price"]
    '''-----------------------------------'''
    def get_name_by_ticker(self, ticker: str, data_source: str = "cg") -> str:
        """
        Search the csv file for the term in the ticker. 
        Return the name that matches the row of the ticker. 
        """
        csv_file = pd.read_csv(coin_id_path)
        #csv_file.reset_index(inplace=True)

        matching_row = csv_file[csv_file["ticker"] == ticker.lower()]

        if not matching_row.empty:
            if data_source == "cg":
                name = matching_row.iloc[0]["cg_name"]
            elif data_source == "cmc":
                name = matching_row.iloc[0]["cmc_name"]
            else:
                name = matching_row.iloc[0]["cg_name"]
            return name
        else:
            return None
        
    '''-----------------------------------'''
    def get_ticker_by_address(self, address: str) -> str:
        """
        address: String of the contract address for the coin.

        This function will search the csv file, and return the ticker on the row of the matching address.
        """

        csv_file = pd.read_csv(coin_id_path)

        # Make the address uppercase if it is not already since that is how it is stored in the csv file. 
        address = address.upper()


        columns = csv_file.columns

        columns = columns[3:]

        for i in csv_file.iterrows():

            row_data = i[1]
            # Check if the address matches any of the values in the row. 
            address_found = any(address == value for value in row_data)

            if address_found:
                return row_data["ticker"].upper()
    '''-----------------------------------'''
    def get_id_by_ticker(self, ticker: str, method: int = 2) -> str:
        """
        Queries the coingecko api with the ticker and returns the id for coingecko to make further searches. 
        """

        if method == 1:
            base_url = "https://api.coingecko.com/api/v3/coins/list"
            response = requests.get(base_url)

            if response.status_code == 200:
                coins_list = response.json()
                for coin in coins_list:
                    if coin["symbol"].lower() == ticker.lower():
                        return coin["id"]
            else:
                print(f"Failed to retrieve data id coingecko api for: {ticker}")
                return np.nan
        elif method == 2:
            csv_file = pd.read_csv(coin_id_path)

            ticker = ticker.lower()

            ticker_index = csv_file[csv_file["ticker"] == ticker].index.values[0]

            coin_id = csv_file.loc[ticker_index, "cg_name"]
            return coin_id
            

    '''-----------------------------------'''
    def get_tickers_in_file(self) -> list:
        """
        Retrieves all the tickers within the "ticker" column in the csv file.
        """
        csv_data = pd.read_csv(coin_id_path)
        tickers = csv_data["ticker"].tolist()
        return tickers
    '''-----------------------------------'''
    def get_dex_pairs(self, dex_name: str = "Uniswap V3", network: str = "Optimism"):
        """
        Query coingecko api for all of the trading pairs from the DEX on the desired network.
        """
        # CoinGecko API endpoint for exchange information
        exchange_endpoint = "https://api.coingecko.com/api/v3/exchanges"

        # Fetch exchange data
        response = requests.get(exchange_endpoint)
        exchanges = response.json()

        print(f"Response: {response.status_code}")

        # Find the Uniswap V3 exchange on Optimism
        dex_exchange = None
        for exchange in exchanges:
            full_name = dex_name + " " + f"({network})"
            if exchange["name"] == full_name :
                dex_exchange = exchange
                break

        if dex_exchange:
            exchange_id = dex_exchange["id"]

            # CoinGecko API endpoint for pairs traded on an exchange
            pairs_endpoint = f"https://api.coingecko.com/api/v3/exchanges/{exchange_id}/pairs"

            print(f"Pairs: {pairs_endpoint}")

            # Fetch pairs traded on Uniswap V3 on Optimism
            response = requests.get(pairs_endpoint)
            pairs = response.json()

            print(f"Pairs: {pairs}")
            
            for pair in pairs:
                print("Pair ID:", pair["id"])
                print("Base Currency:", pair["base"]["name"])
                print("Quote Currency:", pair["quote"]["name"])
                print("----")

            # Coingecko API endpoint for pairs traded on the exchange.
    '''-----------------------------------'''
    def get_csv_file(self) -> pd.DataFrame:
        """
        Read the csv file, and return it in a pandas dataframe.
        """
        return pd.read_csv(coin_id_path)
    '''----------------------------------- Boolean Checks -----------------------------------'''
    '''-----------------------------------'''
    def does_coin_exist(self, ticker: str = "", name: str = "") -> bool:
        '''
        Can either search the file by "ticker" or "name". If searching by "ticker" then keep "name" blank. 
        Will return a boolean representing if the ticker was found. 
        '''
        try:
            with open(self.csv_file, "r") as file:
                reader = csv.reader(file)

                # Logic to determine what to search for. 
                if ticker != "" and name != "":
                    for row in reader:
                        row_ticker, row_name = row
                        if row_ticker == ticker and row_name == name:
                            return True
                    return False
                elif ticker != "":
                    for row in reader:
                        row_ticker, row_name = row
                        if row_ticker == ticker:
                            return True
                    return False
                elif name != "":
                    for row in reader:
                        row_ticker, row_name = row
                        if row_name == name:
                            return True
                    return False
        except Exception as e:
            print(f"[Csv Scan Error] {e}")
            return False

    '''-----------------------------------'''
    def is_address(self, input_str) -> bool:
        # Define the regular expressions for different crypto address formats
        crypto_patterns = [
            r"^0x[a-fA-F0-9]+$",  # Ethereum address format
            r"^0X[a-fA-F0-9]+$",  # Ethereum address format with capitalization support
            r"^IBC[a-zA-Z0-9]+$"  # IBC address format (example)
            # Add more patterns for other crypto address formats if needed
        ]

        for pattern in crypto_patterns:
            if re.match(pattern, input_str):
                return True

        return False
    
    '''-----------------------------------'''
    def coin_in_file(self, search_term: str, search_col: str) -> bool:
        """
        Will return a boolean dependent on the state if the search_term is found in the search_col.
        """

        # Read the csv file.
        csv_file = pd.read_csv(coin_id_path)

        matching_row = csv_file[csv_file[search_col] == search_term.lower()]

        if matching_row.empty:
            return False
        else:
            return True


    '''----------------------------------- CSV File Functions -----------------------------------'''
    '''-----------------------------------'''
    def add_coin_to_csv(self, ticker: str, name: str) -> None:
        '''
        Takes the ticker and name of coin and appends it to the csv file. 
        Ex: {"BTC": "bitcoin"}'''

        try:
            with open(self.csv_file, "a") as file:
                writer = csv.writer(file)
                writer.writerow([ticker, name])
        except Exception as e:
            print(f"[Csv Error] {e}")
    '''-----------------------------------'''
    def ticker_list_handling(self, ticker_list: list) -> None:
        '''
        Takes a list of tickers such as ["BTC", "ETH", "LTC"], checks if they exist in the csv file.
        If they do not, it will make an api call for each ticker to retrieve the name, then append it to the csv.
        '''
        for ticker in ticker_list:
            coin_exist = self.does_coin_exist(ticker=ticker)
            # If the coin has been found, do not append it again.  
            if coin_exist:
                pass
            elif not coin_exist:
                coin_name = self.get_coin_name(ticker=ticker)
                self.add_coin_to_csv(ticker=ticker, name=coin_name)


    '''-----------------------------------'''
    def get_address_by_ticker(self, ticker: str, network: str):
        """
        Takes the ticker as a parameter and searches the csv file.
        Will return the address in the column of the network desired.
        """
        # Read csv data.
        csv_file = pd.read_csv(coin_id_path)

        # Lowercase the network to match keys in dictionary.
        network = network.lower()

        # Get the column.
        col_name = self.network_to_column_mapping[network]

        # Get the ticker index. 
        ticker_index = csv_file[csv_file["ticker"] == ticker.lower()].index.values[0]
        print(f'Tinker: {ticker_index}')
        address = csv_file.loc[ticker_index, col_name.upper()]
        print(f"Address: {address}")
        return address



    '''-----------------------------------'''
    
    def convert_addresses_to_uppercase(self):

        with open(coin_id_path, 'r') as csv_file:
            reader = csv.reader(csv_file)
            rows = list(reader)
            
        for row in rows:
            for i in range(3, len(row)):  # Start from the 4th column containing addresses
                if row[i]:
                    row[i] = row[i].upper()
                    
        with open(coin_id_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(rows)
    '''-----------------------------------'''
    def sort_file_by_ticker(self):
        """
        Read the data from the csv file and re-write it in alphabetical order by the ticker column.
        """
        # Read csv data. Set index_col to the first column. In this case "ticker".
        data = pd.read_csv(coin_id_path)
        # Sort the dataframe by the ticker column. 
        sorted_data = data.sort_values(by="ticker", ascending=True)


        # Write the sorted data back to the same csv.
        sorted_data.to_csv(coin_id_path, index=False)

        self.remove_unnamed_columns()

    '''-----------------------------------'''
    def add_new_column(self, col_name: str, capitalize: bool = True) -> str:
        """
        Adds a new column to the csv file. 
        """
        # Read the csv data.
        if capitalize:
            col_name = col_name.upper()
        data = pd.read_csv(coin_id_path)
        data[col_name] = [None] * len(data)
        data.to_csv(coin_id_path, index=False)
    '''-----------------------------------'''
    def add_new_row(self, ticker: str):
        """
        Adds a new row to the csv file. Then the function will fetch the contract addresses on all available networks and add the data to the row. 
        Then the function will sort the csv so the new coin is in the right location.
        """
        # Format ticker to lowercase.
        ticker = ticker.lower()

        # Check if the ticker is already in the csv file. 
        if not self.coin_in_file(search_term=ticker, search_col="ticker"):


            # Read the csv data 
            csv_data = pd.read_csv(coin_id_path)
            # Dictionary to hold data for new row.
            new_row = {"ticker": ticker}
            # Iterate through the columns.
            for column in csv_data.columns:
                # If not the "ticker" column, set value to NaN. 
                if column != "ticker":
                    new_row[column] = np.nan

            # Get the last index of the dataframe with the csv data. 
            last_csv_index = csv_data.index[-1]


            new_row_df = pd.DataFrame(new_row, index=[last_csv_index])

            # Concatenate the original dataframe with the new dataframe.
            csv_data = pd.concat([csv_data.iloc[:last_csv_index], new_row_df, csv_data.iloc[last_csv_index:]], ignore_index=True)

            # Write to csv.
            csv_data.to_csv(coin_id_path, index=False)

            # Get the contract data for the coin. 
            contract_data = self.get_address_from_cmc(ticker)

            # Write all the contracts to the csv file. 
            self.dump_contracts_to_csv(ticker, contracts=contract_data)
            self.sort_file_by_ticker() 
        else:
            print(f"Coin already in file")

    '''-----------------------------------'''
    def insert_coin_address(self, ticker: str, col_name: str, address: str) -> None:
        """
        Takes the ticker to find the row needed. 
        Takes the name of the column to find the column desired within that row. 
        Insert the address at the row, column coordinates. 
        """
        # Read data from csv file. 
        data = pd.read_csv(coin_id_path)

        # Format ticker to be lowercase, the column name to be uppercase, and the address to uppercase. 
        # This is because this is the format the csv file is in. 
        ticker = ticker.lower()
        col_name = col_name.upper()
        address = address.upper()

        # Set the value of the address for the coin on the desired network. 
        data.loc[data["ticker"] == ticker, col_name] = address

        # Write the new data to the csv file. 
        data.to_csv(coin_id_path, index=False)
        
    '''-----------------------------------'''
    def remove_unnamed_columns(self) -> None:
        """
        Will read data from the csv file and remove and columns that start with "Unnamed".
        With other formatting functions sometimes blank columns are left over. 
        So this function cleans them up. 
        """
        # Read the data from the csv file.
        data = pd.read_csv(coin_id_path)

        unnamed_cols = [col for col in data.columns if col.startswith("Unnamed")]

        # Drop the unnamed columns.
        cleaned_data = data.drop(columns=unnamed_cols)

        # Write the cleaned data back to the csv.
        cleaned_data.to_csv(coin_id_path, index=False)

    '''-----------------------------------'''
    def get_address_from_cmc(self, ticker: str, show_untracked: bool = False) -> dict:
        # Format the ticker to lowercase.
        ticker = ticker.lower()

        # Dictionary to hold addresses on different networks. 
        tracked_platforms = {}
        untracked_platforms = {}


        base_url = "https://pro-api.coinmarketcap.com/v1"
        end_point = f"/cryptocurrency/info?symbol={ticker}"
        url = base_url + end_point

        response = self.cmc.get(url)

       

        
        if response.status_code == 200:
            data = response.json()

            try:
                coin_data = data["data"][ticker.upper()]["contract_address"]#["platform"].keys()
            

                # Parse the data. 
                for i in coin_data:
                    contract_address = i["contract_address"].upper()
                    platform_name = i["platform"]["name"].lower()

                    #Try to get the column name based on the platform.
                    try:
                        col_name = self.network_to_column_mapping[platform_name]
                        tracked_platforms[col_name] = contract_address
                    except KeyError:
                        untracked_platforms[platform_name] = contract_address

                if show_untracked:
                    print(f"Untracked: {untracked_platforms.keys()}")


                return tracked_platforms
            except KeyError:
                return {}
        # Too many requests
        elif response.status_code == 429:
            rerun = True
            request_delay = 60
            while rerun:
                time.sleep(request_delay)

                response = self.cmc.get(url)
                if response.status_code == 200:
                    data = response.json()

                    try:
                        coin_data = data["data"][ticker.upper()]["contract_address"]#["platform"].keys()
                    

                        # Parse the data. 
                        for i in coin_data:
                            contract_address = i["contract_address"].upper()
                            platform_name = i["platform"]["name"].lower()

                            #Try to get the column name based on the platform.
                            try:
                                col_name = self.network_to_column_mapping[platform_name]
                                tracked_platforms[col_name] = contract_address
                            except KeyError:
                                untracked_platforms[platform_name] = contract_address

                        if show_untracked:
                            print(f"Untracked: {untracked_platforms.keys()}")

                        rerun = False
                        return tracked_platforms
                    except KeyError:
                        rerun = False
                        return {}
        elif response.status_code == 400:
            return {}
        

    '''-----------------------------------'''
    def dump_contracts_to_csv(self, ticker: str, contracts: dict):
        """
        ticker: Which ticker to write the contracts to. 
        contracts: Dictionary with the contracts and which network column to insert them to. 
        Take all the contracts from CoinMarketCap and put them in a csv file. 
        """
        # Read the csv data.
        csv_data = pd.read_csv(coin_id_path)

        ticker_index = csv_data[csv_data["ticker"] == ticker.lower()].index[0]

        for key, val in contracts.items():
            try:
                existing_data = csv_data.iloc[ticker_index][key]

                # If there is a NaN value, write the data. 
                if pd.isna(existing_data):
                    csv_data.loc[ticker_index, key] = val.upper()
            # If the column does not exist, create an empty column in equal width to the other columns.
            except KeyError:
                csv_data[key] = [None] * len(csv_data)
                csv_data.loc[ticker_index, key] = val.upper()

        csv_data.to_csv(coin_id_path, index=False)
    '''-----------------------------------'''
    def write_cg_ids_to_csv(self):
        """
        Read the data from the csv_file and search the "cg_name" column. 
        Get the coingecko id for each ticker with a nan value.
        """
        # Read the csv file.
        csv_file = pd.read_csv(coin_id_path)

        # Rows with no id.
        no_ids = csv_file[pd.isna(csv_file["cg_name"])]

        # If there are rows with empty ids.
        if not no_ids.empty:
            for index, row in no_ids.iterrows():
                coin_id = self.get_id_by_ticker(row["ticker"])
                csv_file.loc[index, "cg_name"] = coin_id

            # Write the new data.
            csv_file.to_csv(coin_id_path, index=False)


    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''