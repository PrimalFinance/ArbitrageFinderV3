

# CSV related imports
import csv

# Regular expression imports 
import re

# Requests imports
import requests

import json

# Pandas related imports
import pandas as pd



coin_id_path = "D:\\Coding\\VisualStudioCode\\Projects\\Python\\ArbitrageFinderV3\\Oracle\\coins.csv"

class CoinStorage:
    def __init__(self) -> None:
        self.csv_file = "D:\\Coding\\VisualStudioCode\\Projects\\Python\\ArbitrageFinderV3\\Oracle\\coins.csv"
        self.coin_data = None
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
            print(f"Coin: {coin}")
            try:
                if coin['symbol'] == ticker.lower():
                    name = coin['name']
                    return name
            except TypeError:
                print(f"Tag: {coin}")
    '''-----------------------------------'''
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
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''