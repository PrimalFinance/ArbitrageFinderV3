

# Import date & time.
import time
import datetime as dt

from Oracle.coin_oracle import CoinOracle





class Route:
    def __init__(self, base_ticker: str = "", target_ticker: str = "") -> None:
        self.base_ticker = base_ticker
        self.target_ticker = target_ticker
        self.route_path = {}

    '''-----------------------------------'''
    def set_route(self, x_exchange: dict, y_exchange: dict, percentage_change: float):
        """
        x_exchange: The main exchange used for base comparison.
        y_exchange: The second exchange to compare the x_exchange with. 
        percentage_change: The % difference between the prices of the two exchanges. 
                           This should be calculated before calling this function.
        
        Ex: x_exchange = Coinbase

        Coinbase -> Kraken
        Coinbase -> Kucoin
        Coinbase -> Bitmart

        x_exchange will be used as the base for the comparison. 
        """
        # Create a temporary oracle object to retrieve further information. 
        oracle = CoinOracle()

        
        
        x_base_ticker = x_exchange["base_ticker"].upper()
        x_target_ticker = x_exchange["target_ticker"].upper()
        y_base_ticker = y_exchange["base_ticker"].upper()
        y_target_ticker = y_exchange["target_ticker"].upper()

        x_base_address, x_target_address, y_base_address, y_target_address = oracle.is_address(x_base_ticker), oracle.is_address(x_target_ticker), oracle.is_address(y_base_ticker), oracle.is_address(y_target_ticker)

        # If the base ticker is an address rather than in ticker format. 
        if x_base_address:
            x_base_ticker = oracle.get_ticker_by_address(x_base_ticker)
            if x_base_ticker == None:
                print(f"XBASE: {x_exchange['base_ticker']}")
            x_exchange["base_ticker"] = x_base_ticker
        if x_target_address:
            x_target_ticker = oracle.get_ticker_by_address(x_target_ticker)
            if x_target_ticker == None:
                print(f"XTARGET: {x_exchange['target_ticker']}")
            x_exchange["target_ticker"] = x_target_ticker
        if y_base_address:
            y_base_ticker = oracle.get_ticker_by_address(y_base_ticker)
            if y_base_ticker == None:
                print(f"YBASE: {y_exchange['base_ticker']}")
            y_exchange["base_ticker"] = y_base_ticker

        if y_target_address:
            y_target_ticker = oracle.get_ticker_by_address(y_target_ticker)
            if y_target_ticker == None:
                print(f"YTARGET: {y_exchange['target_ticker']}")
            y_exchange["target_ticker"] = y_target_ticker
        
        # Put data into route path. 
        self.route_path = {
            "base": x_exchange,
            "target": y_exchange,
            "perc_diff": percentage_change
        }

    '''-----------------------------------'''
    def get_route(self) -> dict:
        return self.route_path
    '''-----------------------------------'''
    def __str__(self) -> str:
        """
        Custom __str__ method for printing out routes. 
        """
        return f"""-------------------------------
Route: {self.route_path['base']['exchange_name']} -> {self.route_path['target']['exchange_name']}
Percent Change: {self.route_path["perc_diff"]}%
Base Pair: {self.route_path["base"]["base_ticker"]}/{self.route_path["base"]["target_ticker"]}
Target Pair: {self.route_path["target"]["base_ticker"]}/{self.route_path["target"]["target_ticker"]}
Base Price: ${self.route_path['base']['price']}
Target Price: ${self.route_path['target']['price']}
-------------------------------
"""
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''
    '''-----------------------------------'''









class ArbitrageFinder:
    def __init__(self, arb_threshold: float = 0.0, ignore_threshold: bool = False, exclude_exchanges: bool = True) -> None:
        
        self.stable_coins = ["USD", "USDT", "USDC", "DAI"]
        self.oracle = CoinOracle()
        # The minimum % the arbitrage route must meet to be included.
        self.arb_threshold = arb_threshold
        self.ignore_threshold = ignore_threshold
        # Boolean to track if the routes have been sorted. By default it is set to False since the data is not sorted.
        self.routes_sorted = False
        # List to hold coin routes.
        self.coin_routes = []

        self.all_exchanges = {
            "CEX": [
                "Bitmart", "Bitrue", "Coinbase Exchange", "Kraken", "MEXC"
            ],
            "DEX": [
                "Curve (Ethereum)", "Curve (Arbitrum)", "Curve (Optimism)",
                "Kyberswap Elastic (Arbitrum)", "Kyberswap Elastic (Linea)", "Kyberswap Elastic (Optimism)", "Kyberswap Elastic (Polygon)", # Kyberswap Elastic
                "Pancakeswap V3 (BSC)", "Pancakeswap V3 (Ethereum)", "Pancakeswap V3 (zkSync)", # Pancakeswap
                "RCP Swap", # Reddit Community Point Swap
                "Sushiswap", "Sushiswap (Arbitrum Nova)", "Sushiswap (Arbitrum One)", "Sushiswap (BSC)", "Sushiswap V3 (Arbitrum)", "Sushiswap V3 (Base)", "Sushiswap V3 (Arbitrum Nova)", # Sushiswap
                "Uniswap V2 (Ethereum)", "Uniswap V3 (Base)","Uniswap V3 (BSC)", "Uniswap V3 (Ethereum)", "Uniswap V3 (Optimism)", "Uniswap V3 (Polygon)", # Uniswap
            ]
        }

        # Make a copy of all_exchanges.
        self.valid_exchanges = self.all_exchanges

        # List of exchanges to exclude.
        excluded_exchanges = {
            "CEX": [],
            "DEX": [
                "Pancakeswap V3 (Ethereum)",               # Pancakeswap
                "Uniswap V2 (Ethereum)","Uniswap V3 (Ethereum)", # Uniswap
                ]
        }

        # Boolean to track if exchanges will be excluded.
        self.exclude_exchanges = exclude_exchanges


        if excluded_exchanges != {}:
            if self.exclude_exchanges:
                for key, values in excluded_exchanges.items():
                    if key in self.valid_exchanges:
                        for value in values:
                            if value in self.valid_exchanges[key]:
                                self.valid_exchanges[key].remove(value)





    '''-----------------------------------'''
    def find_arbitrage_routes(self, coin_name: str, ticker: bool = False) -> None:
        """
        coin_name: The name of the coin to search.
        ticker: A boolean to determine if the coin name needs to be fetched from the csv file. 
                If this is true, a ticker will be passed in "coin_name" instead, and the name 
                will be retrieved from the csv file within this function. 
        """

        if ticker:
            coin_name = self.oracle.get_name_by_ticker(ticker=coin_name)


        print(f"Coinname: {coin_name}")
        # Get the time the data was retrieved. 
        datetime_string = str(dt.datetime.now().isoformat())
        date_time_parts = datetime_string.split("T")
        date_without_fraction = date_time_parts[0] + " " + date_time_parts[1].split(".")[0]
        time_retrieved = date_without_fraction

        # Get the prices from the coin oracle
        exchange_prices = self.oracle.get_cg_exchange_prices(coin_name)

        try:
            for i in range(len(exchange_prices)):
                # Get data for the "outer exchange" that we are comparing.
                outter_exchange = exchange_prices[i]
                # Check if the outer exchange is in the valid exchange list.
                if outter_exchange["market"]["name"] in self.valid_exchanges["CEX"] or outter_exchange["market"]["name"] in self.valid_exchanges["DEX"]: 
                    for j in range(len(exchange_prices)):
                        # Get data for  "inner exchange" to compare against. 
                        inner_exchange = exchange_prices[j]
                        # Check if the inner exchange is in the valid exchange list. 
                        if inner_exchange["market"]["name"] in self.valid_exchanges["CEX"] or inner_exchange["market"]["name"] in self.valid_exchanges["DEX"]:
                            if i == j:
                                pass
                            else:
                                # Logic to fix pairs that do not include stablecoins. 
                                if outter_exchange["target"] not in self.stable_coins:
                                    x_price = outter_exchange["converted_last"]["usd"]
                                else:
                                    x_price = outter_exchange["last"]
                                if inner_exchange["target"] not in self.stable_coins:
                                    y_price = inner_exchange["converted_last"]["usd"]
                                else:
                                    y_price = inner_exchange["last"]

                                # Calculate the % change between the 2 classes. 
                                perc_change = float("{:.3f}".format(((y_price - x_price)/abs(x_price)) * 100))

                                # Check if threshold is to be ignored. 
                                if self.ignore_threshold:
                                    x_exchange = {
                                        "exchange_name": outter_exchange["market"]["name"],
                                        "base_ticker": outter_exchange["base"],
                                        "target_ticker": outter_exchange["target"],
                                        "price": x_price,
                                        "volume": outter_exchange["converted_volume"]["usd"],
                                        "trust_score": outter_exchange["trust_score"],
                                        "is_anomaly": outter_exchange["is_anomaly"],
                                        "is_stale": outter_exchange["is_stale"],
                                    }
                                    # Create object for the "inner_exchange".
                                    y_exchange = {
                                        "exchange_name": inner_exchange["market"]["name"],
                                        "base_ticker": inner_exchange["base"],
                                        "target_ticker": inner_exchange["target"],
                                        "price": y_price,
                                        "volume": inner_exchange["converted_volume"]["usd"],
                                        "trust_score": inner_exchange["trust_score"],
                                        "is_anomaly": inner_exchange["is_anomaly"],
                                        "is_stale": inner_exchange["is_stale"],
                                    }
                                    
                                    route = Route()
                                    route.set_route(x_exchange=x_exchange, y_exchange=y_exchange, percentage_change=perc_change)

                                    self.coin_routes.append(route)
                                # If threshold is *not* to be ignored.
                                elif not self.ignore_threshold:
                                    # Check if the percentage change is above the "arbitrage threshold".
                                    if perc_change >= self.arb_threshold:

                                        # Create object for the "outter_exchange".
                                        x_exchange = {
                                            "exchange_name": outter_exchange["market"]["name"],
                                            "base_ticker": outter_exchange["base"],
                                            "target_ticker": outter_exchange["target"],
                                            "price": x_price,
                                            "volume": outter_exchange["converted_volume"]["usd"],
                                            "trust_score": outter_exchange["trust_score"],
                                            "is_anomaly": outter_exchange["is_anomaly"],
                                            "is_stale": outter_exchange["is_stale"],
                                        }
                                        # Create object for the "inner_exchange".
                                        y_exchange = {
                                            "exchange_name": inner_exchange["market"]["name"],
                                            "base_ticker": inner_exchange["base"],
                                            "target_ticker": inner_exchange["target"],
                                            "price": y_price,
                                            "volume": inner_exchange["converted_volume"]["usd"],
                                            "trust_score": inner_exchange["trust_score"],
                                            "is_anomaly": inner_exchange["is_anomaly"],
                                            "is_stale": inner_exchange["is_stale"],
                                        }
                                        
                                        route = Route()
                                        route.set_route(x_exchange=x_exchange, y_exchange=y_exchange, percentage_change=perc_change)

                                        self.coin_routes.append(route)
            # Once all the routes are collected, sort them. 
            self.sort_routes()
        except TypeError as e:
            print(f"CoinERROR!!!!!!!: {coin_name}")



    '''-----------------------------------'''
    def sort_routes(self) -> None:
        self.coin_routes = sorted(self.coin_routes, key=lambda route: route.route_path["perc_diff"], reverse=True)
        self.routes_sorted = True
    '''-----------------------------------'''
    def display_routes(self, routes_displayed: int = 0) -> None:
        if not self.routes_sorted:
            self.sort_routes()

        # If the parameter is left at the default setting, display all the routes in the coin list. 
        if routes_displayed == 0:
            try:
                for i in self.coin_routes:
                    print(f"{i}")
            except IndexError:
                print(f"[No Routes]")
        else:
            try:
                for i in range(routes_displayed):
                    print(f"{self.coin_routes[i]}")
            except IndexError:
                print(f"[No Routes]")
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